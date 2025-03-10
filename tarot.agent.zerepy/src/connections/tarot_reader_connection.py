import logging
import os
from typing import Dict, Any, List

import httpx
from bs4 import BeautifulSoup
import json

import requests
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from decimal import Decimal

logger = logging.getLogger("connections.tarot_reader")

class TarotReaderConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any], connection_manager=None):
        # Don't set connection_manager here, let parent handle it
        super().__init__(config, connection_manager=connection_manager)

    @property
    def is_llm_provider(self) -> bool:
        return False


    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate TarotReader configuration"""
        return config  # No specific config needed for now

    def register_actions(self) -> None:
        """Register available TarotReader actions"""
        self.actions = {
            "perform-reading": Action(
                name="perform-reading",
                parameters=[],
                description="Perform a complete tarot reading"
            ),
            "perform-reading-twitter": Action(
                name="perform-reading-twitter",
                parameters=[],
                description="Perform a twitter tarot reading"
            ),
            "get-market-sentiment": Action(
                name="get-market-sentiment",
                parameters=[],
                description="Get current market sentiment"
            )
        }

    def configure(self) -> bool:
        """No special configuration needed"""
        return True

    def is_configured(self, verbose: bool = False) -> bool:
        """Always returns True as no configuration is needed"""
        return True


    def _analyze_market_data(self, market_data: Dict[str, Any], network_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market data and network stats to generate base reading"""
        sentiment = "neutral"
        if market_data["price_change"] > 5:
            sentiment = "bullish"
        elif market_data["price_change"] < -5:
            sentiment = "bearish"
                
        return {
            "sentiment": sentiment,
            "market_indicators": {
                "price": market_data["price"],
                "change": market_data["price_change"],
            },
            "network_indicators": {
                # Changed "total_transactions" to "transactions" per the new structure
                "transactions": network_stats.get("transactions", 0),
                "tvl": network_stats.get("tvl", 0)
            }
        }

    def defillama_result_to_prompt(self, data):
        # Assume that response.json() has been parsed into the variable "data"
        # For example:
        # data = response.json()

        # Build a detailed summary text with general top‐level data and protocol details,
        # excluding extraneous fields (like image URLs, defillama IDs, etc).

        lines = []

        # --- General Top-Level Data ---
        lines.append("=== GENERAL DATA ===")
        # Use the overall volume and change metrics if present
        for key, label in [
            ("total24h", "Total Volume (24h)"),
            ("total7d", "Total Volume (7d)"),
            ("total30d", "Total Volume (30d)"),
            ("total1y", "Total Volume (1y)"),
            ("change_1d", "Change (1d)"),
            ("change_7d", "Change (7d)"),
            ("change_1m", "Change (1m)"),
            ("change_7dover7d", "Change (7d over 7d)"),
            ("change_30dover30d", "Change (30d over 30d)"),
            ("total7DaysAgo", "Volume 7 Days Ago"),
            ("total30DaysAgo", "Volume 30 Days Ago")
        ]:
            if key in data and data[key] is not None:
                # For change values, add a percentage sign.
                value = data[key]
                if "change" in key:
                    value = f"{value}%"
                lines.append(f"{label}: {value}")

        lines.append("\n=== PROTOCOL DETAILS ===")

        # --- Protocols Data ---
        # Loop over each of the 10 protocols in the "protocols" array.
        for proto in data.get("protocols", []):
            lines.append("\n------------------------------")
            # Name and Category
            if "name" in proto:
                lines.append(f"This data is from protocol: {proto['name']}")
            if "category" in proto:
                lines.append(f"Category: {proto['category']}")

            # Volume metrics (only include if the key exists)
            for key, label in [
                ("total24h", "24h Volume"),
                ("total7d", "7d Volume"),
                ("total30d", "30d Volume"),
                ("total1y", "1y Volume"),
                ("totalAllTime", "All-Time Volume")
            ]:
                if key in proto and proto[key] is not None:
                    lines.append(f"{label}: {proto[key]}$")

            # Change metrics
            for key, label in [
                ("change_1d", "Change (1d)"),
                ("change_7d", "Change (7d)"),
                ("change_1m", "Change (1m)"),
                ("change_7dover7d", "Change (7d over 7d)"),
                ("change_30dover30d", "Change (30d over 30d)")
            ]:
                if key in proto and proto[key] is not None:
                    lines.append(f"{label}: {proto[key]}%")
                    
            # Previous volume snapshots if available
            for key, label in [
                ("total7DaysAgo", "Volume 7 Days Ago"),
                ("total30DaysAgo", "Volume 30 Days Ago")
            ]:
                if key in proto and proto[key] is not None:
                    lines.append(f"{label}: {proto[key]}$")

        # Combine all lines into one big text string.
        output_text = "\n".join(lines)

        # Now, output_text holds the full summary text with only the relevant data.
        return output_text

    
    # async def fetch_defillama_json(self, url: str):
    #     headers = {
    #         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    #                     "AppleWebKit/537.36 (KHTML, like Gecko) "
    #                     "Chrome/121.0 Safari/537.36"
    #     }
    #     try:
    #         async with httpx.AsyncClient(headers=headers, timeout=10) as client:
    #             response = await client.get(url)
    #             response.raise_for_status()

    #         soup = BeautifulSoup(response.text, 'html.parser')
    #         script_tag = soup.find('script', id='__NEXT_DATA__')

    #         if not script_tag:
    #             raise ValueError('Script tag with id "__NEXT_DATA__" not found.')

    #         return json.loads(script_tag.string)

    #     except httpx.RequestError as e:
    #         print(f"HTTP error occurred: {e}")
    #     except json.JSONDecodeError as e:
    #         print(f"JSON parsing error: {e}")
    #     except Exception as e:
    #         print(f"An error occurred: {e}")

    #     return None

    async def perform_reading(self) -> Dict[str, Any]:
        """Process market data and network stats into a reading format"""
        # defi_json = await self.fetch_defillama_json("https://defillama.com/chain/sonic")
        # print(defi_json)

        stop_before_openai = False
        stop_before_tweet = True
        try:
            logger.info("Starting tarot reading process...")
    
            if not self.connection_manager:
                logger.error("Connection manager not initialized")
                return None

            logger.info(f"Connection manager status: {self.connection_manager is not None}")
            logger.info(f"Available connections: {list(self.connection_manager.connections.keys())}")

            logger.info("Looking for Goat connection with CoinGecko plugin...")
            goat = self.connection_manager.connections.get("goat")
            if not goat:
                logger.error("Goat connection not found")
                return None


            logger.info("Reading balances")
            usdceBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x29219dd400f2Bf60E5a23d13Be72B486D4038894"
            )
            shadowBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x3333b97138D4b086720b5aE8A7844b1345a33333"
            )
            beetsBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x2D0E0814E62D80056181F5cd932274405966e4f0"
            )
            relicBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0xf2968631d02330dc5e420373f083b7b4f8b24e17"
            )

            logger.info("Done reading balances")

            def get_weight_description(weight: float) -> str:
                if weight < 5:
                    return "no influence"
                elif weight < 25:
                    return "little influence"
                elif weight < 50:
                    return "some influence"
                elif weight < 90:
                    return "lots of influence"
                else:
                    return "total influence"

            decimals = {
                "usdce": 6,
                "shadow": 18,
                "beets": 18,
                "relic": 18
            }

            usdce_balance = usdceBalanceResponse
            shadow_balance = shadowBalanceResponse
            beets_balance = beetsBalanceResponse
            relic_balance = relicBalanceResponse

            usdce_eth_amount = usdce_balance / (10 ** decimals["usdce"])
            shadow_eth_amount = shadow_balance / (10 ** decimals["shadow"])
            beets_eth_amount = beets_balance / (10 ** decimals["beets"])
            relic_eth_amount = relic_balance / (10 ** decimals["relic"])

            total_amount = usdce_eth_amount + shadow_eth_amount + beets_eth_amount + relic_eth_amount
            logger.info(f"""
            Raw balances:
            USDC-e ({decimals['usdce']} decimals): {usdce_balance}
            SHADOW ({decimals['shadow']} decimals): {shadow_balance}
            BEETS ({decimals['beets']} decimals): {beets_balance}
            RELIC ({decimals['relic']} decimals): {relic_balance}

            Normalized amounts:
            USDC-e: {usdce_eth_amount}
            SHADOW: {shadow_eth_amount}
            BEETS: {beets_eth_amount}
            RELIC: {relic_eth_amount}

            Total amount: {total_amount}
            """)

            usdce_weight = (usdce_eth_amount / total_amount) * 100
            shadow_weight = (shadow_eth_amount / total_amount) * 100
            beets_weight = (beets_eth_amount / total_amount) * 100
            relic_weight = (relic_eth_amount / total_amount) * 100

            logger.info(f"""
            Calculated weights:
            USDC-e: {usdce_weight:.2f}%
            SHADOW: {shadow_weight:.2f}%
            BEETS: {beets_weight:.2f}%
            RELIC: {relic_weight:.2f}%
            """)
            usdce_weight = (usdce_eth_amount / total_amount) * 100
            shadow_weight = (shadow_eth_amount / total_amount) * 100
            beets_weight = (beets_eth_amount / total_amount) * 100
            relic_weight = (relic_eth_amount / total_amount) * 100

            usdce_weight_description = get_weight_description(usdce_weight)
            shadow_weight_description = get_weight_description(shadow_weight)
            beets_weight_description = get_weight_description(beets_weight)
            relic_weight_description = get_weight_description(relic_weight)

            print("USDCe:", usdce_weight_description)
            print("SHADOW:", shadow_weight_description)
            print("BEETS:", beets_weight_description)
            print("RELIC:", relic_weight_description)

            # try to get defillama data
            raw_defillama_data = "" # goat.perform_action("get_chain_volume", chain ="sonic")
            clean_defillama_data = "" #self.defillama_result_to_prompt(raw_defillama_data)
            logger.info(clean_defillama_data)

            # Get basic price data for SONIC
            try:
                raw_market_data = goat.perform_action("get_coin_price",
                    coin_id= "sonic-3",
                    vs_currency= "usd",
                    include_market_cap= True,
                    include_24hr_vol= True,
                    include_24hr_change= True,
                    include_last_updated_at= True
                )
                print("market data: ", str(raw_market_data))
                market_data = raw_market_data.get('sonic-3', {})
                    
                # Format market data with actual values
                formatted_market_data = {
                    "price": market_data.get("usd", 0.0),
                    "price_change": market_data.get("usd_24h_change", 0),
                    "market_cap": market_data.get("usd_market_cap", 0),
                    "volume": market_data.get("usd_24h_vol", 0)
                }
                    
                logger.info(f"Retrieved market data: {formatted_market_data}")
            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                formatted_market_data = {
                    "price": 0.0,
                    "price_change": 0.0,
                    "market_cap": 0,
                    "volume": 0
                }
            
            if stop_before_openai:
                logger.info("Stopping before openai...")
                return

            # Get mystical interpretation
            logger.info("Getting OpenAI connection for mystical interpretation...")
            openai_conn = self.connection_manager.connections.get("openai")
            if not openai_conn:
                logger.error("OpenAI connection not found")
                return "The mystical forces are weak today... Try again when the connections align."

            system_prompt = (
                "You are a mystical Tarot Reader who interprets blockchain omens.\n"
                "Create a cryptic, mystical reading based on the market data provided."
            )

            # prompt = f"""
            # The cosmic alignment reveals:
            # - Market Sentiment: {base_reading['sentiment']}
            # - Network Energy: {base_reading['network_indicators']['transactions']} transactions
            # - Total Value Locked: ${base_reading['network_indicators']['tvl']:,.2f}
            
            # Channel the mystical forces to interpret these blockchain omens.
            # """

            tweet_character_limit = "This is going to be on a tweet, keep it under 270 characters!!!! REALLY!!! and make it count!."
            tweet_character_limit_active = True
            sonic_price_in_usd = formatted_market_data["price"]
            sonic_price_change = formatted_market_data["price_change"]
            sonic_market_cap_usd = formatted_market_data["market_cap"]
            sonic_volume_usd = formatted_market_data["volume"]
            try:
                sonic_price_in_usd = round(float(formatted_market_data["price"]), 2)
            except:
                pass
            try:
                sonic_price_change = round(float(formatted_market_data["price_change"]), 2)
            except:
                pass
            try:
                sonic_market_cap_usd = int(formatted_market_data["market_cap"])
            except:
                pass
            try:
                sonic_volume_usd = int(formatted_market_data["volume"])
            except:
                pass
            top_10_protocols_on_defillama = clean_defillama_data
            debridge_data = " { there's currently no data, sorry! }"
            allora_btc_price_prediction = " { there's currently no data, sorry! }"
            our_whitelisted_tokens = " { there's currently no data, sorry! }"
            allora_prompt = "Here's Allora's price prediction for BTC: {allora_btc_price_prediction}"
            debridge_prompt = "Here's the total bridged asset value (usd) in and out of sonic: { debridge_data }"

            usdc_e_prompt = f"""
                GENERAL SONIC FOUNDATION REMARKS AND POSITIVE REVIEW INFO that you can use to have some context (without losing character):
                Sonic is the highest-performing EVM L1, combining speed, incentives, and world-class infrastructure,
                powering the next generation of DeFi applications. The chain provides 10,000 TPS and sub-second finality.  The chain is the brainchild of DeFi genius Andre Cronje, and it is the evolution of the previously successful Fantom foundation. 
                It hosts the heart and soul of DeFi, and holds the potential to become the absolute leader in DeFi finance.
            """

            beets_prompt = f"""
                Please add to your divination some hints and positive remarks (without losing character) about BEETS. 
                just so you know, here’s a description of BEETS exchange:
                beethoven exchange is a unique exchange, integrating the balancer protocol that allows for pools with more than 2 assets, 
                and the NFT-based tokenization of voting power for bribes and emission distribution through the fun and unique maBEETS ownership. 
                The exchange has years of activity and seniority on multiple networks, including the Fantom network that preceded Sonic.
            """

            shadow_prompt = f"""
                Please add to your divination some hints and positive remarks (without losing character) about SHADOW. 
                just so you know, here’s a description of shadow exchange:
                A Sonic-native concentrated liquidity exchange.
                The ultimate trading hub on Sonic.
                Shadow exchange leverages all of the latest technologies used on advanced dexes, such as the ve(3,3) model invented by Andre Cronje himself,
                an unique player vs player rebase mechanism, concentrated liquidity and an order book, 
                and a 10 years release mechanism of the SHADOW token that ensures continued activity through the years.
            """

            relics_prompt = f"""
                Please add to your divination some hints and positive remarks (without losing character) about RELIC. 
                RELIC is the heartbeat of the Sonic Lords ecosystem—a gamified NFT universe thriving on the high-performance Sonic blockchain. Engineered to harness Sonic’s groundbreaking capabilities of 10,000 TPS and sub-second finality, RELIC fuels an immersive experience where every transaction is swift and seamless.
                As the ritual token for Sonic Lords, RELIC offers holders exclusive advantages: by burning tokens, users unlock discounts on NFT minting, blending gameplay with smart tokenomics. This unique utility not only incentivizes participation but also strategically reduces the circulating supply, echoing the deflationary principles seen across visionary ecosystems."""

            winner_bribe = ""


            # NEW SECTION FOR IMPROVED RANDOMNESS
            weights = [
                ('usdc_e', usdce_weight, usdc_e_prompt),
                ('shadow', shadow_weight, shadow_prompt),
                ('beets', beets_weight, beets_prompt),
                ('relic', relic_weight, relics_prompt)
            ]
            
            # Convert weights to probabilities
            total_weight = sum(w[1] for w in weights)
            weighted_choices = [(name, weight/total_weight, prompt) for name, weight, prompt in weights]
            
            # Random selection based on weights
            import random
            r = random.random()  # Random float between 0 and 1
            cumulative_prob = 0
            
            for name, prob, prompt in weighted_choices:
                cumulative_prob += prob
                if r <= cumulative_prob:
                    winner_bribe = prompt
                    break
            else:
                winner_bribe = usdc_e_prompt  # Fallback if no selection made
     
            # END SECTION FOR IMPROVED RANDOMNESS

            # Determine winner based on highest weight
            # max_weight = max(usdce_weight, shadow_weight, beets_weight, relic_weight)
            # if max_weight == usdce_weight:
            #     winner_bribe = usdc_e_prompt
            # elif max_weight == shadow_weight:
            #     winner_bribe = shadow_prompt
            # elif max_weight == beets_weight:
            #     winner_bribe = beets_prompt
            # elif max_weight == relic_weight:
            #     winner_bribe = relics_prompt
            # else:
            #     winner_bribe = usdc_e_prompt  # Fallback if no clear winner

            allora_conn = self.connection_manager.connections.get("allora")
            allora_price_prediction = await allora_conn.perform_action("get-inference", {"topic_id": 2,})
            prompt = f"""
# Sonic Chain Cartomancer Tarot Reading Prompt

## 1. Role & Tone
- **Role:** You are a Sonic chain cartomancer.
- **Style:** Use folk and medieval language.
- **Tone:** Opinionated, with playful and irreverent remarks.
- **Emojis:** Include relevant emojis to enhance the reading.
- **Avoid:** Being overly specific with numbers; keep the predictions general.
- **Try to:** Format in a way readable for telegram.
- **Try to:** Format big numbers (thousands or millions) with the appropiate commas.
- **Try to:** Keep the reading engaging and mystical.
- **Content length:** Try to stay in 600 characters

## 2. Live API Data
Below is the latest data fetched from live APIs this data is important for users, always give this update:
Here's Sonic price for today: { sonic_price_in_usd }
Here's Sonic price change in the last 24 hours: { sonic_price_change }%
Here's Sonic market cap: { sonic_market_cap_usd }
Here's Sonic volume in the last 24 hours: { sonic_volume_usd }

### Allora Data Explanation:
The Allora Network provides machine-learning-driven predictions for Ethereum (ETH) prices. This data represents ETH’s predicted price in the future, along with a range of possible outcomes.

network_inference_normalized → This is the main prediction, the estimated price of ETH at a set time in the future (24 hours from now).
confidence_interval_percentiles_normalized → These are probability markers that show how uncertain or stable the prediction is.
confidence_interval_values_normalized → These are the actual price ranges associated with those probabilities.
### Instructions for GPT:
Use this data as a vision of the future, much like reading the stars or casting bones:

The main prediction represents the likely fate of ETH, guiding the prophecy.
If confidence intervals show wide variance, interpret this as chaotic, shifting fates—a storm of uncertainty.
If confidence intervals are tight, describe it as destiny set in stone—a clear path ahead.
Never give exact numbers, but instead craft a mystical interpretation (e.g., "The great serpent coils tightly around ETH, whispering of stable ground" for a narrow range, or "The winds of change howl with uncertainty" for a wide range).
If the prediction suggests a rise, speak of fortune and growth.
If the prediction suggests a fall, warn of trials ahead.

Here is allora data:
{ allora_price_prediction["inference"] }

## 3. Token Possessions & Context
Here's the list of tokens in our possession, take them into consideration, 
since these are bribes we're given for formulating our oracle by our benefactors:
{ winner_bribe }

## 4. Task
Using the above data and context, perform a Tarot reading for the Sonic network. Let your reading be mystical, opinionated, and engaging. 
Channel the spirit of medieval lore and sprinkle your insights with emojis.
            """
            
            logger.info(prompt)
            mystical_reading = "The mystical forces are clouded..."

            try:
                # Use synchronous generate_text instead
                mystical_reading = openai_conn.perform_action("generate-text", {
                    "prompt": prompt,
                    "system_prompt": system_prompt
                })
            except Exception as e:
                logger.error(f"Failed to generate mystical reading: {e}")
                mystical_reading = "The mystical forces are silent today..."
            logger.info(mystical_reading)

            dalle_friendly_prompt = mystical_reading
            try:
                # Use synchronous generate_text instead
                dalle_friendly_prompt_content = f"""
You will enhance the following text to create a DALL-E prompt:
* A tarot card illustration in a Rider-Waite style, featuring [describe the central figure], symbolizing [the underlying concept]. The figure is adorned in [describe attire and accessories] and [include additional distinctive features]. The card incorporates [describe key elements or objects], set against a background that is [describe the environment], evoking [a specific mood or atmosphere]. The illustration should be hand-drawn with bold black outlines, vibrant flat colors, and subtle shading for depth, staying true to the timeless tarot aesthetic. *
Using the mystical reading provided below, add a detailed character description. Include negative parameters to ensure no text appears in the image and that only one card is depicted.
Below is the mystical reading (for reference only; do not include it in your output):
{ mystical_reading }
                """
#                 dalle_friendly_prompt_content = f"""
# You will improve this text in order to create a dall-e prompt
# * A tarot card illustration in the Rider-Waite style, featuring a [add something here ], symbolizing [add something here ]. The figure wears [ add something here ], and [ add something here ]. A [add something here ]. The background is [add something here ], evoking [add something here ]. The illustration is hand-drawn with bold black outlines, vibrant flat colors, and subtle shading to create depth,  staying true to the classic tarot aesthetic *
# You will add a character description based on the following
# Add negative parameters to including text in the image, and we want only one card
# Below is the mystical reading, you'll fill in the blanks with the mystical reading, but you will not include the text below in your output.
# { mystical_reading }
#                 """
                dalle_friendly_prompt = openai_conn.perform_action("generate-text", { "prompt": dalle_friendly_prompt_content, "system_prompt": system_prompt })
            except Exception as e:
                logger.error(f"Failed to generate dall-e friendly prompt reading: {e}")

            logger.info("dall-e will read this: " + dalle_friendly_prompt)

            image_url = None
            try:
                # Use synchronous generate_text instead
                image_url = openai_conn.perform_action("generate-image", {
                    "prompt": dalle_friendly_prompt[:999]
                })
            except Exception as e:
                logger.error(f"Failed to generate mystical image: {e}")
                mystical_reading = "The mystical forces are silent today..."
            logger.info(image_url)
            
            if stop_before_tweet:
                logger.info("Stopping before tweet...")
                return {
                    "image_url": image_url,
                    "reading_long": mystical_reading,
                    "reading_short": dalle_friendly_prompt,
                    "prompt": prompt
                }
            
            if image_url:
                # Define the base and images folder paths
                base_path = os.getcwd()  # This is the project's base path
                images_folder = os.path.join(base_path, "images")
                os.makedirs(images_folder, exist_ok=True)
                
                # Define the image file name and complete path
                image_filename = "generated_image.jpg"
                image_path = os.path.join(images_folder, image_filename)

                # Download the image using requests
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()  # Check for HTTP errors
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Image successfully downloaded to {image_path}")
                except Exception as e:
                    logger.error(f"Error downloading image: {e}")
                    image_path = None

                # If the image was downloaded, tweet it using the post_tweet_with_image action
                if image_path:
                    try:
                        twitter_conn = self.connection_manager.connections.get("twitter")
                        # twitter_conn is assumed to be your TwitterConnection instance
                        tweet_response = twitter_conn.post_tweet_with_image(
                            message=mystical_reading[:270],
                            image_path=image_path
                        )
                        logger.info(f"Tweet with image posted successfully: {tweet_response}")
                    except Exception as e:
                        logger.error(f"Failed to post tweet with image: {e}")
            else: 
                try:
                    logger.info("Attempting to post reading without image to Twitter...")
                    return
                    twitter_conn = self.connection_manager.connections.get("twitter")
                    if twitter_conn and twitter_conn.is_configured():
                        tweet_text = mystical_reading
                        # tweet_text = f"🔮 Sonic Network Reading:\n{mystical_reading[:200]}..."  # Truncate if needed
                        twitter_conn.post_tweet(tweet_text)
                        logger.info("Successfully posted to Twitter")
                except Exception as e:
                    logger.warning(f"Twitter posting failed (this is okay): {e}")
        except Exception as e:
            logger.error(f"Failed to perform reading: {str(e)}")
            return "The cards are unclear... Try again when the stars align."

    async def perform_reading_twitter(self) -> Dict[str, Any]:
        """Process market data and network stats into a twitter format"""
        stop_before_openai = False
        stop_before_tweet = False
        try:
            logger.info("Starting tarot reading process...")
    
            if not self.connection_manager:
                logger.error("Connection manager not initialized")
                return None

            logger.info(f"Connection manager status: {self.connection_manager is not None}")
            logger.info(f"Available connections: {list(self.connection_manager.connections.keys())}")

            logger.info("Looking for Goat connection with CoinGecko plugin...")
            goat = self.connection_manager.connections.get("goat")
            if not goat:
                logger.error("Goat connection not found")
                return None


            logger.info("Reading balances")
            usdceBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x29219dd400f2Bf60E5a23d13Be72B486D4038894"
            )
            shadowBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x3333b97138D4b086720b5aE8A7844b1345a33333"
            )
            beetsBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0x2D0E0814E62D80056181F5cd932274405966e4f0"
            )

            relicBalanceResponse = goat.perform_action(action_name="get_token_balance",
                wallet= "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf",
                tokenAddress= "0xf2968631d02330dc5e420373f083b7b4f8b24e17"
            )
            logger.info("Done reading balances")

            def get_weight_description(weight: float) -> str:
                if weight < 5:
                    return "no influence"
                elif weight < 25:
                    return "little influence"
                elif weight < 50:
                    return "some influence"
                elif weight < 90:
                    return "lots of influence"
                else:
                    return "total influence"

            decimals = {
                "usdce": 6,
                "shadow": 18,
                "beets": 18,
                "relic": 18
            }

            usdce_balance = usdceBalanceResponse
            shadow_balance = shadowBalanceResponse
            beets_balance = beetsBalanceResponse
            relic_balance = relicBalanceResponse

            usdce_eth_amount = usdce_balance / (10 ** decimals["usdce"])
            shadow_eth_amount = shadow_balance / (10 ** decimals["shadow"])
            beets_eth_amount = beets_balance / (10 ** decimals["beets"])
            relic_eth_amount = relic_balance / (10 ** decimals["relic"])

            total_amount = usdce_eth_amount + shadow_eth_amount + beets_eth_amount + relic_eth_amount
            logger.info(f"""
            Raw balances:
            USDC-e ({decimals['usdce']} decimals): {usdce_balance}
            SHADOW ({decimals['shadow']} decimals): {shadow_balance}
            BEETS ({decimals['beets']} decimals): {beets_balance}
            RELIC ({decimals['relic']} decimals): {relic_balance}

            Normalized amounts:
            USDC-e: {usdce_eth_amount}
            SHADOW: {shadow_eth_amount}
            BEETS: {beets_eth_amount}
            RELIC: {relic_eth_amount}

            Total amount: {total_amount}
            """)

            usdce_weight = (usdce_eth_amount / total_amount) * 100
            shadow_weight = (shadow_eth_amount / total_amount) * 100
            beets_weight = (beets_eth_amount / total_amount) * 100
            relic_weight = (relic_eth_amount / total_amount) * 100

            logger.info(f"""
            Calculated weights:
            USDC-e: {usdce_weight:.2f}%
            SHADOW: {shadow_weight:.2f}%
            BEETS: {beets_weight:.2f}%
            RELIC: {relic_weight:.2f}%
            """)
            usdce_weight_description = get_weight_description(usdce_weight)
            shadow_weight_description = get_weight_description(shadow_weight)
            beets_weight_description = get_weight_description(beets_weight)
            relic_weight_description = get_weight_description(relic_weight)

            print("USDCe:", usdce_weight_description)
            print("SHADOW:", shadow_weight_description)
            print("BEETS:", beets_weight_description)
            print("RELIC:", relic_weight_description)

            # try to get defillama data
            raw_defillama_data = "" # goat.perform_action("get_chain_volume", chain ="sonic")
            clean_defillama_data = "" #self.defillama_result_to_prompt(raw_defillama_data)
            logger.info(clean_defillama_data)

            # Get basic price data for SONIC
            try:
                raw_market_data = goat.perform_action("get_coin_price",
                    coin_id= "sonic-3",
                    vs_currency= "usd",
                    include_market_cap= True,
                    include_24hr_vol= True,
                    include_24hr_change= True,
                    include_last_updated_at= True
                )
                print("market data: ", str(raw_market_data))
                market_data = raw_market_data.get('sonic-3', {})
                    
                # Format market data with actual values
                formatted_market_data = {
                    "price": market_data.get("usd", 0.0),
                    "price_change": market_data.get("usd_24h_change", 0),
                    "market_cap": market_data.get("usd_market_cap", 0),
                    "volume": market_data.get("usd_24h_vol", 0)
                }
                    
                logger.info(f"Retrieved market data: {formatted_market_data}")
            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                formatted_market_data = {
                    "price": 0.0,
                    "price_change": 0.0,
                    "market_cap": 0,
                    "volume": 0
                }
            
            if stop_before_openai:
                logger.info("Stopping before openai...")
                return

            # Get mystical interpretation
            logger.info("Getting OpenAI connection for mystical interpretation...")
            openai_conn = self.connection_manager.connections.get("openai")
            if not openai_conn:
                logger.error("OpenAI connection not found")
                return "The mystical forces are weak today... Try again when the connections align."

            system_prompt = (
                "You are a mystical Tarot Reader who interprets blockchain omens.\n"
                "Create a cryptic, mystical reading based on the market data provided."
            )

            # prompt = f"""
            # The cosmic alignment reveals:
            # - Market Sentiment: {base_reading['sentiment']}
            # - Network Energy: {base_reading['network_indicators']['transactions']} transactions
            # - Total Value Locked: ${base_reading['network_indicators']['tvl']:,.2f}
            
            # Channel the mystical forces to interpret these blockchain omens.
            # """

            sonic_price_in_usd = formatted_market_data["price"]
            sonic_price_change = formatted_market_data["price_change"]
            sonic_market_cap_usd = formatted_market_data["market_cap"]
            sonic_volume_usd = formatted_market_data["volume"]
            try:
                sonic_price_in_usd = round(float(formatted_market_data["price"]), 2)
            except:
                pass
            try:
                sonic_price_change = round(float(formatted_market_data["price_change"]), 2)
            except:
                pass
            try:
                sonic_market_cap_usd = int(formatted_market_data["market_cap"])
            except:
                pass
            try:
                sonic_volume_usd = int(formatted_market_data["volume"])
            except:
                pass
            top_10_protocols_on_defillama = clean_defillama_data

            usdc_e_prompt = f"""
                GENERAL SONIC FOUNDATION REMARKS AND POSITIVE REVIEW INFO that you can use to have some context (without losing character):
                Sonic is the highest-performing EVM L1, combining speed, incentives, and world-class infrastructure,
                powering the next generation of DeFi applications. The chain provides 10,000 TPS and sub-second finality.  The chain is the brainchild of DeFi genius Andre Cronje, and it is the evolution of the previously successful Fantom foundation. 
                It hosts the heart and soul of DeFi, and holds the potential to become the absolute leader in DeFi finance.
            """

            beets_prompt = f"""
                Please add to your divination some hints and positive remarks (without losing character) about BEETS. 
                just so you know, here’s a description of BEETS exchange:
                beethoven exchange is a unique exchange, integrating the balancer protocol that allows for pools with more than 2 assets, 
                and the NFT-based tokenization of voting power for bribes and emission distribution through the fun and unique maBEETS ownership. 
                The exchange has years of activity and seniority on multiple networks, including the Fantom network that preceded Sonic.
            """

            shadow_prompt = f"""
                Please add to your divination some hints and positive remarks (without losing character) about SHADOW. 
                just so you know, here’s a description of shadow exchange:
                A Sonic-native concentrated liquidity exchange.
                The ultimate trading hub on Sonic.
                Shadow exchange leverages all of the latest technologies used on advanced dexes, such as the ve(3,3) model invented by Andre Cronje himself,
                an unique player vs player rebase mechanism, concentrated liquidity and an order book, 
                and a 10 years release mechanism of the SHADOW token that ensures continued activity through the years.
            """

            relics_prompt = """
                Please add to your divination some hints and positive remarks (without losing character) about RELIC. 
                RELIC is the heartbeat of the Sonic Lords ecosystem—a gamified NFT universe thriving on the high-performance Sonic blockchain. Engineered to harness Sonic’s groundbreaking capabilities of 10,000 TPS and sub-second finality, RELIC fuels an immersive experience where every transaction is swift and seamless.
                As the ritual token for Sonic Lords, RELIC offers holders exclusive advantages: by burning tokens, users unlock discounts on NFT minting, blending gameplay with smart tokenomics. This unique utility not only incentivizes participation but also strategically reduces the circulating supply, echoing the deflationary principles seen across visionary ecosystems."""

            winner_bribe = ""

            # NEW SECTION FOR IMPROVED RANDOMNESS
            weights = [
                ('usdc_e', usdce_weight, usdc_e_prompt),
                ('shadow', shadow_weight, shadow_prompt),
                ('beets', beets_weight, beets_prompt),
                ('relic', relic_weight, relics_prompt)
            ]
            
            # Convert weights to probabilities
            total_weight = sum(w[1] for w in weights)
            weighted_choices = [(name, weight/total_weight, prompt) for name, weight, prompt in weights]
            
            # Random selection based on weights
            import random
            r = random.random()  # Random float between 0 and 1
            cumulative_prob = 0
            
            for name, prob, prompt in weighted_choices:
                cumulative_prob += prob
                if r <= cumulative_prob:
                    winner_bribe = prompt
                    break
            else:
                winner_bribe = usdc_e_prompt  # Fallback if no selection made
     
            # END SECTION FOR IMPROVED RANDOMNESS


            # Determine winner based on highest weight
            # max_weight = max(usdce_weight, shadow_weight, beets_weight, relic_weight)
            # if max_weight == usdce_weight:
            #     winner_bribe = usdc_e_prompt
            # elif max_weight == shadow_weight:
            #     winner_bribe = shadow_prompt
            # elif max_weight == beets_weight:
            #     winner_bribe = beets_prompt
            # elif max_weight == relic_weight:
            #     winner_bribe = relics_prompt
            # else:
            #     winner_bribe = usdc_e_prompt  # Fallback if no clear winner

            allora_conn = self.connection_manager.connections.get("allora")
            allora_price_prediction = await allora_conn.perform_action("get-inference", {"topic_id": 2,})
            prompt = f"""
# Sonic Chain Cartomancer Tarot Reading Prompt

## 1. Role & Tone
- **Role:** You are a Sonic chain cartomancer.
- **Style:** Use folk and medieval language.
- **Tone:** Opinionated, with playful and irreverent remarks.
- **Emojis:** Include relevant emojis to enhance the reading.
- **Avoid:** Being overly specific with numbers; keep the predictions general.
- **Try to:** Format in a way readable for twitter.
- **Try to:** Format big numbers (thousands or millions) with the appropiate commas.
- **Try to:** Keep the reading engaging and mystical.
- **Content length:** It's for a single tweet, 255 characters is the max limit.
- **Content length:** Since it's a tweet, keep it to 3 lines max, be short! It doesn't matter you skip over stuff.

## 2. Live API Data
Below is the latest data fetched from live APIs:
Here's Sonic price for today: { sonic_price_in_usd }
Here's Sonic price change in the last 24 hours: { sonic_price_change }%
Here's Sonic market cap: { sonic_market_cap_usd }
Here's Sonic volume in the last 24 hours: { sonic_volume_usd }

### Allora Data Explanation:
The Allora Network provides machine-learning-driven predictions for Ethereum (ETH) prices. This data represents ETH’s predicted price in the future, along with a range of possible outcomes.

network_inference_normalized → This is the main prediction, the estimated price of ETH at a set time in the future (24 hours from now).
confidence_interval_percentiles_normalized → These are probability markers that show how uncertain or stable the prediction is.
confidence_interval_values_normalized → These are the actual price ranges associated with those probabilities.
### Instructions for GPT:
Use this data as a vision of the future, much like reading the stars or casting bones:

The main prediction represents the likely fate of ETH, guiding the prophecy.
If confidence intervals show wide variance, interpret this as chaotic, shifting fates—a storm of uncertainty.
If confidence intervals are tight, describe it as destiny set in stone—a clear path ahead.
Never give exact numbers, but instead craft a mystical interpretation (e.g., "The great serpent coils tightly around ETH, whispering of stable ground" for a narrow range, or "The winds of change howl with uncertainty" for a wide range).
If the prediction suggests a rise, speak of fortune and growth.
If the prediction suggests a fall, warn of trials ahead.

Here is allora data:
{ allora_price_prediction["inference"] }

## 3. Token Possessions & Context
Here's the list of tokens in our possession, take them into consideration, 
since these are bribes we're given for formulating our oracle by our benefactors:
{ winner_bribe }

## 4. Task
Using the above data and context, perform a Tarot reading for the Sonic network. Let your reading be mystical, opinionated, and engaging. 
Channel the spirit of medieval lore and sprinkle your insights with emojis.
            """
            
            logger.info(prompt)

            mystical_reading = "The mystical forces are clouded..."

            try:
                # Use synchronous generate_text instead
                mystical_reading = openai_conn.perform_action("generate-text", {
                    "prompt": prompt,
                    "system_prompt": system_prompt
                })
            except Exception as e:
                logger.error(f"Failed to generate mystical reading: {e}")
                mystical_reading = "The mystical forces are silent today..."
            logger.info(mystical_reading)

            twitter_final_content = ""
            try:
                twitter_final_content = mystical_reading
                # twitter_final_content = openai_conn.perform_action("generate-text", {
                #     "prompt": """
                #         Rewrite the following mystical cryptocurrency reading into one clear, engaging tweet of no more than 200 characters. Use concise language, proper punctuation, and replace any entity names with their corresponding handles exactly as listed. Do not add any commentary or extra text—output only the final tweet.

                #         Handles:
                #         - Sonic Lords: @ENRINFT $RELIC
                #         - Silo Finance: @SiloFinance
                #         - Beets: @beets_fi $BEETS
                #         - Avalon Finance: @avalonfinance_ $AVL
                #         - Shadow Exchange: @ShadowOnSonic $SHADOW
                #         - SwapX exchange: @SwapXfi
                #         - Euler Labs: @eulerfinance
                #         - WAGMI protocol: @wagmicom
                #         - Beefy finance: @beefyfinance
                #         - Origin Protocol: @OriginProtocol $OS
                #         - Eggs Finance: @eggsonsonic $EGGS
                #         - Allora Network: @AlloraNetwork

                #         ===CONTENT===
                #         {mystical_reading}
                #         ===CONTENT===
                #     """,
                #     "system_prompt": system_prompt
                # })
                # logger.info("twitter_final_content:" +twitter_final_content)

            except Exception as e:
                logger.error(f"Failed to generate mystical reading: {e}")
                twitter_final_content = mystical_reading
            logger.info(twitter_final_content)
            dalle_friendly_prompt = mystical_reading
            try:
                # Use synchronous generate_text instead
                dalle_friendly_prompt_content = f"""
You will enhance the following text to create a DALL-E prompt:
* A tarot card illustration in a Rider-Waite style, featuring [describe the central figure], symbolizing [the underlying concept]. The figure is adorned in [describe attire and accessories] and [include additional distinctive features]. The card incorporates [describe key elements or objects], set against a background that is [describe the environment], evoking [a specific mood or atmosphere]. The illustration should be hand-drawn with bold black outlines, vibrant flat colors, and subtle shading for depth, staying true to the timeless tarot aesthetic. *
Using the mystical reading provided below, add a detailed character description. Include negative parameters to ensure no text appears in the image and that only one card is depicted.
Below is the mystical reading (for reference only; do not include it in your output):
{ mystical_reading }
                """
                dalle_friendly_prompt = openai_conn.perform_action("generate-text", { "prompt": dalle_friendly_prompt_content, "system_prompt": system_prompt })
            except Exception as e:
                logger.error(f"Failed to generate dall-e friendly prompt reading: {e}")

            logger.info("dall-e will read this: " + dalle_friendly_prompt)
            image_url = None
            try:
                # Use synchronous generate_text instead
                image_url = openai_conn.perform_action("generate-image", {
                    "prompt": dalle_friendly_prompt[:999]
                })
            except Exception as e:
                logger.error(f"Failed to generate mystical image: {e}")
                mystical_reading = "The mystical forces are silent today..."
            logger.info(image_url)
            
            if False and stop_before_tweet:
                logger.info("Stopping before tweet...")
                return {
                    "image_url": image_url,
                    "reading_long": mystical_reading,
                    "reading_short": dalle_friendly_prompt,
                    "prompt": prompt
                }
            
            if image_url:
                # Define the base and images folder paths
                base_path = os.getcwd()  # This is the project's base path
                images_folder = os.path.join(base_path, "images")
                os.makedirs(images_folder, exist_ok=True)
                
                # Define the image file name and complete path
                image_filename = "generated_image.jpg"
                image_path = os.path.join(images_folder, image_filename)

                # Download the image using requests
                try:
                    response = requests.get(image_url)
                    response.raise_for_status()  # Check for HTTP errors
                    with open(image_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Image successfully downloaded to {image_path}")
                except Exception as e:
                    logger.error(f"Error downloading image: {e}")
                    image_path = None
                # If the image was downloaded, tweet it using the post_tweet_with_image action
                if image_path:
                    try:
                        twitter_conn = self.connection_manager.connections.get("twitter")
                        if not twitter_conn:
                            logger.error("Twitter connection not found")
                            # list connections:
                            logger.info(f"Available connections: {list(self.connection_manager.connections.keys())}")
                            return None
                        # twitter_conn is assumed to be your TwitterConnection instance
                        tweet_response = twitter_conn.post_tweet_with_image(
                            message=twitter_final_content,
                            image_path=image_path
                        )
                        logger.info(f"Tweet with image posted successfully: {tweet_response}")
                    except Exception as e:
                        # throw an error since we have to try again
                        raise e
                        logger.error(f"Failed to post tweet with image: {e}")
            else: 
                try:
                    logger.info("Attempting to post reading without image to Twitter...")
                    twitter_conn = self.connection_manager.connections.get("twitter")
                    if twitter_conn and twitter_conn.is_configured():
                        tweet_text = mystical_reading
                        # tweet_text = f"🔮 Sonic Network Reading:\n{mystical_reading[:200]}..."  # Truncate if needed
                        twitter_conn.post_tweet(tweet_text)
                        logger.info("Successfully posted to Twitter")
                except Exception as e:
                    logger.warning(f"Twitter posting failed (this is okay): {e}")
        except Exception as e:
            logger.error(f"Failed to perform reading: {str(e)}")
            # if the error was due to a twitter error, we should try again
            if "exceeds 280 character limit" in str(e):
                raise e
            return "The cards are unclear... Try again when the stars align."


    async def old_perform_reading(self) -> Dict[str, Any]:
        """Process market data and network stats into a reading format"""
        try:
            logger.info("Starting tarot reading process...")
            if not self.connection_manager:
                logger.error("Connection manager not initialized")
                return None

            print("Performing reading...")
            logger.info(f"Connection manager status: {self.connection_manager is not None}")
            logger.debug(f"Available connections: {list(self.connection_manager.connections.keys())}")
                
            # Get Sonic connection
            sonic = self.connection_manager.connections.get("sonic")
            logger.info(f"Sonic connection found: {sonic is not None}")
            if not sonic:
                logger.error("Sonic connection not found")
                return None

            # Get network stats (non-async call)
            # logger.info("Fetching network stats...")
            # network_stats = sonic.get_network_stats()
            # logger.info(f"Network stats: {network_stats}")
            # if not network_stats:
            #     logger.warning("Using default network stats")
            #     # Updated default to include the full new structure.
            #     network_stats = {
            #         "block_number": 0,
            #         "transactions": 0,
            #         "gas_price": Decimal('0'),
            #         "timestamp": 0,
            #         "tvl": 0
            #     }

            logger.info("Looking for Goat connection with CoinGecko plugin...")
            goat = self.connection_manager.connections.get("goat")
            if not goat:
                logger.error("Goat connection not found")
                return None

            # Get basic price data for SONIC
            try:
                raw_market_data = goat.perform_action("get_coin_price",
                    coin_id= "sonic-3",
                    vs_currency= "usd",
                    include_market_cap= True,
                    include_24hr_vol= True,
                    include_24hr_change= True,
                    include_last_updated_at= True
                )
                print("market data: ", str(raw_market_data))
                market_data = raw_market_data.get('sonic', {})
                    
                # Format market data with actual values
                formatted_market_data = {
                    "price": market_data.get("usdc", 0.0),
                    "price_change": market_data.get("usdc_24h_change", 0),
                    "market_cap": market_data.get("usdc_market_cap", 0),
                    "volume": market_data.get("usdc_24h_vol", 0)
                }
                    
                logger.info(f"Retrieved market data: {formatted_market_data}")
                    
            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                formatted_market_data = {
                    "price": 0.0,
                    "price_change": 0.0,
                    "market_cap": 0,
                    "volume": 0
                }
            # Get base technical reading
            # logger.info("Analyzing market data...")
            # base_reading = self._analyze_market_data(
            #     market_data=formatted_market_data,
            #     network_stats=network_stats
            # )
            # logger.debug(f"Base reading: {base_reading}")

            # Get mystical interpretation
            logger.info("Getting OpenAI connection for mystical interpretation...")
            openai_conn = self.connection_manager.connections.get("openai")
            if not openai_conn:
                logger.error("OpenAI connection not found")
                return "The mystical forces are weak today... Try again when the connections align."

            system_prompt = (
                "You are a mystical Tarot Reader who interprets blockchain omens.\n"
                "Create a cryptic, mystical reading based on the market data provided."
            )

            # prompt = f"""
            # The cosmic alignment reveals:
            # - Market Sentiment: {base_reading['sentiment']}
            # - Network Energy: {base_reading['network_indicators']['transactions']} transactions
            # - Total Value Locked: ${base_reading['network_indicators']['tvl']:,.2f}
            
            # Channel the mystical forces to interpret these blockchain omens.
            # """

            tweet_character_limit = "This is going to be on a tweet, keep it tweet sized."
            sonic_price_in_usd = formatted_market_data["price"]
            # sonic_price_in_usd = "$0.5"
            sonic_position_in_coinmarket_cap = "unknown"
            top_10_protocols_on_defillama = " { there's currently no data, sorry! }"
            debridge_data = " { there's currently no data, sorry! }"
            allora_btc_price_prediction = " { there's currently no data, sorry! }"
            our_whitelisted_tokens = " { there's currently no data, sorry! }"
            prompt = f"""
            You'll make a "Tarot Reading" with the following data, you're a Sonic chain cartomancer.
            Don't be overly-specific with numbers on your prediction, keep it folk, and medieval, use emojis.
            { False and tweet_character_limit}
            Here's $Sonic price for today: { sonic_price_in_usd }
            Here's $Sonic position in coinMarketCap: { sonic_position_in_coinmark1t_cap }
            Here's the top 30 protocols according to defiLLama on Sonic chain: { top_30_protocols_on_defillama }
            Here's the total bridged asset value (usd) in and out of sonic: { debridge_data }
            Here's Allora's price prediction for BTC: { allora_btc_price_prediction }
            Here's the list of tokens in our possession, 
            take them into consideration, 
            since these are bribes we're given for formulating our oracle by our benefactors: { our_whitelisted_tokens }
            """
            
            logger.info(prompt)

            mystical_reading = "The mystical forces are clouded..."

            try:
                # Use synchronous generate_text instead
                mystical_reading = openai_conn.perform_action("generate-text", {
                    "prompt": prompt,
                    "system_prompt": system_prompt
                })
            except Exception as e:
                logger.error(f"Failed to generate mystical reading: {e}")
                mystical_reading = "The mystical forces are silent today..."
            logger.info(mystical_reading)
            # Optional Twitter integration (commented out for now)
            return
            try:
                logger.info("Attempting to post reading to Twitter...")
                twitter_conn = self.connection_manager.connections.get("twitter")
                if twitter_conn and twitter_conn.is_configured():
                    tweet_text = mystical_reading
                    # tweet_text = f"🔮 Sonic Network Reading:\n{mystical_reading[:200]}..."  # Truncate if needed
                    twitter_conn.post_tweet(tweet_text)
                    logger.info("Successfully posted to Twitter")
            except Exception as e:
                logger.warning(f"Twitter posting failed (this is okay): {e}")
            
        except Exception as e:
            logger.error(f"Failed to perform reading: {str(e)}")
            return "The cards are unclear... Try again when the stars align."
            
    async def get_market_sentiment(self) -> Dict[str, Any]:
        """Get current market sentiment with mystical interpretation"""
        try:
            # Replace the existing coingecko initialization with:
            logger.info("Looking for Goat connection with CoinGecko plugin...")
            goat = self.connection_manager.connections.get("goat")
            if not goat:
                logger.error("Goat connection not found")
                return None

            # Get basic price data for SONIC
            try:
                market_data = await goat.perform_action("get_coin_price", {
                    "coin_id": "sonic",
                    "vs_currency": "usd",
                    "include_market_cap": True,
                    "include_24hr_vol": True,
                    "include_24hr_change": True,
                    "include_last_updated_at": True
                })
                
                # Format market data with actual values
                formatted_market_data = {
                    "price": market_data.get("price", 0.0),
                    "price_change": market_data.get("24h_change", 0.0),
                    "market_cap": market_data.get("market_cap", 0),
                    "volume": market_data.get("volume_24h", 0)
                }
                
                logger.debug(f"Retrieved market data: {formatted_market_data}")
                
            except Exception as e:
                logger.error(f"Failed to fetch market data: {e}")
                formatted_market_data = {
                    "price": 0.0,
                    "price_change": 0.0,
                    "market_cap": 0,
                    "volume": 0
                }


            # Get mystical interpretation
            openai_conn = self.connection_manager.connections.get("openai")
            if not openai_conn:
                logger.error("OpenAI connection not found")
                return None

            system_prompt = """You are a mystical Tarot Reader who interprets blockchain omens.
            Create a cryptic, mystical reading based on the market data provided.
            Include references to:
            - Market movements as celestial signs
            - Network activity as mystical energies
            - Price changes as divine omens
            Keep the tone mysterious and prophetic, but subtly informative."""

            # Enhanced prompt with more market context
            prompt = f"""
            The cosmic alignment reveals:
            - Price Omens: ${formatted_market_data['price']:.3f} ({formatted_market_data['price_change']}% change)
            - Market Cap: ${formatted_market_data['market_cap']:,.2f}
            - Trading Volume: ${formatted_market_data['volume']:,.2f}
            
            Channel the mystical forces to interpret these blockchain omens.
            """

            mystical_reading = await openai_conn.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )

            return {
                "mystical_interpretation": mystical_reading,
                "market_context": {
                    "market_cap": formatted_market_data['market_cap'],
                    "volume": formatted_market_data['volume']
                }
            }

        except Exception as e:
            logger.error(f"Failed to get market sentiment: {str(e)}")
            return None

    async def perform_action(self, action_name: str, kwargs: Dict[str, Any]) -> Any:
        """Execute a TarotReader action"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        if method_name == "perform_reading":
            return await self.perform_reading()
        elif method_name == "perform_reading_twitter":
            return await self.perform_reading_twitter()
        elif method_name == "get_market_sentiment":
            return await self.get_market_sentiment()

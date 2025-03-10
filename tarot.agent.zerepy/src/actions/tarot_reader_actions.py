import logging
import os
from dotenv import load_dotenv
from src.action_handler import register_action

logger = logging.getLogger("actions.tarot_reader_actions")

# Note: These action handlers are currently simple passthroughs to the tarot_reader_connection methods.
# They serve as hook points where hackathon participants can add custom logic, validation,
# or additional processing before/after calling the underlying connection methods.
# Feel free to modify these handlers to add your own business logic!


@register_action("perform-reading-twitter")
async def perform_reading_twitter(agent, **kwargs):
    """Perform a complete mystical twitter tarot reading using automatically gathered blockchain data"""
    logger.info(f"Performing a reading!")
    tarot_reader = agent.connection_manager.connections.get("tarot-reader")
    if not tarot_reader:
        logger.error("Tarot Reader connection not found")
        return None
    import asyncio
    result = asyncio.run(tarot_reader.perform_action("perform_reading_twitter", {}))
    logger.info(f"Tarot reading result: {result}")
    pass

@register_action("perform-reading")
def perform_reading(agent, **kwargs):
    """Perform a complete mystical tarot reading using automatically gathered blockchain data"""
    try:
        # Get Sonic connection for network stats
        sonic = agent.connection_manager.connections.get("sonic")
        if not sonic:
            logger.error("Sonic connection not found")
            return None

        # Fetch network statistics synchronously
        network_stats = sonic.perform_action("get-network-stats", {})

        # Get CoinGecko connection for market data
        coingecko = next(
            (conn for conn in agent.connection_manager.connections.values() 
             if conn.name == "goat" and 
             any(plugin["name"] == "coingecko" for plugin in conn.config.get("plugins", []))),
            None
        )
        
        if not coingecko:
            logger.error("CoinGecko connection not found")
            return None

        # Fetch comprehensive market data synchronously
        market_data = coingecko.perform_action("get-market-data", {
            "coins": ["sonic"],
            "metrics": ["price", "24h_change", "market_cap", "volume"]
        })

        # Format market data
        formatted_market_data = {
            "price": market_data["sonic"]["price"],
            "price_change": market_data["sonic"]["24h_change"],
            "market_cap": market_data["sonic"]["market_cap"],
            "volume": market_data["sonic"].get("volume", 0)
        }

        # Get base technical reading
        base_reading = agent.connection_manager.connections["tarot_reader"].perform_reading(
            market_data=formatted_market_data,
            network_stats=network_stats
        )

        # Get mystical interpretation
        openai_conn = agent.connection_manager.connections.get("openai")
        if not openai_conn:
            logger.error("OpenAI connection not found")
            return base_reading

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
        - Market Sentiment: {base_reading['sentiment']}
        - Price Omens: ${base_reading['market_indicators']['price']:.3f} ({base_reading['market_indicators']['change']}% change)
        - Network Energy: {base_reading['network_indicators']['transactions']} transactions
        - Total Value Locked: ${base_reading['network_indicators']['tvl']:,.2f}
        - Market Cap: ${formatted_market_data['market_cap']:,.2f}
        - Trading Volume: ${formatted_market_data['volume']:,.2f}
        
        Channel the mystical forces to interpret these blockchain omens.
        """

        mystical_reading = openai_conn.generate_text_sync(
            prompt=prompt,
            system_prompt=system_prompt
        )

        return {
            **base_reading,
            "mystical_interpretation": mystical_reading,
            "market_context": {
                "market_cap": formatted_market_data['market_cap'],
                "volume": formatted_market_data['volume']
            }
        }

    except Exception as e:
        logger.error(f"Failed to perform reading: {str(e)}")
        return None

@register_action("get-market-sentiment")
async def get_market_sentiment(agent, **kwargs):
    """Get current market sentiment with mystical interpretation"""
    try:
        # Automatically fetch current price change
        coingecko = next(
            (conn for conn in agent.connection_manager.connections.values() 
             if conn.name == "goat" and 
             any(plugin["name"] == "coingecko" for plugin in conn.config.get("plugins", []))),
            None
        )
        
        if not coingecko:
            logger.error("CoinGecko connection not found")
            return None

        market_data = await coingecko.perform_action("get-market-data", {
            "coins": ["sonic"],
            "metrics": ["24h_change"]
        })

        price_change = market_data["sonic"]["24h_change"]
        sentiment = agent.connection_manager.connections["tarot_reader"].get_market_sentiment(
            price_change=price_change
        )

        # Get mystical interpretation
        openai_conn = agent.connection_manager.connections.get("openai")
        if openai_conn:
            system_prompt = """You are a mystical market oracle who interprets price movements 
            through the lens of celestial omens and mystical signs."""

            prompt = f"""
            The celestial spheres show a {price_change}% movement, indicating a {sentiment} sentiment.
            Provide a cryptic interpretation of this cosmic omen (2-3 sentences).
            """

            mystical_interpretation = await openai_conn.generate_text(
                prompt=prompt,
                system_prompt=system_prompt
            )

            return {
                "sentiment": sentiment,
                "price_change": price_change,
                "mystical_interpretation": mystical_interpretation
            }

        return {"sentiment": sentiment, "price_change": price_change}

    except Exception as e:
        logger.error(f"Failed to get market sentiment: {str(e)}")
        return None


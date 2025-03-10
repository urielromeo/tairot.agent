import os
import logging
from dotenv import set_key, load_dotenv
from typing import Dict, Any, List, Tuple

import requests
from src.connections.base_connection import BaseConnection, Action, ActionParameter
from src.helpers import print_h_bar

logger = logging.getLogger("connections.telegram_connection")

class TelegramConnectionError(Exception):
    """Base exception for Telegram connection errors"""
    pass

class TelegramConfigurationError(TelegramConnectionError):
    """Raised when there are configuration/credential issues"""
    pass

class TelegramAPIError(TelegramConnectionError):
    """Raised when Telegram API requests fail"""
    pass


class TelegramConnection(BaseConnection):
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        # self._oauth_session = None
    
    @property
    def is_llm_provider(self) -> bool:
        return False

    def validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate Telegram configuration from JSON"""
        required_fields = []
        missing_fields = [field for field in required_fields if field not in config]
        
        if missing_fields:
            raise ValueError(f"Missing required configuration fields: {', '.join(missing_fields)}")

        return config
    
    def register_actions(self) -> None:
        """Register available Telegram actions"""
        self.actions = {
            "send-message": Action(
                name="send-message",
                parameters=[
                    ActionParameter(
                        "chat_id",
                        required=True,
                        type=str,
                        description="Unique identifier for the target chat or username of the target channel (in the format @channelusername)"
                    ),
                    ActionParameter(
                        "text",
                        required=True,
                        type=str,
                        description="Text of the message to be sent"
                    ),
                ],
                description="Send a message via Telegram bot"
            ),
            "send-message-with-image": Action(
                name="send-message-with-image",
                parameters=[
                    ActionParameter(
                        "chat_id",
                        required=True,
                        type=str,
                        description="Unique identifier for the target chat or username of the target channel (in the format @channelusername)"
                    ),
                    ActionParameter(
                        "text",
                        required=True,
                        type=str,
                        description="Caption text for the image"
                    ),
                    ActionParameter(
                        "image_url",
                        required=True,
                        type=str,
                        description="URL of the image to be sent"
                    ),
                ],
                description="Send a message with an image via Telegram bot"
            ),
            "set-webhook": Action(
                name="set-webhook",
                parameters=[
                    ActionParameter(
                        "webhook_url",
                        required=True,
                        type=str,
                        description="The URL to which Telegram should send updates"
                    ),
                    ActionParameter(
                        "secret",
                        required=False,
                        type=str,
                        description="A secret token to be sent in a header “X-Telegram-Bot-Api-Secret-Token” in every webhook request."
                    ),
                    ActionParameter(
                        "allowed_updates",
                        required=False,
                        type=list,
                        description="Optional list of update types to receive (e.g., ['message', 'edited_channel_post'])"
                    ),
                ],
                description="Set the webhook for the Telegram bot"
            ),
            "delete-webhook": Action(
                name="delete-webhook",
                parameters=[],
                description="Delete the current webhook from Telegram"
            ),
            "get-webhook-info": Action(
                name="get-webhook-info",
                parameters=[],
                description="Retrieve current webhook status and configuration from Telegram"
            ),
        }


    def _get_credentials(self) -> Dict[str, str]:
        """Get Telegram credentials from environment with validation"""
        logger.debug("Retrieving Telegram credentials")
        load_dotenv()

        required_vars = {
            'TELEGRAM_API_KEY': 'Telegram API Key',
        }

        credentials = {}
        missing = []

        for env_var, description in required_vars.items():
            value = os.getenv(env_var)
            if not value:
                missing.append(description)
            credentials[env_var] = value

        if missing:
            error_msg = f"Missing Telegram credentials: {', '.join(missing)}"
            raise TelegramConfigurationError(error_msg)

        logger.debug("All required credentials found")
        return credentials

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict:
        """
        Make a request to the Telegram API with error handling

        Args:
            method: HTTP method ('get', 'post', etc.)
            endpoint: API endpoint path (e.g., 'getMe', 'sendMessage')
            **kwargs: Additional request parameters (like params, json, etc.)

        Returns:
            Dict containing the API response
        """
        logger.debug(f"Making {method.upper()} request to Telegram endpoint: {endpoint}")
        try:
            # Get the Telegram API key from credentials
            credentials = self._get_credentials()
            api_key = credentials['TELEGRAM_API_KEY']
            # Construct the full URL for the Telegram API
            full_url = f"https://api.telegram.org/bot{api_key}/{endpoint.lstrip('/')}"
            logger.debug(f"Full URL: {full_url}")

            # Make the HTTP request using the requests library
            response = getattr(requests, method.lower())(full_url, **kwargs)

            # Check for unsuccessful status codes
            if response.status_code not in [200, 201]:
                logger.error(f"Request failed: {response.status_code} - {response.text}")
                raise TelegramAPIError(
                    f"Request failed with status {response.status_code}: {response.text}"
                )

            logger.debug(f"Request successful: {response.status_code}")
            return response.json()

        except Exception as e:
            raise TelegramAPIError(f"API request failed: {str(e)}")

    def configure(self) -> None:
        """Sets up Telegram Connection"""
        logger.info("Starting Telegram setup")

        # Check existing configuration
        if self.is_configured(verbose=False):
            logger.info("Telegram API is already configured")
            response = input("Do you want to reconfigure? (y/n): ")
            if response.lower() != 'y':
                return

        setup_instructions = [
            "\n🤖 TELEGRAM AUTHENTICATION SETUP",
            "\n📝 To get your Telegram API key:",
            "1. Create your bot using Telegram's BotFather",
            "2. Obtain your API Key"
        ]
        logger.info("\n".join(setup_instructions))
        print_h_bar()

        try:
            # Prompt the user for the API key
            logger.info("\nPlease enter your Telegram API key:")
            api_key = input("Enter your API Key: ").strip()

            # Validate the API key by calling the getMe endpoint
            test_url = f"https://api.telegram.org/bot{api_key}/getMe"
            response = requests.get(test_url)
            if response.status_code != 200:
                raise TelegramAPIError(f"Failed to contact Telegram API. Status code: {response.status_code}")

            result = response.json()
            if not result.get("ok"):
                raise TelegramAPIError("Invalid Telegram API key or error in API response.")

            bot_info = result.get("result", {})
            bot_id = bot_info.get("id")
            bot_username = bot_info.get("username")

            # Save credentials to .env
            if not os.path.exists('.env'):
                logger.debug("Creating new .env file")
                with open('.env', 'w') as f:
                    f.write('')

            env_vars = {
                'TELEGRAM_API_KEY': api_key,
                'TELEGRAM_BOT_ID': str(bot_id),
                'TELEGRAM_BOT_USERNAME': bot_username
            }

            for key, value in env_vars.items():
                set_key('.env', key, value)
                logger.debug(f"Saved {key} to .env")

            logger.info("\n✅ Telegram authentication successfully set up!")
            logger.info("Your API key and bot details have been stored in the .env file.")
            return True

        except Exception as e:
            error_msg = f"Setup failed: {str(e)}"
            logger.error(error_msg)
            raise TelegramConfigurationError(error_msg)

    def is_configured(self, verbose=False) -> bool:
        """Check if Telegram credentials are configured and valid"""
        logger.debug("Checking Telegram configuration status")
        try:
            # Check if credentials exist
            credentials = self._get_credentials()

            # Validate the configuration by calling getMe
            test_url = f"https://api.telegram.org/bot{credentials['TELEGRAM_API_KEY']}/getMe"
            response = requests.get(test_url)
            if response.status_code != 200 or not response.json().get("ok"):
                raise TelegramAPIError("Invalid API key or unable to reach Telegram API.")

            logger.debug("Telegram configuration is valid")
            return True

        except Exception as e:
            if verbose:
                error_msg = str(e)
                if isinstance(e, TelegramConfigurationError):
                    error_msg = f"Configuration error: {error_msg}"
                elif isinstance(e, TelegramAPIError):
                    error_msg = f"API validation error: {error_msg}"
                logger.error(f"Configuration validation failed: {error_msg}")
            return False

    def perform_action(self, action_name: str, kwargs) -> Any:
        """Execute a Telegram action with validation"""
        if action_name not in self.actions:
            raise KeyError(f"Unknown action: {action_name}")

        action = self.actions[action_name]
        errors = action.validate_params(kwargs)
        if errors:
            raise ValueError(f"Invalid parameters: {', '.join(errors)}")

        # Call the appropriate method based on action name
        method_name = action_name.replace('-', '_')
        method = getattr(self, method_name)
        return method(**kwargs)

    def set_webhook(self, webhook_url: str, secret: str = None, allowed_updates: List[str] = None) -> dict:
        """
        Registers a webhook URL with Telegram.
        
        Args:
            webhook_url: The URL where Telegram will send updates.
            allowed_updates: List of update types to receive (e.g., ['message', 'edited_channel_post']).
            
        Returns:
            A dict containing the API response.
        """
        payload = {"url": webhook_url}
        if allowed_updates:
            payload["allowed_updates"] = allowed_updates

        if secret:
            payload["secret"] = secret

        return self._make_request("post", "setWebhook", json=payload)

    def delete_webhook(self) -> dict:
        """
        Removes the currently set webhook.
        
        Returns:
            A dict containing the API response.
        """
        return self._make_request("post", "deleteWebhook")

    def get_webhook_info(self) -> dict:
        """
        Retrieves information about the current webhook status.
        
        Returns:
            A dict containing webhook details.
        """
        return self._make_request("get", "getWebhookInfo")

    def send_message(self, chat_id: int, text: str, **kwargs) -> dict:
        """
        Send a message via Telegram bot.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel (in format @channelusername).
            text: Text of the message to be sent.
            **kwargs: Additional optional parameters to pass to the Telegram API (e.g., parse_mode, disable_notification, etc.)

        Returns:
            A dict containing the Telegram API response.
        """
        payload = {
            "chat_id": chat_id,
            "text": text
        }
        # Merge any additional optional parameters into the payload
        payload.update(kwargs)

        return self._make_request("post", "sendMessage", json=payload)

    def send_message_with_image(self, chat_id: int, text: str, image_url: str, **kwargs) -> dict:
        """
        Send a message with an image via Telegram bot.

        Args:
            chat_id: Unique identifier for the target chat or username of the target channel.
            text: Caption text for the image.
            image_url: URL of the image to be sent.
            **kwargs: Additional optional parameters to pass to the Telegram API.

        Returns:
            A dict containing the Telegram API response.
        """
        payload = {
            "chat_id": chat_id,
            "photo": image_url,
            "caption": text
        }
        # Merge any additional optional parameters into the payload
        payload.update(kwargs)

        return self._make_request("post", "sendPhoto", json=payload)
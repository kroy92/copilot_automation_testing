import json
import logging
from typing import List, Dict, Any
import requests
import websocket

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
HEADERS_CONTENT_TYPE = {'Content-Type': 'application/json'}


class BotClient:
    """
    A client to interact with a bot using Direct Line API and WebSocket for real-time communication.

    Attributes:
        endpoint (str): The endpoint URL to obtain the bot token.
        conversation_id (str): The ID of the conversation with the bot.
        conversation_token (str): The token for the conversation.
        ws (websocket.WebSocket): The WebSocket connection to the bot.
    """

    def __init__(self, endpoint: str):
        """
        Initialize the BotClient with the given endpoint.

        Args:
            endpoint (str): The endpoint URL to obtain the bot token.
        """
        self.endpoint = endpoint
        self.conversation_id: str = None
        self.conversation_token: str = None
        self.ws: websocket.WebSocket = None

    def connect(self) -> None:
        """
        Establish a connection with the bot by obtaining a token and starting a WebSocket connection.

        Raises:
            requests.RequestException: If there is an error in the HTTP request.
        """
        try:
            response = requests.get(self.endpoint)
            response.raise_for_status()
            token = response.json()['token']

            headers = {'Authorization': f'Bearer {token}', **HEADERS_CONTENT_TYPE}
            response = requests.post('https://directline.botframework.com/v3/directline/conversations', headers=headers)
            response.raise_for_status()

            conversation_data = response.json()
            self.conversation_id = conversation_data['conversationId']
            self.conversation_token = conversation_data['token']
            stream_url = conversation_data['streamUrl']

            self.ws = websocket.WebSocket()
            self.ws.connect(stream_url)
            logger.info("Successfully connected to the bot.")

        except requests.RequestException as e:
            logger.error(f"Failed to connect to bot: {e}")
            raise

    def disconnect(self) -> None:
        """
        Close the WebSocket connection with the bot.
        """
        if self.ws:
            self.ws.close()
            logger.info("WebSocket connection closed.")
        else:
            logger.warning("WebSocket connection is not established.")

    def send(self, message: str) -> None:
        """
        Send a message to the bot.

        Args:
            message (str): The message to send to the bot.

        Raises:
            requests.RequestException: If there is an error in the HTTP request.
        """
        headers = {'Authorization': f'Bearer {self.conversation_token}', **HEADERS_CONTENT_TYPE}
        payload = {
            'locale': 'en-EN',
            'type': 'message',
            'from': {'id': 'user1'},
            'text': message
        }
        url = f'https://directline.botframework.com/v3/directline/conversations/{self.conversation_id}/activities'

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            logger.info("Message sent successfully.")
        except requests.RequestException as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def receive(self, timeout: int = 20) -> List[str]:
        """
        Receive messages from the bot over WebSocket.

        Args:
            timeout (int): The timeout for receiving messages in seconds. Default is 20 seconds.

        Returns:
            List[str]: A list of messages received from the bot.

        Raises:
            Exception: If the WebSocket connection is closed unexpectedly.
        """
        self.ws.settimeout(timeout)
        message_buffer = ''

        while True:
            try:
                frame = self.ws.recv()
                message_buffer += frame
                try:
                    parsed_message = json.loads(message_buffer)
                    responses = self._extract_bot_responses(parsed_message)
                    if responses:
                        logger.info("Bot response received.")
                        return responses
                    else:
                        message_buffer = ''
                except json.JSONDecodeError:
                    # Continue accumulating data
                    continue
            except websocket.WebSocketTimeoutException:
                logger.warning("WebSocket timeout occurred.")
                return []
            except websocket.WebSocketConnectionClosedException:
                logger.error("WebSocket connection closed unexpectedly.")
                raise Exception('WebSocket connection closed')

    @staticmethod
    def _extract_bot_responses(data: Dict[str, Any]) -> List[str]:
        """
        Extract bot responses from JSON data.

        Args:
            data (Dict[str, Any]): The JSON data containing bot responses.

        Returns:
            List[str]: A list of bot responses.
        """
        responses = []
        for activity in data.get('activities', []):
            if activity.get('type') == 'message' and activity.get('from', {}).get('role') == 'bot':
                responses.append(activity.get('text', ''))
                if 'suggestedActions' in activity:
                    for action in activity['suggestedActions'].get('actions', []):
                        responses.append(action['title'])
        return responses


if __name__ == "__main__":
    try:
        bot = BotClient("your_endpoint_here")
        bot.connect()
        bot.send("Hello, bot!")
        responses = bot.receive()
        for response in responses:
            print(response)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

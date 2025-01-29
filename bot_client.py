import json
import requests
import websocket

# Constants
HEADERS_CONTENT_TYPE = {'Content-Type': 'application/json'}


class BotClient:
    def __init__(self, endpoint):
        self.endpoint = endpoint
        self.conversation_id = None
        self.conversation_token = None
        self.ws = None

    def connect(self):
        """Establish a connection with the bot."""
        response = requests.get(self.endpoint)
        response.raise_for_status()
        token = response.json()['token']

        headers = {'Authorization': f'Bearer {token}', **HEADERS_CONTENT_TYPE}
        response = requests.post('https://directline.botframework.com/v3/directline/conversations', headers=headers)
        response.raise_for_status()
        #print(response.json())

        conversation_data = response.json()
        self.conversation_id = conversation_data['conversationId']
        self.conversation_token = conversation_data['token']
        stream_url = conversation_data['streamUrl']

        self.ws = websocket.WebSocket()
        self.ws.connect(stream_url)

    def send(self, message):
        """Send a message to the bot."""
        headers = {'Authorization': f'Bearer {self.conversation_token}', **HEADERS_CONTENT_TYPE}
        payload = {
            'locale': 'en-EN',
            'type': 'message',
            'from': {'id': 'user1'},
            'text': message
        }
        url = f'https://directline.botframework.com/v3/directline/conversations/{self.conversation_id}/activities'
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()

    def receive(self):
        """Receive messages from the bot over WebSocket."""
        self.ws.settimeout(20)
        message_buffer = ''

        while True:
            try:
                frame = self.ws.recv()
                message_buffer += frame
                try:
                    parsed_message = json.loads(message_buffer)
                    # print(parsed_message)
                    ls: list = self._extract_bot_responses(parsed_message)
                    if len(ls) > 0:
                        return ls
                    else:
                        message_buffer = ''
                        raise json.JSONDecodeError('No bot responses found', '', 0)
                except json.JSONDecodeError:
                    pass  # Continue accumulating
            except websocket.WebSocketTimeoutException:
                return None
            except websocket.WebSocketConnectionClosedException:
                raise Exception('WebSocket connection closed')

    @staticmethod
    def _extract_bot_responses(data):
        """Extract bot responses from JSON."""
        responses = []
        for activity in data.get('activities', []):
            if activity.get('type') == 'message' and activity.get('from', {}).get('role') == 'bot':
                responses.append(activity.get('text', ''))
                if 'suggestedActions' in activity:
                    for action in activity['suggestedActions'].get('actions', []):
                        responses.append(action['title'])
        return responses

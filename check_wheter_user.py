import json

import requests
import websocket

copilot_token_endpoint = ('https://default90474664dbca4de489503382fc4737.e4.environment.api.powerplatform.com'
                          '/powervirtualagents/botsbyschema/cr437_weather/directline/token?api-version=2022-03-01'
                          '-preview')

# send a request to the endpoint for the token
response = requests.get(copilot_token_endpoint)
token = response.json()['token']
bearer_token = 'Bearer ' + token

start_conversation_endpoint = 'https://directline.botframework.com/v3/directline/conversations'
headers = {
    'Authorization': bearer_token,
    'Content-Type': 'application/json'
}
response = requests.post(start_conversation_endpoint, headers=headers)
conversation_id = response.json()['conversationId']
conversation_token = response.json()['token']
stream_url = response.json()['streamUrl']


def print_only_text_and_suggestions_for_bot(json_str):
    data = json.loads(json_str)

    for activity in data.get('activities', []):
        # Check if the activity is from a bot and type is message
        if activity.get('type') == 'message' and activity.get('from', {}).get('role') == 'bot':
            # if activity.get('from', {}).get('role') == 'bot':
            print('Received message from bot:')
            print(f"Activity type: {activity['type']}")
            # Print the text if it exists
            if 'text' in activity:
                print(f"{activity['text']}")

            # Print suggested actions if they exist
            if 'suggestedActions' in activity and 'actions' in activity['suggestedActions']:
                for action in activity['suggestedActions']['actions']:
                    print(f"{action['title']}")


def send_http_messsage_to_bot(message):
    conversation_bearer_token = 'Bearer ' + conversation_token
    headers = {
        'Authorization': conversation_bearer_token,
        'Content-Type': 'application/json'
    }
    message_payload = {
        'locale': 'en-EN',
        'type': 'message',
        'from': {
            'id': 'user1'
        },
        'text': message
    }
    send_message_endpoint = f'https://directline.botframework.com/v3/directline/conversations/{conversation_id}/activities'
    response = requests.post(send_message_endpoint, headers=headers, json=message_payload)
    if response.status_code != 200:
        raise Exception('Failed to send message to bot')
    return response.json()


def receive_websocket_message(ws):
    ws.settimeout(20)  # Set a 5-second timeout for each recv operation
    last_s = None
    message_received = ''
    while True:
        try:
            frame = ws.recv()
            message_received += frame
            try:
                # Attempt to parse the accumulated message as JSON
                s = json.loads(message_received)

                print_only_text_and_suggestions_for_bot(message_received)
                # Reset message_received for the next message
                last_s = s
                message_received = ''
            except json.JSONDecodeError:
                # If not complete JSON yet, continue accumulating
                pass
        except websocket.WebSocketTimeoutException:
            # Optional: Decide what to do after a timeout, for now, just continue waiting
            return last_s
        except websocket.WebSocketConnectionClosedException:
            raise Exception('WebSocket connection closed')


# open a websocket connection to the stream URL
ws = websocket.WebSocket()
ws.connect(stream_url)
messages = ['hi', 'weather', 'hyderabad', 'tomorrow', 'Rainy', 'Get Forecast For Tomorrow', 'Mumbai', 'Ok  Bye', 'Yes',
            'No']
for message in messages:
    # send a message to the bot
    send_http_messsage_to_bot(message)
    print('Message sent to bot:', message)

    # receive the response from the bot
    response = receive_websocket_message(ws)

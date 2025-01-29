import json
import os
from dotenv import load_dotenv
import pytest
from copilot_chat_client import BotClient

# Load environment variables
load_dotenv()

# Fetch the endpoint
BOT_ENDPOINT = os.getenv("BOT_ENDPOINT")


@pytest.fixture
def bot_client():
    """Fixture to initialize and connect to the bot."""
    client = BotClient(BOT_ENDPOINT)
    client.connect()
    yield client
    client.disconnect()  # Ensure the connection is properly closed after tests


def test_connection(bot_client):
    """Test if the bot client connects successfully."""
    assert bot_client.conversation_id is not None, "Conversation ID should not be None"
    assert bot_client.conversation_token is not None, "Conversation token should not be None"
    assert bot_client.ws is not None, "WebSocket should be established"


def test_send_and_receive(bot_client):
    """Test sending and receiving a message from the bot."""
    bot_client.send("Hello")
    response = bot_client.receive()
    print(response)
    assert response is not None, "Bot did not respond"
    assert any("hello" in msg.lower() for msg in response), f"Expected greeting in bot response: {response}"


def test_multiple_messages(bot_client):
    """Test a conversation with multiple exchanges."""
    messages = ["Hi", "Weather", "Hyderabad", "Tomorrow"]
    for msg in messages:
        bot_client.send(msg)
        response = bot_client.receive()
        print(response)
        assert response is not None, f"No response for message: {msg}"
        assert '' not in response, f"Empty response for message: {msg}"


def test_conversation_flow(bot_client):
    """Test a conversation flow with multiple specific messages."""
    messages = [
        "hi",
        "weather",
        "hyderabad",
        "tomorrow",
        "Rainy",
        "Get Forecast For Tomorrow",
        "Mumbai",
        "Ok Bye",
        "Yes",
        "No"
    ]
    for msg in messages:
        bot_client.send(msg)
        response = bot_client.receive()
        print(response)
        assert response is not None, f"No response for message: {msg}"
        assert '' not in response, f"Empty response for message: {msg}"


if __name__ == "__main__":
    # Run the tests
    pytest.main(['-v', __file__])
import json

import pytest
from copilot_clientv2 import BotClient

# Replace with the actual endpoint
BOT_ENDPOINT = ("https://default90474664dbca4de489503382fc4737.e4.environment.api.powerplatform.com/powervirtualagents"
                "/botsbyschema/cr437_weather/directline/token?api-version=2022-03-01-preview")


@pytest.fixture
def bot_client():
    """Fixture to initialize and connect to the bot."""
    client = BotClient(BOT_ENDPOINT)
    client.connect()
    return client


def test_connection(bot_client):
    """Test if the bot client connects successfully."""
    assert bot_client.conversation_id is not None
    assert bot_client.conversation_token is not None
    assert bot_client.ws is not None


def test_send_and_receive(bot_client):
    """Test sending and receiving a message from the bot."""
    bot_client.send("Hello")
    response = bot_client.receive()
    print(response)
    assert response is not None, "Bot did not respond"
    assert any("hello" in msg.lower() for msg in response), "Expected greeting in bot response" + str(response)


def test_multiple_messages(bot_client):
    """Test a conversation with multiple exchanges."""
    messages = ["Hi", "Weather", "Hyderabad", "Tomorrow"]
    for msg in messages:
        bot_client.send(msg)
        response = bot_client.receive()
        print(response)
        assert response is not None, f"No response for message: {msg}"
        assert '' not in response, f"Empty response for message: {msg}"


if __name__ == "__main__":
    # Run the tests
    pytest.main(['-v', __file__])
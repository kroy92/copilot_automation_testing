from copilot_chat_client import BotClient
import os
import pytest
from dotenv import load_dotenv
from semantic_assertion import SemanticSimilarityClient

# Load environment variables
load_dotenv()

# Fetch the endpoint
PERFORMANCE_BOT_ENDPOINT = os.getenv("PERFORMANCE_BOT_ENDPOINT")


@pytest.fixture
def bot_client():
    """Fixture to initialize and connect to the bot."""
    client = BotClient(PERFORMANCE_BOT_ENDPOINT)
    client.connect()
    yield client
    client.disconnect()  # Ensure the connection is properly closed after tests


def test_connection(bot_client):
    """Test if the bot client connects successfully."""
    assert bot_client.conversation_id is not None, "Conversation ID should not be None"
    assert bot_client.conversation_token is not None, "Conversation token should not be None"
    assert bot_client.ws is not None, "WebSocket should be established"


def test_garbage_collection_conversion(bot_client):
    """Test sending and receiving a message from the bot."""
    load_dotenv()
    similarity_client = SemanticSimilarityClient(os.getenv("ENDPOINT_NAME"), os.getenv("API_KEY"),
                                                 os.getenv("DEPLOYMENT_NAME"),
                                                 os.getenv("API_VERSION"))
    bot_client.send("Hello")
    response = bot_client.receive()
    print(response)
    assert response is not None, "Bot did not respond"
    assert any("hello" in msg.lower() for msg in response), f"Expected greeting in bot response: {response}"

    bot_client.send('What is Garbage collection in JVM?')
    response = bot_client.receive()
    print(response)
    similarity_client.assert_semantically("Garbage collection in JVM is a form of automatic memory management used to "
                                          "reclaim memory occupied by objects that are no longer in use",
                                          response[0], threshold=0.8)

    bot_client.send('What do you mean by no longer in use')
    response = bot_client.receive()
    print(response)
    similarity_client.assert_semantically("Objects that are no longer in use refer to objects that are no longer "
                                          "reachable or referenced by any part of the program, making them eligible "
                                          "for memory reclamation by the garbage collector",
                                          response[0], threshold=0.8)

    bot_client.send('Can static collection references cause memory leaks?')
    response = bot_client.receive()
    print(response)
    similarity_client.assert_semantically("Yes, static collection references can cause memory leaks if they are not "
                                          "properly managed or released, as they can keep objects alive longer than "
                                          "necessary, preventing them from being garbage collected",
                                          response[0], threshold=0.8)

    bot_client.send('what is difference between concurrent mark sweep and parallel garbage collection?')
    response = bot_client.receive()
    print(response)
    similarity_client.assert_semantically(expected="Concurrent Mark-Sweep (CMS) is a garbage collector that "
                                                   "enables concurrent collection, automatically enabling "
                                                   "ParNewGC by default. Parallel GC uses a single-threaded "
                                                   "garbage collector for the old generation and a "
                                                   "multi-threaded garbage collector for the young generation ",
                                          actual=response[0], threshold=0.8)

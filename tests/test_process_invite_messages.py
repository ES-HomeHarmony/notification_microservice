import pytest
from unittest.mock import MagicMock, patch
from app.main import process_invite_messages

@pytest.fixture
def kafka_message():
    return {
        "action": "create_user",
        "user_data": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        }
    }

@patch("app.main.invite_consumer")
@patch("app.main.process_user_data")
def test_process_invite_messages_success(mock_process_user_data, mock_invite_consumer, kafka_message):
    # Mock Kafka consumer behavior for a valid message
    mock_message = MagicMock()
    mock_message.value = kafka_message
    mock_invite_consumer.__iter__.return_value = [mock_message]

    # Call the function
    process_invite_messages()

    # Assert that process_user_data was called with the correct user data
    mock_process_user_data.assert_called_once_with(kafka_message["user_data"])

@patch("app.main.invite_consumer")
@patch("app.main.process_user_data")
def test_process_invite_messages_exception(mock_process_user_data, mock_invite_consumer, kafka_message):
    # Mock Kafka consumer behavior with an exception during processing
    mock_message = MagicMock()
    mock_message.value = kafka_message
    mock_invite_consumer.__iter__.return_value = [mock_message]

    # Simulate an exception in process_user_data
    mock_process_user_data.side_effect = Exception("Test exception")

    # Call the function
    process_invite_messages()

    # Assert that the exception was handled (process_user_data was called, but no crash)
    mock_process_user_data.assert_called_once_with(kafka_message["user_data"])

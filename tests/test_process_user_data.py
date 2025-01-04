import pytest
from unittest.mock import patch, mock_open
from app.main import process_user_data

@pytest.fixture
def user_data():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    }

@patch("builtins.open", new_callable=mock_open, read_data="<h1>Welcome, {{name}}</h1>")
@patch("app.main.send_email")
def test_process_user_data(mock_send_email, mock_open, user_data):
    # Call the function
    process_user_data(user_data)

    # Assert the file was opened correctly
    mock_open.assert_called_once_with("templates/invite.html", 'r', encoding='utf-8')

    # Assert that send_email was called with the correct arguments
    mock_send_email.assert_called_once_with(
        user_data["email"],
        "Welcome to Home Harmony!",
        "<h1>Welcome, Jane Doe</h1>"
    )

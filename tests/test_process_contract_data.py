import pytest
from unittest.mock import patch, mock_open
from app.main import process_contract_data

@pytest.fixture
def user_data():
    return {
        "name": "Jane Doe",
        "email": "jane.doe@example.com"
    }

@patch("builtins.open", new_callable=mock_open, read_data="<h1>Dear, {{name}}</h1>")
@patch("app.main.send_email")
def test_process_contract_data(mock_send_email, mock_open, user_data):
    # Call the function
    process_contract_data(user_data)

    # Assert the file was opened correctly
    mock_open.assert_called_once_with("templates/contract.html", 'r', encoding='utf-8')

    # Assert that send_email was called with the correct arguments
    mock_send_email.assert_called_once_with(
        user_data["email"],
        "Contract Uploaded!",
        "<h1>Dear, Jane Doe</h1>"
    )

import pytest
from unittest.mock import patch, ANY
from app.main import startup_event

@patch("threading.Thread")
def test_startup_event_success(mock_thread):
    # Simulate thread behavior
    mock_thread_instance = mock_thread.return_value

    # Call the startup_event function
    startup_event()

    # Assert that the thread was initialized and started
    mock_thread.assert_called_once_with(
        target=ANY, daemon=True
    )
    mock_thread_instance.start.assert_called_once()


@patch("threading.Thread")
def test_startup_event_exception(mock_thread):
    # Simulate an exception during thread initialization
    mock_thread.side_effect = Exception("Thread initialization failed")

    # Call the startup_event function and ensure it handles the exception
    try:
        startup_event()
    except Exception as e:
        pytest.fail(f"startup_event raised an unexpected exception: {e}")

    # Assert that the thread was attempted to be started despite the exception
    mock_thread.assert_called_once_with(
        target=ANY, daemon=True
    )

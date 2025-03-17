"""
This module contains unit tests for the DirectMessenger, ds_protocol, and Profile classes.
It tests functionality such as message extraction, connection handling, and profile management.
"""

import json
from unittest.mock import patch, MagicMock
import pytest
from ds_messenger import DirectMessenger
from ds_protocol import extract_json
from Profile import Profile


# Test ds_protocol.py
def test_extract_json_with_message():
    """Test extracting a JSON response with a message."""
    json_msg = json.dumps({"response": {"type": "ok", "message": "Test"}})
    result = extract_json(json_msg)
    assert result.response_type == "ok" and result.message == "Test"


def test_extract_json_with_messages():
    """Test extracting a JSON response with a list of messages."""
    json_msg = json.dumps({
        "response": {
            "type": "ok",
            "messages": [{"from": "user", "entry": "Hi",
                          "timestamp": "2023-10-01T12:00:00Z"}]
        }
    })
    result = extract_json(json_msg)
    assert result.response_type == "ok" and result.messages == [
        {"from": "user", "entry": "Hi", "timestamp": "2023-10-01T12:00:00Z"}
    ]


def test_extract_json_invalid():
    """Test extracting an invalid JSON response."""
    assert extract_json("invalid_json") is None


# Test ds_messenger.py
@patch('socket.socket')
def test_connect_success(mock_socket):
    """Test successful connection to the server."""
    mock_socket.return_value.makefile.return_value.readline.return_value = (
        json.dumps({"response": {"type": "ok", "token": "test_token"}}))
    dm = DirectMessenger("test_server", "test_user", "test_password")
    assert dm.profile.token == "test_token"


@patch('socket.socket')
def test_connect_failure(mock_socket):
    """Test failed connection to the server."""
    mock_socket.return_value.makefile.return_value.readline.return_value = (
        json.dumps({"response": {"type": "error"}}))
    with pytest.raises(ConnectionError):
        DirectMessenger("test_server", "test_user", "test_password")


@patch('socket.socket')
def test_send_message_success(mock_socket):
    """Test successfully sending a message."""
    mock_socket.return_value.makefile.return_value.readline.side_effect = [
        json.dumps({"response": {"type": "ok", "token": "test_token"}}),
        json.dumps({"response": {"type": "ok",
                                 "message": "Direct message sent"}})
    ]
    dm = DirectMessenger("test_server", "test_user", "test_password")
    assert dm.send("Hello", "test_recipient") is True


@patch('socket.socket')
def test_send_message_failure(mock_socket):
    """Test failing to send a message."""
    mock_socket.return_value.makefile.return_value.readline.side_effect = [
        json.dumps({"response": {"type": "ok", "token": "test_token"}}),
        json.dumps({"response": {"type": "error"}})
    ]
    dm = DirectMessenger("test_server", "test_user", "test_password")
    assert dm.send("Hello", "test_recipient") is False


@patch('socket.socket')
def test_retrieve_new(mock_socket):
    """Test retrieving new messages."""
    mock_socket.return_value.makefile.return_value.readline.side_effect = [
        json.dumps({"response": {"type": "ok", "token": "test_token"}}),
        json.dumps({
            "response": {
                "type": "ok",
                "messages": [{"from": "user", "entry": "Hi",
                              "timestamp": "2023-10-01T12:00:00Z"}]
            }
        })
    ]
    dm = DirectMessenger("test_server", "test_user", "test_password")
    messages = dm.retrieve_new()
    assert len(messages) == 1 and messages[0].sender == "user"


@patch('socket.socket')
def test_retrieve_all(mock_socket):
    """Test retrieving all messages."""
    mock_socket.return_value.makefile.return_value.readline.side_effect = [
        json.dumps({"response": {"type": "ok", "token": "test_token"}}),
        json.dumps({
            "response": {
                "type": "ok",
                "messages": [{"from": "user", "entry": "Hi",
                              "timestamp": "2023-10-01T12:00:00Z"}]
            }
        })
    ]
    dm = DirectMessenger("test_server", "test_user", "test_password")
    messages = dm.retrieve_all()
    assert len(messages) == 1 and messages[0].sender == "user"

@patch('socket.socket')
def test_close_connection(mock_socket):
    """Test closing the connection to the server."""
    mock_socket_instance = MagicMock()
    mock_socket.return_value = mock_socket_instance
    mock_socket_instance.makefile.return_value.readline.return_value = (
        json.dumps({"response": {"type": "ok", "token": "test_token"}})
    )
    dm = DirectMessenger("test_server", "test_user", "test_password")
    dm.close_connection()
    mock_socket_instance.close.assert_called_once()


# profile.py testing
def test_profile_add_msg():
    """Test adding a message to the profile."""
    profile = Profile("test_server", "test_user", "test_password")
    profile.add_msg({"message": "Hi"})
    assert len(profile.messages) == 1


def test_profile_add_rec():
    """Test adding a recipient to the profile."""
    profile = Profile("test_server", "test_user", "test_password")
    profile.add_rec("user1")
    assert "user1" in profile.recipients


def test_profile_save_and_load():
    """Test saving and loading a profile."""
    profile = Profile("test_server", "test_user", "test_password")
    profile.add_msg({"message": "Hi"})
    profile.save_profile("test_profile.dsu", "user_k")
    loaded_profile = Profile("test_server", "test_user", "test_password")
    loaded_profile.load_profile("test_profile.dsu", "user_k")
    assert len(loaded_profile.messages) == 1

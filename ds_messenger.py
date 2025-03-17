"""
Module for handling direct messaging via a socket connection.
"""
import socket
import time
import json
import ds_protocol as dsp
from Profile import Profile


class DirectMessage:
    """Represents a direct message."""
    def __init__(self):
        self.recipient = None
        self.message = None
        self.timestamp = None
        self.sender = None

    def set_message(self, sender, recipient, message, timestamp):
        """Sets message details."""
        self.sender = sender
        self.recipient = recipient
        self.message = message
        self.timestamp = timestamp

    def get_message(self) -> dict:
        """Returns the message details as a dictionary."""
        return {
            "sender": self.sender,
            "recipient": self.recipient,
            "message": self.message,
            "timestamp": self.timestamp
        }


class DirectMessenger:
    """Handles direct messaging functionalities."""
    def __init__(self, dsuserver=None, username=None,
                 password=None):
        """Initializes the DirectMessenger with server details
           and credentials."""
        self.token = None
        self.dsuserver = dsuserver
        self.username = username
        self.password = password
        self.socket = None
        self.profile = Profile(dsuserver, username, password)
        self.connect()

    def join_req(self, jsonobj):
        """Sends a join request to the server."""
        sendreq = self.socket.makefile("w")
        sendreq.write(jsonobj + "\r\n")
        sendreq.flush()

    def connect(self):
        """Establishes a connection to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.profile.dsuserver, 3001))
            join = json.dumps({
                "join": {
                    "username": self.profile.username,
                    "password": self.profile.password,
                    "token": self.profile.token
                }
            })
            self.join_req(join)
            receive = self.socket.makefile("r").readline().strip()
            p_resp = dsp.extract_json(receive)

            if p_resp.response_type != "ok":
                raise ConnectionError("Failed to connect to server.")

            self.profile.token = p_resp.token

        except ConnectionRefusedError as e:
            raise e

        except (socket.timeout, socket.error, json.JSONDecodeError) as err:
            print(f"Connection error: {err}")
            self.close_connection()

    def close_connection(self):
        """Closes the connection to the server."""
        if self.socket:
            self.socket.close()
            self.socket = None

    def send(self, message: str, recipient: str) -> bool:
        """Sends a direct message to a recipient."""
        if not self.profile.token:
            raise ValueError("Unauthenticated, connect to server first.")

        if recipient not in self.profile.recipients:
            self.profile.add_rec(recipient)
        dm = json.dumps({
            "token": self.profile.token,
            "directmessage": {
                "entry": message,
                "recipient": recipient,
                "timestamp": str(time.time())
            }
        })
        try:
            self.join_req(dm)
            receive = (self.socket.makefile("r")
                       .readline().strip())
            response = dsp.extract_json(receive)
            if (response.response_type == "ok" and
               response.message == "Direct message sent"):
                self.profile.add_msg({
                    "type": "sent",
                    "recipient": recipient,
                    "message": message,
                    "timestamp": time.time()
                })
                return True
            return False
        except (socket.error, json.JSONDecodeError) as err:
            print(f"Error sending message: {err}")
            self.close_connection()
            return False

    def retrieve_new(self) -> list:
        """Retrieves new messages."""
        if not self.profile.token:
            raise ValueError("Unauthenticated, connect to server first.")

        newmsg_req = json.dumps({
            "token": self.profile.token,
            "directmessage": "new"
        })
        try:
            self.join_req(newmsg_req)
            receive = self.socket.makefile("r").readline().strip()
            response = dsp.extract_json(receive)
            messages = []
            if response.response_type == "ok":
                for msg in response.messages:
                    self.profile.add_msg(msg)
                    dm = DirectMessage()
                    dm.sender = msg["from"]
                    dm.message = msg["entry"]
                    dm.timestamp = msg["timestamp"]
                    messages.append(dm)
            return messages
        except (socket.error, json.JSONDecodeError) as err:
            print(f"Error retrieving new messages: {err}")
            self.close_connection()
            return []

    def retrieve_all(self) -> list:
        """Retrieves all messages."""
        if not self.profile.token:
            raise ValueError("Unauthenticated, connect to server first.")

        allmsgs_req = json.dumps({
            "token": self.profile.token,
            "directmessage": "all"
        })
        try:
            self.join_req(allmsgs_req)
            receive = self.socket.makefile("r").readline().strip()
            response = dsp.extract_json(receive)
            messages = []
            if response.response_type == "ok" and response.messages:
                for msg in response.messages:
                    dm = DirectMessage()
                    if "from" in msg:
                        self.profile.add_msg({
                            "sender": msg["from"],
                            "message": msg["entry"],
                            "timestamp": msg["timestamp"]
                        })
                        dm.sender = msg["from"]
                    elif "recipient" in msg:
                        self.profile.add_msg({
                            "recipient": msg["recipient"],
                            "message": msg["entry"],
                            "timestamp": msg["timestamp"]
                        })
                        dm.sender = msg["recipient"]
                    dm.recipient = self.username
                    dm.message = msg["entry"]
                    dm.timestamp = msg["timestamp"]
                    messages.append(dm)
            return messages
        except (socket.error, json.JSONDecodeError) as err:
            print(f"Error retrieving all messages: {err}")
            self.close_connection()
            return []

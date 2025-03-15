# pylint: disable=invalid-name
"""
This module defines the Profile class, which manages user information required
to join an ICS 32 DSU server. It also includes custom exceptions and the Post
class for managing individual user posts.
"""

import json
import time
from pathlib import Path


class DsuFileError(Exception):
    """
    Custom exception raised when attempting to load or save Profile objects to
    the file system.
    """


class DsuProfileError(Exception):
    """
    Custom exception raised when attempting to deserialize a DSU file to a
    Profile object.
    """


class Post(dict):
    """
    The Post class manages individual user posts, providing a timestamp and
    entry property.
    """

    def __init__(self, entry: str = None, timestamp: float = 0):
        self._timestamp = timestamp
        self.set_entry(entry)
        dict.__init__(self, entry=self._entry, timestamp=self._timestamp)

    def set_entry(self, entry):
        """Set the entry content of the post."""
        self._entry = entry
        dict.__setitem__(self, 'entry', entry)
        if self._timestamp == 0:
            self._timestamp = time.time()

    def get_entry(self):
        """Get the entry content of the post."""
        return self._entry

    def set_time(self, timestamp: float):
        """Set the timestamp of the post."""
        self._timestamp = timestamp
        dict.__setitem__(self, 'timestamp', timestamp)

    def get_time(self):
        """Get the timestamp of the post."""
        return self._timestamp

    entry = property(get_entry, set_entry)
    timestamp = property(get_time, set_time)


class Profile:
    """
    The Profile class manages user information required to join an ICS 32 DSU
    server.
    """

    def __init__(self, dsuserver=None, username=None, password=None,
                 token=None):
        """Initialize the Profile object."""
        self.dsuserver = dsuserver  # REQUIRED
        self.username = username  # REQUIRED
        self.password = password  # REQUIRED
        self.token = token
        self.recipients = []
        self.messages = []

    def save_messages(self, path: str):
        """
        Save messages to a DSU file.

        :param path: Path to the DSU file.
        :raises DsuFileError: If there is an error saving the messages.
        """
        p = Path("." + path)
        if p.suffix == '.dsu':
            try:
                with open(p, 'w', encoding='utf-8') as file:
                    json.dump(self.messages, file)
            except Exception as e:
                raise DsuFileError(f"Error saving messages: {e}") from e
        else:
            raise DsuFileError("Invalid File Type.")

    def load_messages(self, path: str):
        """
        Load messages from a DSU file.

        :param path: Path to the DSU file.
        :raises DsuFileError: If there is an error loading the messages.
        """
        p = Path("." + path)
        print(p.absolute())
        if p.suffix == '.dsu' and p.exists():
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    self.messages = json.load(f)
            except Exception as e:
                raise DsuFileError(f"Error loading messages: {e}") from e
        else:
            raise DsuFileError("Invalid file path or type.")

    def add_rec(self, recipient: str):
        """
        Add a recipient to the list of recipients.

        :param recipient: The recipient's username.
        """
        if recipient not in self.recipients:
            self.recipients.append(recipient)

    def add_msg(self, message: dict):
        """
        Add a message to the list of messages.

        :param message: The message to add.
        """
        self.messages.append(message)

    def save_profile(self, path: str, user_k: str) -> None:
        """
        Save the profile to a DSU file.

        :param path: Path to the DSU file.
        :param user_k: The user key to save the profile under.
        :raises DsuFileError: If there is an error saving the profile.
        """
        p = Path("." + path)

        if not p.exists():
            p.touch()
            with open(p, 'w', encoding='utf-8') as f:
                json.dump({}, f)

        if p.exists() and p.suffix == '.dsu':
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                data[user_k] = {
                    "dsuserver": self.dsuserver,
                    "username": self.username,
                    "password": self.password,
                    "token": self.token,
                    "recipients": self.recipients,
                    "messages": self.messages
                }
                with open(p, 'w', encoding='utf-8') as f:
                    json.dump(data, f)
            except Exception as ex:
                raise DsuFileError(
                    "Error while attempting to process the DSU file.", ex
                ) from ex

    def load_profile(self, path: str, user_k: str) -> None:
        """
        Load the profile from a DSU file.

        :param path: Path to the DSU file.
        :param user_k: The user key to load the profile from.
        :raises DsuProfileError: If there is an error loading the profile.
        :raises DsuFileError: If the file is invalid or does not exist.
        """
        p = Path('.' + path)

        if p.exists() and p.suffix == '.dsu':
            try:
                with open(p, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if user_k in data:
                    udt = data[user_k]
                    self.username = udt['username']
                    self.password = udt['password']
                    self.dsuserver = udt['dsuserver']
                    self.token = udt['token']
                    self.recipients = udt['recipients']
                    self.messages = udt['messages']
            except Exception as ex:
                raise DsuProfileError(ex) from ex
        else:
            raise DsuFileError()

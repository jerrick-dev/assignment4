""" ds_protocol.py

# Starter code for assignment 3 in ICS 32 Programming
# with Software Libraries in Python

# Replace the following placeholders with your information.

# Jerrick Aguilar
# jerricka@uci.edu
# 66335000
"""
import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
DataTuple = namedtuple('DataTuple', ['response_type', 'token', 'message',
                                     'messages'])


def extract_json(json_msg: str) -> DataTuple:
    """
    Extracts and parses JSON data from a string.

    Args:
        json_msg (str): A JSON-formatted string.

    Returns:
        DataTuple: A namedtuple containing the extracted data.
    """
    try:
        json_obj = json.loads(json_msg)
        response = json_obj.get('response', {})
        response_type = response.get('type')
        token = response.get('token')

        message = None
        messages = None

        if response_type == 'ok':
            if 'message' in response:
                message = response['message']
            elif 'messages' in response:
                messages = response['messages']

        return DataTuple(response_type, token, message, messages)

    except json.JSONDecodeError:
        print("JSON cannot be decoded.")
        return None

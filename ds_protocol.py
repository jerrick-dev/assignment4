# ds_protocol.py

# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Jerrick Aguilar
# jerricka@uci.edu
# 66335000

import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
DataTuple = namedtuple('DataTuple', ['type','token','message','messages'])

def extract_json(json_msg:str) -> DataTuple:
  try:
    json_obj = json.loads(json_msg)
    response = json_obj.get('response',{})
    type = response.get('type')
    token = response.get('token')

    message = None
    messages = None

    if type == 'ok':
      if 'message' in response:
        message = response['message']
      
      elif 'messages' in response:
        messages = response['messages']

    return DataTuple(type, token, message, messages)
  
  except json.JSONDecodeError:
    print("Json cannot be decoded.")
    return None
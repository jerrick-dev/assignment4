# ds_protocol.py

# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Jerrick Aguilar
# jerricka@uci.edu
# 66335000

import json
from collections import namedtuple

# Namedtuple to hold the values retrieved from json messages.
DataTuple = namedtuple('DataTuple', ['type','token'])

def extract_json(json_msg:str) -> DataTuple:
  try:
    json_obj = json.loads(json_msg)
    type = json_obj['response']['type']
    token = json_obj.get('token', None)

    msg = None
    msgs = None

    if type == 'ok':
      if 'message' in json_obj['response']:
        msg = json_obj['response']['message']
      
      elif 'messages' in json_obj['response']:
        msgs = json_obj['response']['messages']


    return DataTuple(type, token, msg, msgs)
  
  except json.JSONDecodeError:
    print("Json cannot be decoded.")
    return None
import socket
import time
import json
import ds_protocol as dsp

class DirectMessage:
  def __init__(self):
    self.recipient = None
    self.message = None
    self.timestamp = None


class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
    self.token = None
    self.dsuserver = dsuserver
    self.username = username
    self.password = password

  def connect(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
                client.connect((self.dsuserver, 3001))
                join = json.dumps({
                "join": {
                    "username": self.username,
                    "password": self.password,
                    "token": ""
                }
            })
                send_s = client.makefile("w")
                receive = client.makefile("r")
                send_s.write(join + "\r\n")
                send_s.flush()

                response = receive.readline().strip()
                p_resp = dsp.extract_json(response)
                
                if p_resp.type != "ok":
                    return False  
                
                self.token = json.loads(response)["response"]["token"] 

        except (socket.timeout, socket.error, json.JSONDecodeError) as e:
            print(f"Connection error: {e}")
        return False
		
  def send(self, message:str, recipient:str) -> bool:
#  dm = {
#                     "token": self.token,
#                     "directmessage": {
#                             "entry": message,
#                             "recipient": recipient,
#                             "timestamp": str(time.time())
#                         }
#                 }
		
  def retrieve_new(self) -> list:
    # must return a list of DirectMessage objects containing all new messages
    pass
 
  def retrieve_all(self) -> list:
    # must return a list of DirectMessage objects containing all messages
    pass
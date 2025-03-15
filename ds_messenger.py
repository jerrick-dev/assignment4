import socket
import time
import json
import ds_protocol as dsp
from Profile import Profile

class DirectMessage:
  def __init__(self):
    self.recipient = None
    self.message = None
    self.timestamp = None
    self.sender = None

class DirectMessenger:
  def __init__(self, dsuserver=None, username=None, password=None):
    self.token = None
    self.dsuserver = dsuserver
    self.username = username
    self.password = password
    self.socket = None 
    #for local storage
    self.profile = Profile(dsuserver,username,password)
    self.connect()

  
  def join_req(self,jsonobj):
    sendreq = self.socket.makefile("w")
    sendreq.write(jsonobj + "\r\n")
    sendreq.flush()  

  def connect(self):
    try:
      self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      self.socket.connect((self.profile.dsuserver, 3001))
      #join request
      join = json.dumps({
            "join": {
            "username": self.profile.username,
            "password": self.profile.password,
            "token": self.profile.token
              }
      })

      #join request to server
      self.join_req(join)

      #parse server response
      receive = self.socket.makefile("r").readline().strip()
      p_resp = dsp.extract_json(receive)

      if p_resp.type != "ok":
        raise ConnectionError("Failed to connect to server.") 
      
      self.profile.token = p_resp.token
      print(self.profile.token)

    except (socket.timeout, socket.error, json.JSONDecodeError) as e:
      print(f"Connection error: {e}")
      self.close_connection()
      raise
    
  def close_connection(self):
    #closes connection to server
    if self.socket:
      self.socket.close()
      self.socket = None

  def send(self, message:str, recipient:str) -> bool:
    if not self.profile.token:
      raise ValueError("Unauthenicated, connect to server first.")
  
    if not self.socket:
        print("Socket is not connected. Attempting to reconnect...")  # Debug: Reconnect attempt
        self.connect()
        if not self.socket:
            raise ConnectionError("Failed to reconnect to the server.")

    self.profile.add_rec(recipient)
    #direct message request
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
      receive = self.socket.makefile("r").readline().strip()
      response = dsp.extract_json(receive)
      if response.type == "ok" and response.message == "Direct message sent":
         #save locally
        self.profile.add_msg({
                  "type": "sent",
                  "recipient": recipient,
                  "message": message,
                  "timestamp": time.time()
        })
        return True
      return False
    except Exception as e:
      print(f"Error sending message: {e}")
      self.close_connection()
      return False

  def retrieve_new(self) -> list:
    # must return a list of DirectMessage objects containing all new messages
    if not self.profile.token:
      raise ValueError("Unauthenicated, connect to server first.") 
    
    newmsg_req = json.dumps({
      "token": self.profile.token,
      "directmessage":"new"
    })

    try:
      self.join_req(newmsg_req)
      receive = self.socket.makefile("r").readline().strip()
      response = dsp.extract_json(receive)
      messages = []
      if response.type == "ok" and response.messages:
        for msg in response.messages:
          self.profile.add_msg({
            "sender": msg["from"],
            "message": msg["message"],
            "timestamp": msg["timestamp"]
          })
          a = DirectMessage()
          a.sender = msg["from"]
          a.message = msg["message"]
          a.timestamp = msg["timestamp"]
          messages.append(a)
      return messages
    except Exception as e:
      print(f"Error retrieving new messages: {e}")
      self.close_connection()
      return False
    
  def retrieve_all(self) -> list:
    # must return a list of DirectMessage objects containing all messages
    if not self.profile.token:
      raise ValueError("Unauthenicated, connect to server first.") 
    
    allmsgs_req = json.dumps({
      "token":self.profile.token,
      "directmessage": "all"
    }) 
   
    try:
      self.join_req(allmsgs_req)
      receive = self.socket.makefile("r").readline().strip()
      response = dsp.extract_json(receive)
      messages = []
      if response.type == "ok" and response.messages:
            for msg in response.messages:
                if "from" in msg:
                    self.profile.add_msg({
                        "sender": msg["from"],
                        "message": msg["entry"],
                        "timestamp": msg["timestamp"]
                    }) 
                    a = DirectMessage()
                    a.recipient = self.username
                    a.sender=msg["from"],
                    a.message=msg["entry"],
                    a.timestamp=msg["timestamp"]
                    messages.append(a)
                elif "recipient" in msg:
                    # Message sent by the user
                    self.profile.add_msg({
                        "recipient": msg["recipient"],
                        "message": msg["entry"],
                        "timestamp": msg["timestamp"]
                    })
                    a = DirectMessage()
                    a.recipient = self.username
                    a.sender=msg["recipient"],
                    a.message=msg["entry"],
                    a.timestamp=msg["timestamp"]
                    messages.append(a)
      return messages
    
    except Exception as e:
        print(f"Error retrieving all messages: {e}")
        self.close_connection()
        return []
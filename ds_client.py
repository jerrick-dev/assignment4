# Starter code for assignment 3 in ICS 32 Programming with Software Libraries in Python

# Replace the following placeholders with your information.

# Jerrick Aguilar
# jerricka@uci.edu
# 66335000
import socket
import time
import json
import ds_protocol as dsp  # Assuming this is a module you're using for handling responses

def send(server: str, port: int, username: str, password: str, message: str, bio: str = None):
    '''
    The send function joins a DS server and sends a message, bio, or both.

    :param server: The IP address for the ICS 32 DS server.
    :param port: The port where the ICS 32 DS server is accepting connections.
    :param username: The user name to be assigned to the message.
    :param password: The password associated with the username.
    :param message: The message to be sent to the server.
    :param bio: Optional, a bio for the user.
    :return: True if the message was sent successfully, False otherwise.
    '''

    if not server or not username or not password:
        return False
    if message is not None and message.isspace():
        message = None
    if bio is not None and bio.isspace():
        bio = None

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((server, port))

            join = json.dumps({
                "join": {
                    "username": username,
                    "password": password,
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

            token = json.loads(response)["response"]["token"]

            if message:
                message_p = json.dumps({
                    "token": token,
                    "post": {
                        "entry": message,
                        "timestamp": str(time.time())
                    }
                })
                send_s.write(message_p + "\r\n")
                send_s.flush()
                receive.readline()  #read,discard response

            if bio:
                bio_p = json.dumps({
                    "token": token,
                    "bio": {
                        "entry": bio,
                        "timestamp": str(time.time())
                    }
                })
                send_s.write(bio_p + "\r\n")
                send_s.flush()
                receive.readline() #read, discard response

            return True 

    except (socket.timeout, socket.error, json.JSONDecodeError) as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error, try proper inputs!: {e}")

    return False
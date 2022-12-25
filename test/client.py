from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import *
import socket
import sys
import time

HEADER = 64
PORT = 8002
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "127.0.0.1"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print({ADDR})

def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length).encode(FORMAT)
    send_length += b' ' * (HEADER - len(send_length))
    client.send(send_length)
    client.send(message)
    print(client.recv(2048).decode(FORMAT))

def start():
     while True:
        send("Send Logon")
        time.sleep(1)


print("[STARTING] server is starting...")
start()

#send(DISCONNECT_MESSAGE)

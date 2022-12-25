from flask import Flask, url_for, send_from_directory,render_template, request
from flask_cors import CORS
import logging, os
import datetime
import csv
from datetime import date
import requests
import wget
import urllib
import random
import shutil
import uuid
import json
import socket
from bson.objectid import ObjectId
from bson import ObjectId

from random import choice
from string import digits
from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import *

import socket 
import threading
import random

import sys
from time import gmtime, strftime
import time
from datetime import datetime

HEADER = 64
PORT = 8001
SERVER = '127.0.0.1'
#SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
maxConn=100
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

#---------------Addional Data--------------
a = datetime.now()
mounth = int(a.strftime('%m'))
def concat(*args):
    string = ''
    for each in args:
        string += str(each)
    return int(string)
timeback=(time.strftime("%d%I%M%S", time.gmtime()))
gmt=int(''.join(str(x) for x in (mounth,timeback)))
code = list()
for i in range(6):
    code.append(choice(digits))
unique_id=''.join(code)
#---------------Addional Data--------------

def echotest(conn):
    print("Send Echo Test")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        conn.send(message)
        print ('Sending ... %s' % message)
        ans = conn.recv(2048)
        print ("\nResponse ASCII |%s|" % ans)
        isoAns = ISO8583()
        isoAns.setNetworkISO(ans)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
        if isoAns.getMTI() == '0810':
            print ("\tThat's great !!! The server understand my message !!!")
        else:
            print ("The server dosen't understand my message!")
    except InvalidIso8583, ii:
        print ii

def handle_client(conn, addr):
    print({addr})
    connected = True
    while connected:
        msg = conn.recv(2048)   
        print ("\nInput ASCII |%s|" % msg)
        print({SERVER})
        pack = ISO8583()
        try:
            pack.setNetworkISO(msg)
            v1 = pack.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
            if pack.getMTI() == '0800':
                print ("\tThat's great !!! The client send a correct message !!!")
            else:
                print ("The client dosen't send the correct message!")  
                break
        except InvalidIso8583, ii:
            print ii
            break
        except:
            print ('Something happened!!!!')
            break
        pack.setMTI('0810')
        ans = pack.getNetworkISO()
        print ('Sending answer %s' % ans)
        print(conn)
        conn.send(ans)
        #while(True):
         #   print("Looping...")
          #  echotest(conn)
           # time.sleep(10)
        #conn.send(ans)
        #n = random.randint(0,22)
        #send("Response Logon "+str(n))
        #print({msg_length})
        #conn.send("Msg received".encode(FORMAT))



app = Flask(__name__)
CORS(app)

PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/photo/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

HOST = '10.126.205.26'  # The server's hostname or IP address
PORT = 2502        # The port used by the server

@app.route('/')
def index():
    if request.method == "GET":
        return echotest()
    return("Data")


@app.route('/login', methods = ['POST'])
def login():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'001')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)

@app.route('/logout', methods = ['POST'])
def logout():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'002')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)

@app.route('/echo_test', methods = ['POST'])
def echo_test():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'301')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)

@app.route('/cut_over', methods = ['POST'])
def cut_over():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'201')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)


@app.route('/qr-payment-credit-request', methods = ['POST'])
def qr_payment_credit_request():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)


@app.route('/qr-payment-check-status', methods = ['POST'])
def qr_payment_check_status():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)


@app.route('/qr-refund-request', methods = ['POST'])
def qr_payment_refund_request():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)


@app.route('/qr-inquiry-mpan-request', methods = ['POST'])
def qr_inquiry_mpan_request():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)


@app.route('/qr-payment-debit-request', methods = ['POST'])
def qr_payment_debit_request():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)

@app.route('/qr-payment-debit-reversal-advice', methods = ['POST'])
def qr_payment_debit_reversal_advice_request():
    if request.method == "POST":
        details = request.json
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(b'0200')
            data = s.recv(1024)
        print('Received', repr(data))

    return(data)

def jsonDumps(get_data):
    return json.loads(json_util.dumps(get_data))





def start():
    server.listen(maxConn)
    if __name__ == '__main__':
         app.run(debug=False)
    #print({SERVER})
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        #print({SERVER})
        #print({threading.activeCount() - 1})

print("[STARTING] server is starting...")
start()



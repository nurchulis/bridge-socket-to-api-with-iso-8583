from flask import Flask, url_for, send_from_directory,render_template, request, jsonify
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

#-----For ISO8383 Library-----#
from random import choice
from string import digits
from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import *

#----For Socket Library------#
import socket 
import threading
import random
import sys
from time import gmtime, strftime
import time
from datetime import datetime
#----For Socket Library------#



#---Setup Connection Socket-----#
HEADER = 64
PORT = 8001
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '127.0.0.1'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
maxConn=100
DISCONNECT_MESSAGE = "!DISCONNECT"
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)
#---Setup Connection Socket-----#


#---------------Addional Data--------------
a = datetime.now()
mounth = int(a.strftime('%m'))
def concat(*args):
    string = ''
    for each in args:
        string += str(each)
    return int(string)
timeback=(time.strftime("%d%I%M%S", time.gmtime()))
print (timeback)
gmt=int(''.join(str(x) for x in (mounth,timeback)))
code = list()
for i in range(6):
    code.append(choice(digits))
unique_id=''.join(code)
#---------------Addional Data--------------

#------------------All Request----------------#
def logon():
    print("Send Logon Frist")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'001')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        ans = s.recv(2048)
        print ("\nResponse ASCII |%s|" % ans)
        isoAns = ISO8583()
        isoAns.setNetworkISO(ans)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
        if isoAns.getMTI() == '0810':
            print ("\tThat's great !!! The server understand my message !!!")
            status="success"
        else:
            print ("The server dosen't understand my message!")
            status="failed"
    except InvalidIso8583, ii:
        print ii
        status="failed"

    if(status=="success"):
        return jsonify(status='success',error=False,
            description=("Logon Request Success, Response Data = %s" % (ans)),data_iso=ans) 
    else:
        return ("Logon Request Failed, Response Data = %s" % (ans))

def log_out():
    print("Send Logon Frist")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(70,'002')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        ans = s.recv(2048)
        print ("\nResponse ASCII |%s|" % ans)
        isoAns = ISO8583()
        isoAns.setNetworkISO(ans)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
        if isoAns.getMTI() == '0810':
            print ("\tThat's great !!! The server understand my message !!!")
            status="success"
        else:
            print ("The server dosen't understand my message!")
            status="failed"
    except InvalidIso8583, ii:
        print ii
        status="failed"

    if(status=="success"):
        return jsonify(status='success',error=False,
            description=("Logoff Request Success, Response Data = %s" % (ans)),data_iso=ans) 
    else:
        return ("Logoff Request Failed, Response Data = %s" % (ans))


def echotest():
    print("Send Echo Test")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        ans = s.recv(2048)
        print ("\nResponse ASCII |%s|" % ans)
        isoAns = ISO8583()
        isoAns.setNetworkISO(ans)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
        if isoAns.getMTI() == '0810':
            print ("\tThat's great !!! The server understand my message !!!")
            status="success"
        else:
            print ("The server dosen't understand my message!")
            status="failed"
    except InvalidIso8583, ii:
        print ii
        status="failed"

    if(status=="success"):
        return jsonify(status='success',error=False,
            description=("Echo Test Request Success, Response Data = %s" % (ans)),data_iso=ans) 
    else:
        return ("Echo Test Request Failed, Response Data = %s" % (ans))
#------------------All Request----------------#



#------------------All Response----------------#
def echo_response():
    print("Send Echo Response")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(39,'00')
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
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
    return ("Response : %s" % ans)

def logon_response():
    print("Send Logon Response")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'001')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        #ans = s.recv(2048)
        #print ("\nResponse ASCII |%s|" % ans)
        #isoAns = ISO8583()
        #isoAns.setNetworkISO(ans)
        #v1 = isoAns.getBitsAndValues()
        #for v in v1:
            #print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
        #if isoAns.getMTI() == '0810':
            #print ("\tThat's great !!! The server understand my message !!!")
        #else:
            #print ("The server dosen't understand my message!")
    except InvalidIso8583, ii:
        print ii
#------------------All Response----------------#


def handle_client_incoming(msg):
        #print ("Koneksi masuk")
        print(pack.getMTI())
        print ("\nInput ASCII |%s|" % msg)
        pack = ISO8583()
        try:
            pack.setNetworkISO(msg)
            v1 = pack.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
            if pack.getMTI() == '0800':
                print ("\tThat's great !!! The client send a correct message !!!")
                pack.setMTI('0810')
                ans = pack.getNetworkISO()
                print ('Sending answer %s' % ans)
                s.send(ans)
            elif pack.getMTI() == '7081':
                print ("\tResponse :" % msg)
            else:
                print(pack.getMTI())
                print ("The client dosen't send the correct message!")  
        except InvalidIso8583, ii:
            print ii
        except:
            print ('Something happened!!!!')
        #conn.send(ans)
        #n = random.randint(0,22)
        #send("Response Logon "+str(n))3wswswesttg
        #conn.send("Msg received".encode(FORMAT))

#--------Main Connection-------#
def start():
    print ('Something happened!!!!')
    ini=0
    logon()
    while True:
         msg = s.recv(2048)  
         #print(msg.decode("utf-8"))
         handle_client_incoming(msg)
         #print("Disini")
#--------Main Connection-------#    



#-------Flask API run---------#
app = Flask(__name__)
CORS(app)

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8000        # The port used by the server

@app.route('/')
def index():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if request.method == "GET":
        return ("API Brige Rintis to Paprika Tester")

def authorized_check():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    if auth == '567f57b5a271ec56f4d9b46c91c14a95':
        return True
    else:
        return False


#------------------Endpoint For Network Spec--------------#
@app.route('/api/v1/network/login', methods = ['GET'])
def login():
    if(authorized_check()):
        return logon()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route('/api/v1/network/logoff', methods = ['GET'])
def logoff():
    if(authorized_check()):
        return log_out()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
    
@app.route('/api/v1/network/echo_test', methods = ['GET'])
def echo_test():
    if(authorized_check()):
        return echotest()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route('/api/v1/network/cut_over', methods = ['GET'])
def cutover():
    if(authorized_check()):
        return cutover()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route('/api/v1/network/network_status', methods = ['GET'])
def network_status():
    if(authorized_check()):
        return network_status()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
#------------------Endpoint For Network Spec--------------#

@app.route('/api/v1/payment/qr-payment-credit-request', methods = ['POST'])
def qr_payment_credit_request():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    #return(details["order_id"])


@app.route('/api/v1/payment/qr-payment-check-status', methods = ['POST'])
def qr_payment_check_status():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    return(details)


@app.route('/api/v1/payment/qr-refund-request', methods = ['POST'])
def qr_payment_refund_request():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    return(details)


@app.route('/api/v1/payment/qr-inquiry-mpan-request', methods = ['POST'])
def qr_inquiry_mpan_request():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    return(details)


@app.route('/api/v1/payment/qr-payment-debit-request', methods = ['POST'])
def qr_payment_debit_request():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    return(details)

@app.route('/api/v1/payment/qr-payment-debit-reversal-advice', methods = ['POST'])
def qr_payment_debit_reversal_advice_request():
    if request.method == "POST":
        details = request.json
        print('Received', repr(details))
    return(details)

def jsonDumps(get_data):
    return json.loads(json_util.dumps(get_data))

if __name__ == '__main__':
     app.run(host='127.0.0.1',port=4455,debug=True) 
#-------Flask API run---------#
	    	

#-------Main Connection Socket Start------#
print("[STARTING] server is starting...")
print(s.getsockname())
start()
#-------Main Connection Socket Start------#
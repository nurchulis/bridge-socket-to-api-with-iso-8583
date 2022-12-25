from flask import Flask, url_for, send_from_directory,render_template, request
from flask_cors import CORS
import logging, os

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

def logon(conn):
    print("Send Logon Frist")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'001')
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
            print ("\tThat's great !!! The server understand my message masuk!!!")
            status="success"
        else:
            print ("The server dosen't understand my message!")
            status="failed"
    except InvalidIso8583, ii:
        print ii
        status="failed"

    if(status=="success"):
        return ("Success")

    else:
        return ("Failed")

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

def cutover(conn,tracenumber):
    print("Send cutover request")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,tracenumber)
    iso.setBit(15,'0412')
    iso.setBit(70,'201')
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
            print ("\tThat's great !!! The server understand my message masuk!!!")
            status="success"
        else:
            print ("The server dosen't understand my message!")
            status="failed"
    except InvalidIso8583, ii:
        print ii
        status="failed"

    if(status=="success"):
        return ("Success")

    else:
        return ("Failed")


def echo_response(conn):
    print("Send Echo Response")
    iso = ISO8583()
    iso.setMTI('0810')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(39,'00')
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        conn.send(message)
        print ('Sending ... %s' % message)
        isoAns = ISO8583()
    except InvalidIso8583, ii:
        print ii
    return ("Response : Success")


def handle_client(conn, addr):
    print({addr})
    connected = True
    while connected:
        msg = conn.recv(2048)   
        print ("\nInput ASCII |%s|" % msg)
        print({SERVER})
        pack = ISO8583()
        tracenumber=""
        try:
            pack.setNetworkISO(msg)
            v1 = pack.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
                if v['bit']=="11":
                    tracenumber=v['value']
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
        echo_response(conn)
        while(True):
            print("Looping...")
            cutover(conn,tracenumber)
            time.sleep(10)
        #conn.send(ans)
        #n = random.randint(0,22)
        #send("Response Logon "+str(n))
        #print({msg_length})
        #conn.send("Msg received".encode(FORMAT))
        

def start():
    server.listen(maxConn)
    print({SERVER})
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print({SERVER})
        print({threading.activeCount() - 1})


print("[STARTING] server is starting...")
start()

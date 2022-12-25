from random import choice
from string import digits
from ISO8583.ISO8583 import ISO8583
from ISO8583.ISOErrors import *

import socket 
import threading
import random
import requests
import json

import sys
from time import gmtime, strftime
import time
from datetime import datetime

HEADER = 64
PORT = 2502
#SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '10.126.205.26'
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
maxConn=100
DISCONNECT_MESSAGE = "!DISCONNECT"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(ADDR)



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

def logon():
    print("Send Logon Frist")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    iso.setBit(48,'6011020112M003602')
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
        else:
            print ("The server dosen't understand my message!")
    except InvalidIso8183, ii:
        print ii

def echotest():
    print("Send Echo Test")
    iso = ISO8583()
    iso.setMTI('0810')
    iso.setBit(7,gmt)
    iso.setBit(11,unique_id)
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        ans = s.recv(1048)
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
        msg = conn.recv(1048)   
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
        conn.send(ans)
        #n = random.randint(0,22)
        #send("Response Logon "+str(n))
        #print({msg_length})
        #conn.send("Msg received".encode(FORMAT))

def handle_client_incoming(msg):
        print ("Koneksi masuk")
    msg_data=str(msg)
    d = {}
    d['data'] = msg_data
    data_msg=json.dumps(d)
    #data_msg=str(data_msg)
    headers = {"Content-type": "application/json", "Accept":"application/json","Client-Key":"226762e36d27b8c09b72bd1d522cac08"}
    url="https://apibeeop.jellytechno.com/api/v3/paprika/log"
    response=requests.post(url, data=data_msg, headers=headers)
    print(response)
        print ("\nIncomming message ASCII |%s|" % msg)
        pack = ISO8583()
        try:
            pack.setNetworkISO(msg)
            v1 = pack.getBitsAndValues()
            for v in v1:
                print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
            if pack.getMTI() == '0800':
        networkMIC=msg[-3:]
        if(networkMIC=='002'):
            print('Received Logon Request')
        elif(networkMIC=='001'):
            print('Received Echo Request')
                print ("\tThat's great !!! The client send a correct message !!!")
                pack.setMTI('0810')
                ans = pack.getNetworkISO()
                print ('Sending answer %s' % ans)
                s.send(ans)
            elif pack.getMTI() == '9710':
                print ('Response answer %s' % msg)
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

def start():
    ini=0
    logon()
    #echotest()
    while True:
         msg = s.recv(2048)  
         #wwprint(msg.decode("utf-8"))
         handle_client_incoming(msg)
         #print("Disini")
        

            
            

print("[STARTING] server is starting...")
print(s.getsockname())
start()

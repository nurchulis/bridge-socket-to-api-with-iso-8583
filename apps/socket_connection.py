from flask import Blueprint, render_template
import socket
from multiprocessing import Process, Queue
import threading
import requests
from threading import Lock
import json, ast
from config_iso import ISO8583, InvalidIso8583
import gevent

socket_connection = Blueprint('socket_connection', __name__)

#NMM-Response
from network.NNM import echo_response
from network.NNM import cutover_response
from network.NNM import logoff_response
from network.NNM import logon_response


#Handling Payment
from issuer.Payment import sendCallbackTransactions
from acquirer.Payment import sendIncommingRequestTransactions


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
print(ADDR)

payment_request="0"
inquiry_request="0"
network_data="0"
refund_request="0"
check_status_request="0"
#---Setup Connection Socket-----#

#---------------Response -----------------#
def get_response_qr_credit_request(msg):
    switcher = {
        "00": "Approved",
        "03": "Invalid Merchant, this RC can be used by acquirer if there is no longer business with the merchant.",
        "05": "Do not Honor",
        "12": "Invalid Transaction",
        "13": "Invalid Amount",
        "14": "Invalid PAN Number",
        "30": "Format Error",
        "51": "Insuficient funds",
        "57": "Transaction Not Permitted to Cardholder / QR is expired",
        "58": "Transaction Not Permitted to terminal",
        "59": "Suspected Fraud",
        "61": "Exceeds Transaction Amount Limit",
        "62": "Restricted Card",
        "65": "Exceeds Transaction Frequency Limit",
        "68": "Suspend Transaction",
        "90": "Cut Off in Progress",
        "91": "Link Down",
        "92": "Invalid Routing",
        "94": "Duplicate Transmission / Duplicate QR",
        "96": "System Malfunction"
    }
    return switcher.get(msg, "Invalid Status")
#---------------Response -----------------#



def handle_client_incoming(msg):
    print ("In Comming message")
    global network_data
    global payment_request
    global inquiry_request
    global refund_request
    global check_status_request
    print ("\nIncomming message ASCII |%s|" % msg)
    print(network_data)
    pack = ISO8583()
    unique_id=""
    system_trance_audit_number=""
    network_msg=""
    response_code=""
    additional_data_national=""
    invoice_number=""
    try:
        pack.setNetworkISO(msg)
        v1 = pack.getBitsAndValues()
        for v in v1:
            print (
                "Bit %s of type %s with value = %s" % (v["bit"], v["type"], v["value"])
            )
            if v['bit']=="11":
                unique_id=v['value']

            if v['bit']=="48":
                system_trance_audit_number=v['value']

            if v['bit']=="70":
                network_msg=v['value']

            if v['bit']=="15":
                settlement_date=v['value']

            if v['bit']=="39":
                response_code=v['value']

            if v['bit']=="57":
                additional_data_national=v['value']

            if v['bit']=="123":
                invoice_number=v['value']


        print (pack.getMTI())
        print (unique_id)
        d = {}
        d["tracenumber"] = unique_id
        d["nmic"] = network_msg
        d["response_code"] = response_code
        d["additional_data_national"] = additional_data_national  
        d["invoice_number"] = invoice_number        
        data_msg = json.dumps(d)

        if (pack.getMTI() == "0800"): # Network Request
            print (type(network_msg))
            print(str(network_msg))
            if network_msg == "001":
                print ("Received Logon Request")
                logon_response(unique_id,system_trance_audit_number)
            if network_msg == "002":
                print ("Received Logoff Request")
                logoff_response(unique_id)
            if network_msg == "301":
                print ("Received Echo Request")
                echo_response(unique_id,system_trance_audit_number)
            if network_msg == "201":
                print ("Received Cutover Request")
                cutover_response(settlement_date,unique_id)
            else:
                print ("Received Request ETC %s" % msg)
            
            print ("\tThat's great !!! The client send a correct message !!!")
        elif pack.getMTI() == "0210": # Response Transactions
            payment_request=data_msg
            inquiry_request=data_msg
            refund_request=data_msg
            check_status_request=data_msg
            #sendCallbackTransactions(msg) #Sudah tidak diperlukan 
            print ("In Comming Response Transaction %s" % msg)
        elif pack.getMTI() == "0200": # Request Transactions
            print ("In Comming Request Transaction %s" % msg)
            sendIncommingRequestTransactions(msg)
            #sendCallbackTransactions(msg) #Sudah tidak diperlukan 
        elif pack.getMTI() == "0810":
        	network_data=data_msg
        	print (system_trance_audit_number)
        	print ("In Comming.. %s" % msg)
        else:
            print (pack.getMTI())
            print ("The client dosen't send the correct message!")
    except InvalidIso8583, ii:
        print ii
    except:
        print ("Something happened!!!!")

@socket_connection.before_request
def task():
    queue = Queue()
    start_thread = threading.Thread(target=tasks, name="backgorund running")
    start_thread.start()


#--------Main Connection-------#

def tasks():
    print ('Something happened!!!!')
    #logon()
    while True:
        try:
            msg=s.recv(2046) 
            handle_client_incoming(msg)  
        except Exception as e:
            raise
        else:
            pass
        finally:
            pass

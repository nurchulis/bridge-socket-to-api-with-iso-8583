from flask import Flask, url_for, send_from_directory,render_template, request, jsonify
from flask_cors import CORS
import logging, os
import requests
import wget
import urllib
import gevent
import multiprocessing
from multiprocessing import Process, Queue
import gevent
import threading
import datetime
import pytz
from datetime import date, datetime,timedelta
from time import gmtime, strftime
import random
import shutil
import uuid
import json, ast
import socket
import time
from bson.objectid import ObjectId
from bson import ObjectId
from luhn import *

#-----For ISO8383 Library-----#
from random import choice
from string import digits
from lib_ISO_8583.ISO8583 import ISO8583
from lib_ISO_8583.ISOErrors import *


from extensions.socket_libary import *

app = Flask(__name__)

#---Setup Connection Socket-----#
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
print(ADDR)
set_api=1
network_data="0"
payment_request=""
inquiry_request="0"
#---Setup Connection Socket-----#


#---------------Addional Data--------------
a = datetime.now()
mounth = int(a.strftime('%m'))
def concat(*args):
    string = ''
    for each in args:
        string += str(each)
    return int(string)

timeback=(time.strftime("%H%M%S", time.gmtime()))
print (timeback)


gmt=datetime.utcnow().strftime("%m%d%H%M%S")
code = list()
for i in range(6):
    code.append(choice(digits))
unique_id=''.join(code)

def getracenumber():
    code = list()
    for i in range(6):
        code.append(choice(digits))
    unique_id=''.join(code) 
    return unique_id 

#---------------Addional Data--------------


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


def save_logs(msg):
    msg_data = str(msg)
    d = {}
    pack = ISO8583()
    pack.setNetworkISO(msg)
    v1 = pack.getBitsAndValues()
    network_msg=""
    response_code=""
    timetrace=""
    for v in v1:
        if v['bit']=="70":
            network_msg=v['value']
        if v['bit']=="39":
            response_code=v['value']
        if v['bit']=="11":
            timetrace=v['value']

    d["data_iso"] = msg_data
    d["mti"] = pack.getMTI()
    d["nmic"] = network_msg
    d["response_code"] = response_code
    d["timetrace"] = timetrace

    data_msg = json.dumps(d)
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }
    url = "http://api.jellytechno.com/api/save-log"
    response = requests.post(url, data=data_msg, headers=headers)
    print (response)


#------------------All Request----------------#
def logon():
    global network_data
    print("Send Logon Frist")
    iso = ISO8583()
    tracenumber=getracenumber()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,tracenumber)
    iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'001')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Logon... %s' % message)
        with gevent.iwait((network_data)) as it:
            while True:
                if network_data != "0":
                    get_request=json.loads(network_data)
                    if (get_request["tracenumber"]==tracenumber):
                        value = {
                            "tracenumber": get_request["tracenumber"],
                            "nmic": get_request["nmic"],
                            "response_code":get_request["response_code"]
                        }
                        return jsonify(status='waiting',error=False,
                        description=("Success Callback"), message_request=message,data=value) 
                        break
    except InvalidIso8583, ii:
        print ii

def log_out():
    print("Send Logon Frist")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,getracenumber())
    iso.setBit(70,'002')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        save_logs(message)
        print ('Sending Logout test... %s' % message)
        status="success"
    except InvalidIso8583, ii:
        print ii
        status="failed"
    if(status=="success"):
        return jsonify(status='success',error=False,
            description=("Logoff Request Success, Payload Data = %s" % (message)),data_iso=message) 
    else:
        return jsonify(status='success',error=False,
            description=("Logoff Request Failed, Payload Data = %s" % (message)),data_iso=message) 



def echotest():
    print("Send Echo Test")
    iso = ISO8583()
    iso.setMTI('0800')
    iso.setBit(7,gmt)
    iso.setBit(11,getracenumber())
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Echo test... %s' % message)
        status="success"
    except InvalidIso8583, ii:
        print ii
        status="failed"
    if(status=="success"):
        return jsonify(status='success',error=False,
            description=("Echo Request Success, Payload Data = %s" % (message)),data_iso=message) 

    else:
        return jsonify(status='success',error=False,
            description=("Echo Request Failed, Payload Data = %s" % (message)),data_iso=message) 

#------------------All Request----------------#


#------------------All Response----------------#
def echo_response(unique_id,system_trance_audit_number):
    print("Send Echo Response")
    pack = ISO8583()

    pack.setMTI('0810')
    pack.setBit(7,gmt)
    pack.setBit(11,unique_id)
    pack.setBit(39,'00')
    pack.setBit(70,'301')
    try:
        message = pack.getNetworkISO()
        s.send(message)
        print ('Sending Echo Response... %s' % message)
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

def logon_response(unique_id,system_trance_audit_number):
    print("Send Logon Response")
    pack = ISO8583()

    pack.setMTI('0810')
    pack.setBit(7,gmt)
    pack.setBit(11,unique_id)
    pack.setBit(39,'00')
    pack.setBit(48,system_trance_audit_number[3:])
    pack.setBit(70,'001')
    print (unique_id)
    print (system_trance_audit_number)
    try:
        msg = pack.getNetworkISO()
        s.send(msg)
        print ('Sending ... %s' % msg)
    except InvalidIso8583, ii:
        print ii

def logoff_response(unique_id):
    print("Send logoff Response")
    pack = ISO8583()

    pack.setMTI('0810')
    pack.setBit(7,gmt)
    pack.setBit(11,unique_id)
    pack.setBit(39,'00')
    pack.setBit(70,'002')
    try:
        message = pack.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
    except InvalidIso8583, ii:
        print ii

def cutover_response(settlement_date,unique_id):
    print("Send Cutover Response")
    pack = ISO8583()

    pack.setMTI('0810')
    pack.setBit(7,gmt)
    pack.setBit(11,unique_id)
    pack.setBit(15,settlement_date)
    pack.setBit(39,'00')
    pack.setBit(70,'201')
    try:
        message = pack.getNetworkISO()
        s.send(message)
        save_logs(message)
        print ('Sending ... %s' % message)
    except InvalidIso8583, ii:
        print ii

def sendCallbackTransactions(msg):
    msg_data = str(msg)
    d = {}
    pack = ISO8583()
    pack.setNetworkISO(msg)
    v1 = pack.getBitsAndValues()
    network_msg=""
    response_code=""
    timetrace=""
    invoice_number=""
    approval_code=""
    type_callback=""

    pan=""
    processing_code=""
    amount=""
    transmision_date_and_time=""
    local_transaction_time=""
    local_transaction_date=""
    settlement_date=""
    capture_date=""
    merchant_type=""
    point_service_entry=""
    acquirer_institution=""
    retrieval_reference_number=""
    card_acceptor_terminal_identification=""
    card_acceptor_id=""
    card_acceptor_name_location=""
    additional_data=""
    additional_data_national=""
    account_identification=""
    for v in v1:
        if v['bit']=="123":
            invoice_number=v['value']
        if v['bit']=="39":
            response_code=v['value']
        if v['bit']=="11":
            timetrace=v['value']
        if v['bit']=="38":
            approval_code=v['value']
        if v['bit']=="3":
            if v['value']=="366000":
                type_callback="check_status"
            elif v['value']=="200060":
                type_callback="refund_request"
            elif v['value']=="201060":
                type_callback="refund_request"
            else:
                type_callback="credit_request"
        if v['bit']=="2":
            pan=v['value']
        if v['bit']=="3":
            processing_code=v['value']
        if v['bit']=="4":
            amount=v['value']
        if v['bit']=="7":
            transmision_date_and_time=v['value']
        if v['bit']=="12":
            local_transaction_time=v['value']
        if v['bit']=="13":
            local_transaction_date=v['value']
        if v['bit']=="15":
            settlement_date=v['value']
        if v['bit']=="17":
            capture_date=v['value']
        if v['bit']=="18":
            merchant_type=v['value']
        if v['bit']=="22":
            point_service_entry=v['value']
        if v['bit']=="32":
            acquirer_institution=v['value']
        if v['bit']=="33":
            forwarding_institution_id=v['value']
        if v['bit']=="37":
            retrieval_reference_number=v['value']
        if v['bit']=="41":
            card_acceptor_terminal_identification=v['value']
        if v['bit']=="42":
            card_acceptor_id=v['value']
        if v['bit']=="43":
            card_acceptor_name_location=v['value']
        if v['bit']=="48":
            additional_data=v['value']
        if v['bit']=="47":
            additional_data_national=v['value']
        if v['bit']=="100":
            issuer_id=v['value']
        if v['bit']=="102":
            account_identification=v['value']

    d["system_trace_audit_number"] = timetrace
    d["paid_by"] = "offus"
    d["response_code"] = response_code
    d["invoice_number"] = invoice_number
    d["approval_code"] = approval_code
    d["type"] = type_callback

    d["pan"] = pan
    d["processing_code"] = processing_code
    d["amount"] = amount
    d["transmision_date_and_time"] = transmision_date_and_time
    d["local_transaction_time"] = local_transaction_time
    d["local_transaction_date"] = local_transaction_date
    d["settlement_date"] = settlement_date
    d["capture_date"] = capture_date
    d["merchant_type"] = merchant_type
    d["point_service_entry"] = point_service_entry

    d["acquirer_institution"] = acquirer_institution
    d["forwarding_institution_id"] = forwarding_institution_id
    d["retrieval_reference_number"] = retrieval_reference_number
    d["card_acceptor_terminal_identification"] = card_acceptor_terminal_identification
    d["card_acceptor_id"] = card_acceptor_id

    d["card_acceptor_name_location"] = str(card_acceptor_name_location)
    d["additional_data"] = additional_data
    d["additional_data_national"] = additional_data_national
    d["issuer_id"] = issuer_id
    d["account_identification"] = account_identification

    data_msg = json.dumps(d)
    headers = {
        "Content-type": "application/json",
        "Accept": "application/json"
    }
    try:
        url = "https://devserver3.paprika.co.id/api/v2/qris/callbacks"
        url2 = "http://api.jellytechno.com/api/save-log-callback-transaction-payment-request"
        response = requests.post(url, data=data_msg, headers=headers)
        response2 = requests.post(url2, data=data_msg, headers=headers)
        #print(response)
        #print(data_msg)
        print("Success Callback")
        #Check If Refund Request
        getResponse = response.json()
        if(getResponse["is_refund"] == True):
            if(getResponse["refund"]=="success"):
                approval_code=approval_code
                status_refund="approved"
                qr_credit_refund_response_socket(data_msg,approval_code,status_refund)
                print("Refund Success")
            else:
                approval_code=approval_code
                status_refund="decline"
                print("Refund Decline")
                qr_credit_refund_response_socket(data_msg,approval_code,status_refund)

    except Exception as e:
        print(e)



def sendIncommingRequestTransactions(msg):
    print("Send Incomming Transaction To Backend Core")
    msg_data = str(msg)
    d = {}
    pack = ISO8583()
    pack.setNetworkISO(msg)
    v1 = pack.getBitsAndValues()
    try:    
        pan=""
        processing_code=""
        transaction_amount=""
        transmision_date_and_time=""
        system_trance_audit_number=""
        local_transaction_time=""
        local_transaction_date=""
        settlement_date=""
        capture_date=""
        merchant_type=""
        point_service_entry=""
        amount_fee=""
        acquirer_institution=""
        forwarding_institution_id=""
        retrieval_reference_number=""
        approval_code=""
        card_acceptor_terminal_identification=""
        card_acceptor_id=""
        card_acceptor_name_location=""
        additional_data=""
        transaction_currency_code=""
        additional_data_national=""
        issuer_id=""
        account_identification=""
        for v in v1:
            if v['bit']=="2":
                pan=v['value']
            if v['bit']=="3":
                processing_code=v['value']
            if v['bit']=="4":
                transaction_amount=v['value']
            if v['bit']=="7":
                transmision_date_and_time=v['value']
            if v['bit']=="11":
                system_trance_audit_number=v['value']
            if v['bit']=="12":
                local_transaction_time=v['value']
            if v['bit']=="13":
                local_transaction_date=v['value']
            if v['bit']=="15":
                settlement_date=v['value']
            if v['bit']=="17":
                capture_date=v['value']
            if v['bit']=="18":
                merchant_type=v['value']
            if v['bit']=="22":
                point_service_entry=v['value']
            if v['bit']=="28":
                amount_fee=v['value']
            if v['bit']=="32":
                acquirer_institution=v['value']
            if v['bit']=="33":
                forwarding_institution_id=v['value']
            if v['bit']=="37":
                retrieval_reference_number=v['value']
            if v['bit']=="38":
                approval_code=v['value']
            if v['bit']=="41":
                card_acceptor_terminal_identification=v['value']
            if v['bit']=="42":
                card_acceptor_id=v['value']
            if v['bit']=="43":
                card_acceptor_name_location=v['value']
            if v['bit']=="48":
                additional_data=v['value']
            if v['bit']=="57":
                additional_data_national=v['value']
            if v['bit']=="100":
                issuer_id=v['value']
            if v['bit']=="102":
                account_identification=v['value']

        d["pan"] = pan
        d["processing_code"] = processing_code
        d["transaction_amount"] = transaction_amount
        d["transmision_date_and_time"] = transmision_date_and_time
        d["system_trance_audit_number"] = system_trance_audit_number
        d["local_transaction_time"] = local_transaction_time

        d["local_transaction_date"] = local_transaction_date
        d["settlement_date"] = settlement_date
        d["capture_date"] =  capture_date
        d["merchant_type"] = merchant_type
        d["point_service_entry"] = point_service_entry
        d["amount_fee"] = amount_fee

        d["acquirer_institution"] = acquirer_institution
        d["forwarding_institution_id"] = forwarding_institution_id
        d["retrieval_reference_number"] =  retrieval_reference_number
        d["approval_code"] = approval_code
        d["card_acceptor_terminal_identification"] = card_acceptor_terminal_identification
        d["card_acceptor_id"] = card_acceptor_id

        d["card_acceptor_name_location"] = card_acceptor_name_location
        d["additional_data"] = additional_data
        d["additional_data_national"] =  additional_data_national
        d["issuer_id"] = issuer_id
        d["account_identification"] = account_identification

        data_msg = json.dumps(d)
        headers = {
            "Content-type": "application/json",
            "Accept": "application/json"
        }
        print(data_msg)
        
        url = "https://devserver3.paprika.co.id/api/v2/qris/acquirers"
        requests_incomming = requests.post(url, data=data_msg, headers=headers)
        print(requests_incomming)
        print ("Send Transaction Request Incomming")
        getResponse = requests_incomming.json()
        invoice_number=""
        if(getResponse["status"]=="success"):
            invoice_number=getResponse["data"]["qris_invoice_number"]
            response_code=getResponse["response_code"]
            qr_payment_credit_response_socket(data_msg,invoice_number,response_code)
            print("Transaction Success")
        else:
            invoice_number="00000"
            response_code=getResponse["response_code"]
            print("Transaction Failed")
            qr_payment_credit_response_socket(data_msg,invoice_number,response_code)
    except Exception as e:
        print(e)
#------------------All Response----------------#


def handle_client_incoming(msg):
    print ("In Comming message")
    global network_data
    global payment_request
    global inquiry_request
    print ("\nIncomming message ASCII |%s|" % msg)
    pack = ISO8583()
    unique_id=""
    system_trance_audit_number=""
    network_msg=""
    response_code=""
    additional_data_national=""
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

        print (pack.getMTI())
        print (unique_id)
        d = {}
        d["tracenumber"] = unique_id
        d["nmic"] = network_msg
        d["response_code"] = response_code
        d["additional_data_national"] = additional_data_national
        
        data_msg = json.dumps(d)
        network_data=data_msg
        if (pack.getMTI() == "0800"): # Network Request
            #networkMIC = msg[-4:]
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
            sendCallbackTransactions(msg)
            print ("In Comming Response Transaction %s" % msg)

        elif pack.getMTI() == "0200": # Request Transactions
            
            print ("In Comming Request Transaction %s" % msg)
            sendIncommingRequestTransactions(msg)
        elif pack.getMTI() == "0810":
            print (system_trance_audit_number)
            print ("In Comming.. %s" % msg)
        else:
            print (pack.getMTI())
            print ("The client dosen't send the correct message!")
    except InvalidIso8583, ii:
        print ii
    except:
        print ("Something happened!!!!")




def GenerateFillzero(data,count):
    return data.zfill(count)

#---------------Transaction---------------#
def qr_payment_credit_request_socket(get_request):
    global payment_request
    get_month=date.today().month
    get_day=date.today().day
    get_day_se=date.today().day
    get_day=GenerateFillzero(str(get_day),2)
    get_month=GenerateFillzero(str(get_month),2)
    localtime=get_month+get_day
    settlement_date=get_month+str(get_day_se+1)
    t = time.localtime()
    jakarta_time = pytz.timezone('Asia/Jakarta') 
    current_time = datetime.now(jakarta_time).strftime('%H%M%S')

    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Client
    iso.setBit(3,'266000')
    iso.setBit(4,str(GenerateFillzero(get_request["amount"],10)+'00'))
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,current_time) #Generate From Sistem
    iso.setBit(13,localtime) #Generate From Sistem
    #iso.setBit(15,settlement_date) #Generate From Sistem
    iso.setBit(17,localtime) #Generate From Sistem
    iso.setBit(18,get_request["merchant_type"]) 
    iso.setBit(22,'011')
    if get_request["fee_fix_tips"]:
        amount_fee=GenerateFillzero(str(get_request["fee_fix_tips"]),6)
        iso.setBit(28,'C'+amount_fee+'00')   
    elif get_request["fee_percent_tips"]:
        amount_fee=GenerateFillzero(str(get_request["fee_percent_tips"]),6)
        iso.setBit(28,'C'+amount_fee+'00') 
    else:
        print("No Fee")

    iso.setBit(32,get_request["nns_acquirer"]) 
    #iso.setBit(32,'00093600111') 
    iso.setBit(37,get_request["transaction_id"]) # Random
    #iso.setBit(38,get_request["authorization_identification_response"])
    iso.setBit(38,get_request["authorization_identification_response"])
    iso.setBit(41,get_request["card_acceptor_terminal_identification"]) #From Client
    iso.setBit(42,get_request["card_acceptor_id"]) #From Client
    iso.setBit(43,get_request["card_acceptor_name_location"]) #From Client
    iso.setBit(48,get_request["additional_data"]) #From Client

    iso.setBit(49,'360') #From Client
    iso.setBit(57,get_request["additional_data_national"]) #Generate From Sistem
    #iso.setBit(57,'6105125256234011900000000000000337470707RTE4743') #Generate From Sistem
    iso.setBit(100,'00093600823')
    iso.setBit(102,get_request["account_identification"])

    global approved
    tracenumber=get_request["system_trance_audit_number"]

    try:
        message = iso.getNetworkISO()
        s.send(message)
        save_logs(message)
        print ('Sending ... %s' % message)
        approved="success"
        status="success"
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        data=[]
        for v in v1:
            item = {v['bit']: v['value']}
            data.append(item)
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
    except InvalidIso8583, ii:
        print ii
        status="failed"
        approved="success"
    """
    with gevent.iwait((payment_request)) as it:
        while True:
            if payment_request != "0":
                get_request=json.loads(payment_request)
                if (get_request["tracenumber"]==tracenumber):
                    value = {
                        "tracenumber": get_request["tracenumber"],
                        "response_code":get_request["response_code"]
                    }
                    return jsonify(status='waiting',error=False,
                    description=("Payment Response"), message_request=message,data=value) 
                    break
    """
    if(status=="success"):
        if (approved=="success"):
            value = {
                "local_transaction_time": current_time,
                "local_transaction_date": localtime,
                "settlement_date":settlement_date,
                "capture_date":localtime,
                "point_service_entry":"011",
                "acquiring_institution_id":"000"+get_request["nns_acquirer"],
                "issuer_id":"00093600823",
                "approval_code":get_request["authorization_identification_response"]
            }
         
            return jsonify(status='waiting',error=False,
            description=("Waiting Callback"), message_request=message,data=value,iso_data=data) 
        else:
            return jsonify(status='failed',error=True,
            description=("Failed Request"), message_request=message)
    else:
        return jsonify(status='failed',error=True,
            description=("Failed Request"), message_request=message)  


#---------------Transaction---------------#
def qr_payment_credit_response_socket(get_request,invoice_number,response_code):
    get_request=json.loads(get_request)
    get_month=date.today().month
    get_day=date.today().day
    get_day_se=date.today().day
    get_day=GenerateFillzero(str(get_day),2)
    get_month=GenerateFillzero(str(get_month),2)
    localtime=get_month+get_day
    settlement_date=get_month+str(get_day_se+1)
    t = time.localtime()
    jakarta_time = pytz.timezone('Asia/Jakarta') 
    current_time = datetime.now(jakarta_time).strftime('%H%M%S')

    iso = ISO8583()
    iso.setMTI('0210')
    iso.setBit(2,get_request["pan"][2:]) #From Client
    iso.setBit(3,get_request["processing_code"])
    iso.setBit(4,get_request["transaction_amount"])
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,get_request["local_transaction_time"]) #Generate From Sistem
    iso.setBit(13,get_request["local_transaction_date"]) #Generate From Sistem
    iso.setBit(15,get_request["settlement_date"]) #Generate From Sistem
    iso.setBit(17,get_request["capture_date"]) #Generate From Sistem
    iso.setBit(18,get_request["merchant_type"]) 
    iso.setBit(22,get_request["point_service_entry"])
    if get_request["amount_fee"]:
        amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        iso.setBit(28,'C'+amount_fee+'00')   
    iso.setBit(32,get_request["acquirer_institution"]) 
    iso.setBit(37,get_request["retrieval_reference_number"]) # Random
    iso.setBit(38,get_request["approval_code"])
    iso.setBit(41,get_request["card_acceptor_terminal_identification"]) #From Client
    iso.setBit(39,response_code)
    iso.setBit(42,get_request["card_acceptor_id"]) #From Client
    iso.setBit(43,get_request["card_acceptor_name_location"]) #From Client
    iso.setBit(48,get_request["additional_data"]) #From Client

    iso.setBit(49,'360') #From Client
    #iso.setBit(57,'61051292062119CREATE QRIS REQUEST') #Generate From Sistem
    iso.setBit(100,get_request["issuer_id"])
    iso.setBit(102,get_request["account_identification"])
    iso.setBit(123,invoice_number)
    global description_status
    global approved

    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Transaction Response... %s' % message)
        approved="success"
        status="success"
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        data=[]
        for v in v1:
            item = {v['bit']: v['value']}
            data.append(item)
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
    except InvalidIso8583, ii:
        print ii
        status="failed"
        approved="success"
    if(status=="success"):
        if (approved=="success"):
            value = {
                "local_transaction_time": current_time,
                "local_transaction_date": localtime,
                "settlement_date":settlement_date,
                "capture_date":localtime,
                "point_service_entry":"031",
                "acquiring_institution_id":"00093600823",
                "issuer_id":"00093600823"
            }
         
            return jsonify(status='waiting',error=False,
            description=("Waiting Callback"), message_request=message,data=value,iso_data=data) 
        else:
            return jsonify(status='failed',error=True,
            description=("Failed Request"), message_request=message)
    else:
        return jsonify(status='failed',error=True,
            description=("Failed Request"), message_request=message)  



def qr_check_status_request_socket(get_request):
    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Credit Request
    iso.setBit(3,'366000')
    iso.setBit(4,str(GenerateFillzero(get_request["amount"],10)+'00'))
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,get_request['local_transaction_time']) #Generate From Sistem
    iso.setBit(13,get_request['local_transaction_date']) #From Credit Request
    #iso.setBit(15,get_request['settlement_date']) #From Credit Request
    iso.setBit(17,get_request['capture_date']) #From Credit Request
    iso.setBit(18,get_request["merchant_type"])  #From Credit Request
    iso.setBit(22,'011') #From Credit Request
    if get_request["amount_fee"]:
        amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        #iso.setBit(28,'C'+amount_fee+'00')  
    iso.setBit(32,get_request['acquiring_institution_id']) #From Credit Request
    #iso.setBit(33,'00000360002')
    iso.setBit(37,get_request["transaction_id"]) #From Credit Request
    iso.setBit(38,get_request['approval_code']) #From Credit Request
    iso.setBit(41,get_request["card_acceptor_terminal_identification"])  #From Credit Request
    iso.setBit(42,get_request["card_acceptor_id"])  #From Credit Request
    iso.setBit(43,get_request["card_acceptor_name_location"])  #From Credit Requestt
    iso.setBit(48,get_request["additional_data"])  #From Credit Request

    iso.setBit(49,'360')  #From Credit Request
    iso.setBit(57,get_request["additional_data_national"])  #From Credit Request
    iso.setBit(100,get_request["issuer_id"])  #From Credit Request
    iso.setBit(102,get_request["account_identification"])  #From Credit Request 
    global description_status
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        approved="success"
        status="success"
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
    except InvalidIso8583, ii:
        print ii
        status="failed"
        approved="success"
    if(status=="success"):
        if (approved=="success"):
            return jsonify(status='waiting',error=False,
            description=("Waiting Callback Check Status"), message_request=message) 
        else:
            return jsonify(status='failed',error=True,
            description=("Failed Request Check Status"), message_request=message)
    else:
        return jsonify(status='failed',error=True,
            description=("Failed Request Check Status"), message_request=message)  


def qr_credit_refund_request_socket(get_request):
    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Credit Request
    iso.setBit(3,'200060')
    iso.setBit(4,get_request["amount"]) #From Credit Request
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,get_request['local_transaction_time']) #Generate From Sistem
    iso.setBit(13,get_request['local_transaction_date']) #From Credit Request
    iso.setBit(15,get_request['settlement_date']) #From Credit Request
    iso.setBit(17,get_request['capture_date']) #From Credit Request
    iso.setBit(18,get_request["merchant_type"])  #From Credit Request
    iso.setBit(22,'011')
    if get_request["amount_fee"]:
        amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        #iso.setBit(28,'C'+amount_fee+'00')  
    iso.setBit(32,get_request['acquiring_institution_id']) #From Credit Request
    #iso.setBit(33,'00000360002')
    iso.setBit(37,get_request["transaction_id"]) #From Credit Request
    iso.setBit(38,get_request['approval_code']) #From Credit Request
    iso.setBit(41,get_request["card_acceptor_terminal_identification"])  #From Credit Request
    iso.setBit(42,get_request["card_acceptor_id"])  #From Credit Request
    iso.setBit(43,get_request["card_acceptor_name_location"])  #From Credit Requestt
    iso.setBit(48,get_request["additional_data"])  #From Credit Request

    iso.setBit(49,'360')  #From Credit Request
    iso.setBit(57,get_request["additional_data_national"])  #From Credit Request
    iso.setBit(100,get_request["issuer_id"])  #From Credit Request
    iso.setBit(102,get_request["account_identification"])  #From Credit Request
    iso.setBit(123,get_request["invoice_number"])  #From Credit Request
    global description_status
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending ... %s' % message)
        approved="success"
        status="success"
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
    except InvalidIso8583, ii:
        print ii
        status="failed"
        approved="success"
    if(status=="success"):
        if (approved=="success"):
            return jsonify(status='waiting',error=False,
            description=("Waiting Callback Refund"), message_request=message) 
        else:
            return jsonify(status='failed',error=True,
            description=("Failed Request Refund"), message_request=message)
    else:
        return jsonify(status='failed',error=True,
            description=("Failed Request Refund"), message_request=message)  


        if v['bit']=="2":
            pan=v['value']
        if v['bit']=="3":
            processing_code=v['value']
        if v['bit']=="4":
            amount=v['value']
        if v['bit']=="7":
            transmision_date_and_time=v['value']
        if v['bit']=="12":
            local_transaction_time=v['value']
        if v['bit']=="13":
            local_transaction_date=v['value']
        if v['bit']=="15":
            settlement_date=v['value']
        if v['bit']=="17":
            capture_date=v['value']
        if v['bit']=="18":
            merchant_type=v['value']
        if v['bit']=="22":
            point_service_entry=v['value']
        if v['bit']=="32":
            acquirer_institution=v['value']
        if v['bit']=="33":
            forwarding_institution_id=v['value']
        if v['bit']=="37":
            retrieval_reference_number=v['value']
        if v['bit']=="41":
            card_acceptor_terminal_identification=v['value']
        if v['bit']=="42":
            card_acceptor_id=v['value']
        if v['bit']=="43":
            card_acceptor_name_location=v['value']
        if v['bit']=="48":
            additional_data=v['value']
        if v['bit']=="47":
            additional_data_national=v['value']
        if v['bit']=="102":
            account_identification=v['value']


def qr_credit_refund_response_socket(msg,approval_code,status_refund):
    get_request=json.loads(msg)
    iso = ISO8583()
    iso.setMTI('0210')
    iso.setBit(2,get_request["pan"][2:]) #From Credit Request
    iso.setBit(3,'200060')
    iso.setBit(4,get_request["amount"]) #From Credit Request
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trace_audit_number"]) # Random & unique
    iso.setBit(12,get_request["local_transaction_time"]) #Generate From Sistem
    iso.setBit(13,get_request["local_transaction_date"]) #From Credit Request
    iso.setBit(15,get_request["settlement_date"]) #From Credit Request
    iso.setBit(17,get_request["capture_date"]) #From Credit Request
    iso.setBit(18,get_request["merchant_type"])  #From Credit Request
    iso.setBit(22,"011")
    iso.setBit(32,get_request["acquirer_institution"]) #From Credit Request
    iso.setBit(33,get_request["forwarding_institution_id"]) #From Credit Request
    iso.setBit(37,get_request["retrieval_reference_number"]) #From Credit Request
    iso.setBit(38,approval_code) #From Credit Request
    if(status_refund=="approved"):
        iso.setBit(39,"00") #From Credit Request
    else:
        iso.setBit(39,"12") #From Credit Request
    iso.setBit(41,get_request["card_acceptor_terminal_identification"])  #From Credit Request
    iso.setBit(42,get_request["card_acceptor_id"])  #From Credit Request
    iso.setBit(43,get_request["card_acceptor_name_location"])  #From Credit Requestt
    iso.setBit(48,get_request["additional_data"])  #From Credit Request
    iso.setBit(49,'360')  #From Credit Request
    iso.setBit(100,get_request["issuer_id"][2:])  #From Credit Request
    iso.setBit(102,get_request["account_identification"][2:])  #From Credit Request
    iso.setBit(123,get_request["invoice_number"][2:])  #From Credit Request
    global description_status
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Refund Response... %s' % message)
        approved="success"
        status="success"
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        for v in v1:
            print ('Bit %s of type %s with value = %s' % (v['bit'],v['type'],v['value']))
    except InvalidIso8583, ii:
        print ii


def qr_inquiry_request_socket(request_inquiry):
    get_request=json.loads(request_inquiry)
    global inquiry_request
    get_month=date.today().month
    get_day=date.today().day
    get_day=GenerateFillzero(str(get_day),2)
    get_month=GenerateFillzero(str(get_month),2)
    localtime=get_month+get_day
    t = time.localtime()
    jakarta_time = pytz.timezone('Asia/Jakarta') 
    current_time = datetime.now(jakarta_time).strftime('%H%M%S')
    
    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,'93600000'+get_request["nmid"]) #From Client
    iso.setBit(3,'376000')
    iso.setBit(4,str(GenerateFillzero(get_request["amount"],10)+'00'))
    iso.setBit(7,gmt) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,current_time) #Generate From Sistem
    iso.setBit(13,localtime) #Generate From Sistem
    iso.setBit(17,localtime) #Generate From Sistem
    iso.setBit(18,get_request["merchant_type"]) 
    iso.setBit(22,'011')
    if get_request["amount_fee"]:
        amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        #iso.setBit(28,'C'+amount_fee+'00')   
    iso.setBit(32,'00093600000') 
    iso.setBit(37,get_request["transaction_id"]) # Random
    iso.setBit(38,'492952')
    iso.setBit(41,get_request["card_acceptor_terminal_identification"]) #From Client
    iso.setBit(42,get_request["card_acceptor_id"]) #From Client
    iso.setBit(43,get_request["card_acceptor_name_location"]) #From Client
    iso.setBit(48,get_request["additional_data"]) #From Client

    iso.setBit(49,'360') #From Client
    iso.setBit(100,'00093600823')
    iso.setBit(102,get_request["account_identification"])
    tracenumber=get_request["system_trance_audit_number"]
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Inquiry... %s' % message)
        with gevent.iwait((inquiry_request)) as it:
            while True:
                if inquiry_request != "0":
                    get_request=json.loads(inquiry_request)
                    if (get_request["tracenumber"]==tracenumber):
                        value = {
                            "tracenumber": get_request["tracenumber"],
                            "response_code":get_request["response_code"]
                        }
                        additional_data_national=get_request["additional_data_national"]
                        return (additional_data_national)
                        break
    except InvalidIso8583, ii:
        print ii



#-------Flask API run---------#

CORS(app)

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 8000        # The port used by the server


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
    return logon()

@app.route('/api/v1/network/logoff', methods = ['GET'])
def logoff():
    if(authorized_check()):
        return log_out()
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401
    
@app.route('/api/v1/network/echo_test', methods = ['GET'])
def echo_test():
    return echotest()


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
        get_request = request.json
        return qr_payment_credit_request_socket(get_request)

@app.route('/api/v1/payment/qr-payment-credit-response', methods = ['POST'])
def qr_payment_credit_response():
    if request.method == "POST":
        get_request = request.json
        return qr_payment_credit_response_socket(get_request)



@app.route('/api/v1/payment/qr-payment-check-status', methods = ['POST'])
def qr_payment_check_status():
    if request.method == "POST":
        get_request = request.json
        return qr_check_status_request_socket(get_request)


@app.route('/api/v1/payment/qr-refund-request', methods = ['POST'])
def qr_payment_refund_request():
    if request.method == "POST":
        get_request = request.json
        return qr_credit_refund_request_socket(get_request)


@app.route('/api/v1/payment/qr-inquiry-mpan-request', methods = ['POST'])
def qr_inquiry_mpan_request():
    if request.method == "POST":
        get_request = request.json
        return qr_inquiry_request_socket(get_request)

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

 
@app.route('/api/v1/payment/qr-scan', methods = ['POST'])
def qr_scan_v2():
    if request.method == "POST":
        details = request.json
        type_qr=""
        pan=""
        add_lenght=0
        get_id_root_26=""
        try:
            print('Received', repr(details))
            if(details["qrcode"]):
                get_id_root_54=str(0)
                
                if(details["qrcode"][6:12]=="010211"):
                    type_qr="static"
                elif(details["qrcode"][6:12]=="010212"):
                    type_qr="dynamic"

                if_id_root_26=details["qrcode"][12:14]
                print(if_id_root_26)
                if(if_id_root_26=="26"):
                    lenght=20
                    get_lenght_id_root_26=details["qrcode"][18:20]
                    print(get_lenght_id_root_26)
                    get_id_root_26=details["qrcode"][20:20+int(get_lenght_id_root_26)]
                    print(get_id_root_26)
                    lenght=lenght+int(get_lenght_id_root_26)
                    print(lenght)
                    get_lenght_id_root_01=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_01)
                    get_id_root_01=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_01)+4]
                    lenght=lenght+int(get_lenght_id_root_01)+6
                    print(get_id_root_01)
                    print(lenght)
                    get_lenght_id_root_02=details["qrcode"][lenght:lenght+2]
                    print(get_lenght_id_root_02)
                    get_id_root_02=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_02)+2]
                    print(get_id_root_02)
                    lenght=lenght+int(get_lenght_id_root_02)+4
                    print(lenght)

                    get_lenght_id_root_03=details["qrcode"][lenght:lenght+2]
                    print(get_lenght_id_root_03)
                    get_id_root_03=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_03)+2]
                    print(get_id_root_03)

                    lenght=lenght+int(get_lenght_id_root_03)+2
                    print(lenght)
                    get_root_62_sub_07=get_id_root_02
                else:
                    lenght=12



                if_id_root_27=details["qrcode"][lenght:lenght+2]
                if(if_id_root_27=="27"):
                    get_lenght_id_root_27=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_27)
                    get_id_root_27=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_27)+4]
                    print(get_id_root_27)
                    lenght=lenght+int(get_lenght_id_root_27)+4

                if_id_root_28=details["qrcode"][lenght:lenght+2]
                if(if_id_root_28=="28"):
                    get_lenght_id_root_28=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_28)
                    get_id_root_28=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_28)+4]
                    print(get_id_root_28)
                    lenght=lenght+int(get_lenght_id_root_28)+4

                if_id_root_51=details["qrcode"][lenght:lenght+2]
                print(if_id_root_51)
                if(if_id_root_51=="51"):
                    get_lenght_id_root_51=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_51)
                    get_id_root_51=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_51)+4]
                    print(get_id_root_51)

                    lengt_id_root_51=lenght+10
                    get_data_id_root_51_02=details["qrcode"][lengt_id_root_51:lengt_id_root_51+2]
                    if(get_data_id_root_51_02=="02"):
                        print(get_data_id_root_51_02)
                        get_lenght_id_root_51_02=details["qrcode"][lengt_id_root_51+2:lengt_id_root_51+4]
                        print(get_lenght_id_root_51_02)
                        get_data_id_root_02_52=details["qrcode"][lengt_id_root_51+4:lengt_id_root_51+int(get_lenght_id_root_51_02)+4]
                        print(get_data_id_root_02_52)

                    lenght=lenght+int(get_lenght_id_root_51)+4



                get_lenght_id_root_52=details["qrcode"][lenght+2:lenght+4]
                print(get_lenght_id_root_52)
                get_id_root_52=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_52)+4]
                print(get_id_root_52)
                lenght=lenght+int(get_lenght_id_root_52)+6
                print(lenght)

                get_lenght_id_root_53=details["qrcode"][lenght:lenght+2]
                print(get_lenght_id_root_53)
                get_id_root_53=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_52)+1]
                print(get_id_root_53)
                lenght=lenght+int(get_lenght_id_root_53)+2
                print(lenght)

                if_id_root_54=details["qrcode"][lenght:lenght+2]
                if(if_id_root_54=="54"):
                    print(if_id_root_54)
                    get_lenght_id_root_54=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_54)
                    get_id_root_54=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_54)+4]
                    get_id_root_54 = get_id_root_54.split('.')[0]
                    print(get_id_root_54)
                    lenght=lenght+int(get_lenght_id_root_54)+4
                    print(lenght)

                if_id_root_55=details["qrcode"][lenght:lenght+2]
                if(if_id_root_55=="55"):
                    print(if_id_root_55)
                    get_lenght_id_root_55=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_55)
                    get_id_root_55=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_55)+4]
                    print(get_id_root_55)
                    lenght=lenght+int(get_lenght_id_root_55)+4
                    print(lenght)

                if_id_root_56=details["qrcode"][lenght:lenght+2]
                get_id_root_56=""
                if(if_id_root_56=="56"):
                    print(if_id_root_56)
                    get_lenght_id_root_56=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_56)
                    get_id_root_56=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_56)+4]
                    print(get_id_root_56)
                    lenght=lenght+int(get_lenght_id_root_56)+4
                    print(lenght)

                if_id_root_57=details["qrcode"][lenght:lenght+2]
                get_id_root_57=""
                if(if_id_root_57=="57"):
                    print(if_id_root_57)
                    get_lenght_id_root_57=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_57)
                    get_id_root_57=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_57)+4]
                    print(get_id_root_57)
                    lenght=lenght+int(get_lenght_id_root_57)+4
                    print(lenght)


                if_id_root_58=details["qrcode"][lenght:lenght+2]
                if(if_id_root_58=="58"):
                    print(if_id_root_58)
                    get_lenght_id_root_58=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_58)
                    get_id_root_58=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_58)+4]
                    print(get_id_root_58)
                    lenght=lenght+int(get_lenght_id_root_58)+4
                    print(lenght)

                if_id_root_59=details["qrcode"][lenght:lenght+2]
                if(if_id_root_59=="59"):
                    print(if_id_root_59)
                    get_lenght_id_root_59=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_59)
                    get_id_root_59=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_59)+4]
                    print(get_id_root_59)
                    lenght=lenght+int(get_lenght_id_root_59)+4
                    print(lenght)

                if_id_root_60=details["qrcode"][lenght:lenght+2]
                if(if_id_root_60=="60"):
                    print(if_id_root_60)
                    get_lenght_id_root_60=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_60)
                    get_id_root_60=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_60)+4]
                    print(get_id_root_60)
                    lenght=lenght+int(get_lenght_id_root_60)+4
                    print(lenght)                   

                if_id_root_61=details["qrcode"][lenght:lenght+2]
                if(if_id_root_61=="61"):
                    print(if_id_root_61)
                    get_lenght_id_root_61=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_61)
                    get_id_root_61=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_61)+4]
                    print(get_id_root_61)
                    lenght=lenght+int(get_lenght_id_root_61)+4
                    print(lenght)       


                if_id_root_55=details["qrcode"][lenght:lenght+2]
                if(if_id_root_55=="55"):
                    print(if_id_root_55)
                    get_lenght_id_root_55=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_55)
                    get_id_root_55=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_55)+4]
                    print(get_id_root_55)
                    lenght=lenght+int(get_lenght_id_root_55)+4
                    print(lenght)

                get_id_root_62=""
                if_id_root_62=details["qrcode"][lenght:lenght+2]
                if(if_id_root_62=="62"):
                    sub_07=0
                    print(if_id_root_62)
                    get_lenght_id_root_62=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_62)
                    get_id_root_62=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_62)+4]
                    get_id_root_62="62"+get_id_root_62
                    print(get_id_root_62)

                    lengt_id_root_62=lenght+4
                    get_id_root_62_sub_01=details["qrcode"][lengt_id_root_62:lengt_id_root_62+2]
                    if(get_id_root_62_sub_01=="01"):
                        print(get_id_root_62_sub_01)
                        get_lenght_root_62_sub_01=details["qrcode"][lengt_id_root_62+2:lengt_id_root_62+4]
                        print(get_lenght_root_62_sub_01)
                        get_root_62_sub_01=details["qrcode"][lengt_id_root_62+4:lengt_id_root_62+int(get_lenght_root_62_sub_01)+4]
                        print(get_root_62_sub_01)
                        lengt_id_root_62=lengt_id_root_62+int(get_lenght_root_62_sub_01)+4

                    get_id_root_62_sub_07=details["qrcode"][lengt_id_root_62:lengt_id_root_62+2]
                    if(get_id_root_62_sub_07=="07"):
                        print(get_id_root_62_sub_07)
                        get_lenght_root_62_sub_07=details["qrcode"][lengt_id_root_62+2:lengt_id_root_62+4]
                        print(get_lenght_root_62_sub_07)
                        get_root_62_sub_07=details["qrcode"][lengt_id_root_62+4:lengt_id_root_62+int(get_lenght_root_62_sub_07)+4]
                        print(get_root_62_sub_07)
                        sub_07=1

                    
                    if (sub_07==0):
                        print("DISINI")
                        get_root_62_sub_07=makeFillSpace(get_id_root_02,16)
                    else:
                        print(get_root_62_sub_07)
                        get_root_62_sub_07=makeFillSpace(get_root_62_sub_07,16)

                    lenght=lenght+int(get_lenght_id_root_62)+4
                    print(lenght)       
                    
                if_id_root_63=details["qrcode"][lenght:lenght+2]
                if(if_id_root_63=="63"):
                    print(if_id_root_63)
                    get_lenght_id_root_63=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_63)
                    get_id_root_63=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_63)+4]
                    print(get_id_root_63)
                    lenght=lenght+int(get_lenght_id_root_63)+4
                    print(lenght)      

                card_acceptor_name_location=makeFillSpace(get_id_root_59,25).ljust(3)+makeFillSpace(get_id_root_60,13)+"ID"

                if(if_id_root_26!="26"):
                    print("Inquiry Request")
                    d={}
                    d["transaction_id"] = details["request_number"]
                    d["system_trance_audit_number"] = details["system_trance_audit_number"]
                    #d["transaction_id"] = "283929"
                    #d["system_trance_audit_number"] = "838302"
                    d["nmid"] = get_data_id_root_02_52[-11:]
                    d["amount"] = get_id_root_54
                    d["amount_fee"] = ""
                    d["merchant_type"] = get_id_root_52
                    d["card_acceptor_terminal_identification"] = get_root_62_sub_07
                    d["card_acceptor_id"] = get_data_id_root_02_52
                    d["card_acceptor_name_location"] = card_acceptor_name_location
                    d["additional_data"] = "PI04IQ02"
                    d["account_identification"] = details["account_identification"]
                    d["additional_data_national"] = "6105"+get_id_root_61+get_id_root_62

                    request_inquiry = json.dumps(d)
                    get_inquiry_data=qr_inquiry_request_socket(request_inquiry)
                    """                  
                    if(get_inquiry_data=="000"):
                        message = {"message":"Invalid Format"}
                        return jsonify(code=400,message="Validation Failed", error=message), 400 
                    """
                    get_root_id_inquiry=get_inquiry_data[0:3]
                    lenght_inquiry=3
                    print(get_root_id_inquiry)
                    get_root_id_inquiry_26=get_inquiry_data[lenght_inquiry:lenght_inquiry+2]
                    if(get_root_id_inquiry_26=="26"):
                        print("26")
                        lenght_inquiry_26=lenght_inquiry+4

                        get_sub_id_inquiry_26_1=get_inquiry_data[lenght_inquiry_26:lenght_inquiry_26+2]
                        print(get_sub_id_inquiry_26_1)
                        if(get_sub_id_inquiry_26_1=="01"):
                            print("SIJI")
                            get_lenght_root_26_sub_01=get_inquiry_data[lenght_inquiry_26+2:lenght_inquiry_26+4]
                            print(get_lenght_root_26_sub_01)
                            get_root_26_sub_01_inquiry=get_inquiry_data[lenght_inquiry_26+4:lenght_inquiry_26+int(get_lenght_root_26_sub_01)+4]
                            print(get_root_26_sub_01_inquiry)
                            lenght_inquiry_26=lenght_inquiry_26+int(get_lenght_root_26_sub_01)+4

                        get_sub_id_inquiry_26_2=get_inquiry_data[lenght_inquiry_26:lenght_inquiry_26+2]
                        print(get_sub_id_inquiry_26_2)
                        if(get_sub_id_inquiry_26_2=="02"):
                            print("DUA")
                            get_lenght_root_26_sub_02=get_inquiry_data[lenght_inquiry_26+2:lenght_inquiry_26+4]
                            print(get_lenght_root_26_sub_02)
                            get_root_26_sub_02_inquiry=get_inquiry_data[lenght_inquiry_26+4:lenght_inquiry_26+int(get_lenght_root_26_sub_02)+4]
                            print(get_root_26_sub_02_inquiry)
                            lenght_inquiry_26=lenght_inquiry_26+int(get_lenght_root_26_sub_02)+4

                        get_sub_id_inquiry_26_3=get_inquiry_data[lenght_inquiry_26:lenght_inquiry_26+2]
                        print(get_sub_id_inquiry_26_3)
                        if(get_sub_id_inquiry_26_3=="03"):
                            print("TIGA")
                            get_lenght_root_26_sub_03=get_inquiry_data[lenght_inquiry_26+2:lenght_inquiry_26+4]
                            print(get_lenght_root_26_sub_03)
                            get_root_26_sub_03_inquiry=get_inquiry_data[lenght_inquiry_26+4:lenght_inquiry_26+int(get_lenght_root_26_sub_03)+4]
                            print(get_root_26_sub_03_inquiry)
                            

                    get_lenght_id_inquiry_26=get_inquiry_data[lenght_inquiry+2:lenght_inquiry+4]
                    print(get_lenght_id_inquiry_26)
                    lenght_inquiry=lenght_inquiry+int(get_lenght_id_inquiry_26)+4

                    get_root_id_inquiry_27=get_inquiry_data[lenght_inquiry:lenght_inquiry+2]
                    if(get_root_id_inquiry_27=="27"):
                        print("27")
                        lenght_inquiry_27=lenght_inquiry+4

                        get_sub_id_inquiry_27_1=get_inquiry_data[lenght_inquiry_27:lenght_inquiry_27+2]
                        print(get_sub_id_inquiry_27_1)
                        if(get_sub_id_inquiry_27_1=="01"):
                            print("SIJI 27")
                            get_lenght_root_27_sub_01=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_01)
                            get_root_27_sub_01_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_01)+4]
                            print(get_root_27_sub_01_inquiry)
                            lenght_inquiry_27=lenght_inquiry_27+int(get_lenght_root_27_sub_01)+4

                        get_sub_id_inquiry_27_2=get_inquiry_data[lenght_inquiry_27:lenght_inquiry_27+2]
                        print(get_sub_id_inquiry_27_2)
                        if(get_sub_id_inquiry_27_2=="02"):
                            print("DUA 27")
                            get_lenght_root_27_sub_02=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_02)
                            get_root_27_sub_02_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_02)+4]
                            print(get_root_27_sub_02_inquiry)
                            lenght_inquiry_27=lenght_inquiry_27+int(get_lenght_root_27_sub_02)+4

                        get_sub_id_inquiry_27_3=get_inquiry_data[lenght_inquiry_27:lenght_inquiry_27+2]
                        print(get_sub_id_inquiry_27_3)
                        if(get_sub_id_inquiry_27_3=="03"):
                            print("TIGA 27")
                            get_lenght_root_27_sub_03=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_03)
                            get_root_27_sub_03_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_03)+4]
                            print(get_root_27_sub_03_inquiry)
                    #Set If Inquiry
                    get_id_root_01=get_root_26_sub_01_inquiry
                    get_id_root_26=""
                    get_id_root_02=get_root_26_sub_02_inquiry
                    get_id_root_03=get_root_26_sub_03_inquiry


            value = {
                "type": type_qr,
                "pan": get_id_root_01+str(generate(get_id_root_01)), #Check
                "nns_acquirer": get_id_root_01[0:8],  #Check
                "amount":get_id_root_54,
                "merchant_name":get_id_root_59,
                "merchant_location":get_id_root_60,
                "acquirer":get_id_root_26, #Check
                "zip_code":get_id_root_61,
                "merchant_type":get_id_root_52,
                "card_acceptor_terminal_identification":get_root_62_sub_07,
                "card_acceptor_id":makeFillSpace(get_id_root_02,15), #Check
                "card_acceptor_name_location":card_acceptor_name_location,
                "additional_data_national":"6105"+get_id_root_61+get_id_root_62,
                "additional_data":"PI04Q001CD05BAGUSMC03"+get_id_root_03, #Check
                "additional_data_first":"PI04Q001CD",
                "additional_data_end":"MC03"+get_id_root_03, #Check
                "fee_fix_tips":get_id_root_56,
                "fee_percent_tips":get_id_root_57,
                "account_identification":"9360082300000056382"
            }
                 
            return jsonify(status='success',error=False, description=("Valid"), data=value) 
        except Exception as e:
            print (e)
            message = {"message":"Invalid Format"}
            return jsonify(code=400,message="Validation Failed", error=message), 400 

def jsonDumps(get_data):
    return json.loads(json_util.dumps(get_data))    

def makeFillSpace(data,n):
    count=len(data)
    if(count>n):
        get_space=count-n
        data=data[:-get_space]
    elif(count<n):
        get_space=n-count
    else:
        data=data
        get_space=0
    data=data.ljust(n)
    return (data)    


@app.route('/')
def index():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    queue = Queue()
    if request.method == "GET":
        return ("API Brige Rintis to Paprika Tester")


@app.before_first_request
def task():
    headers = request.headers
    auth = headers.get("X-Api-Key")
    queue = Queue()
    start_thread = threading.Thread(target=task, name="backgorund running")
    start_thread.start()
    if request.method == "GET":
        return ("API Brige Rintis to Paprika Tester")


#--------Main Connection-------#
def task():
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

    
#--------Main Connection-------#    

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=1337, debug=True)
    app.run(host='0.0.0.0', port=1337, debug=True, use_reloader=False, threaded=True)




#-------Main Connection Socket Start------#

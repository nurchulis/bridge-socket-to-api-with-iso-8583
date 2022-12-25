from flask import Blueprint, render_template, jsonify, request
from config_iso import ISO8583, choice, digits, gmt, get_gmtnow, InvalidIso8583
from time import gmtime, strftime
import time

from apps.module.getracenumber import getracenumber
import json, ast
import gevent
import requests
from luhn import *

import datetime
import pytz
from datetime import date, datetime,timedelta

##--Module---#
from apps.module.GenerateFillzero import GenerateFillzero

Acquirer = Blueprint('Acquirer', __name__)

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
        invoice_number=""
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
            if v['bit']=="123":
                invoice_number=v['value']

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
        d["invoice_number"] = invoice_number

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
            invoice_number="00000000000000000000"
            response_code=getResponse["response_code"]
            print("Transaction Failed")
            qr_payment_credit_response_socket(data_msg,invoice_number,response_code)
    except Exception as e:
        print(e)

#---------------Request---------------#
@Acquirer.route("/api/v1/payment/qr-refund-request",  methods=('GET', 'POST'))
def qr_credit_refund_request_socket():
    from apps.socket_connection import s
    get_request = request.json
    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Credit Request
    iso.setBit(3,get_request["processing_code"])
    iso.setBit(4,get_request["amount"]) #From Credit Request
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,get_request['local_transaction_time']) #Generate From Sistem
    iso.setBit(13,get_request['local_transaction_date']) #From Credit Request
    #iso.setBit(15,get_request['settlement_date']) #From Credit Request
    iso.setBit(17,get_request['capture_date']) #From Credit Request
    iso.setBit(18,get_request["merchant_type"])  #From Credit Request
    iso.setBit(22,'011')
    if get_request["amount_fee"]:
        #amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        iso.setBit(28,get_request["amount_fee"])  
    iso.setBit(32,get_request['acquiring_institution_id']) #From Credit Request
    #iso.setBit(33,'00000360002')
    iso.setBit(37,get_request["transaction_id"]) #From Credit Request
    #iso.setBit(38,get_request['approval_code']) #From Credit Request
    iso.setBit(41,get_request["card_acceptor_terminal_identification"])  #From Credit Request
    iso.setBit(42,get_request["card_acceptor_id"])  #From Credit Request
    iso.setBit(43,get_request["card_acceptor_name_location"])  #From Credit Requestt
    iso.setBit(48,get_request["additional_data"])  #From Credit Request

    iso.setBit(49,'360')  #From Credit Request
    #iso.setBit(57,get_request["additional_data_national"])  #From Credit Request
    iso.setBit(100,get_request["issuer_id"])  #From Credit Request
    iso.setBit(102,get_request["account_identification"])  #From Credit Request
    iso.setBit(123,get_request["invoice_number"])  #From Credit Request
    global description_status
    tracenumber=get_request["system_trance_audit_number"]
    transaction_id=get_request["transaction_id"]
    invoice_number=get_request["invoice_number"]
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
        timeout = time.time() + 60   # 5 minutes from now
        while True:
            from apps.socket_connection import refund_request
            timer = 0
            if timer == 1 or time.time() > timeout:
            	return jsonify(status='failed',error=True,
                    description=("Timeout Response Refund")) 
                break
            timer = timer - 1
            if refund_request != "0":
                get_request=json.loads(refund_request)
                if (get_request["tracenumber"]==tracenumber):
                    value = {
                        "tracenumber": get_request["tracenumber"],
                        "response_code":get_request["response_code"],
                        "transaction_id":transaction_id,
                        "invoice_number":invoice_number
                    }
                    return jsonify(status='waiting',error=False,
                    description=("Refund Response"), message_request=message,data=value) 
                    break
    except InvalidIso8583, ii:
        print ii
 

#---------------Response---------------#
def qr_payment_credit_response_socket(get_request,invoice_number,response_code):
    from apps.socket_connection import s
#    time.sleep(60)
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
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
    iso.setBit(11,get_request["system_trance_audit_number"]) # Random & unique
    iso.setBit(12,get_request["local_transaction_time"]) #Generate From Sistem
    iso.setBit(13,get_request["local_transaction_date"]) #Generate From Sistem
    iso.setBit(15,get_request["settlement_date"]) #Generate From Sistem
    iso.setBit(17,get_request["capture_date"]) #Generate From Sistem
    iso.setBit(18,get_request["merchant_type"]) 
    iso.setBit(22,get_request["point_service_entry"])
    if get_request["amount_fee"]:
        #amount_fee=GenerateFillzero(get_request["amount_fee"],6)
        iso.setBit(28,get_request["amount_fee"])   
    iso.setBit(32,get_request["acquirer_institution"]) 
    iso.setBit(33,get_request["forwarding_institution_id"]) 
    iso.setBit(37,get_request["retrieval_reference_number"]) # Random
    iso.setBit(38,get_request["approval_code"])
    iso.setBit(41,get_request["card_acceptor_terminal_identification"]) #From Client
    iso.setBit(39,response_code)
    iso.setBit(42,get_request["card_acceptor_id"]) #From Client
    #iso.setBit(43,get_request["card_acceptor_name_location"]) #From Client
    iso.setBit(48,get_request["additional_data"]) #From Client

    iso.setBit(49,'360') #From Client
    #iso.setBit(57,'61051292062119CREATE QRIS REQUEST') #Generate From Sistem
    iso.setBit(100,get_request["issuer_id"])
    iso.setBit(102,get_request["account_identification"][2:])
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

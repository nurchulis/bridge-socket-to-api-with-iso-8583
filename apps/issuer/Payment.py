from flask import Blueprint, render_template, jsonify, request
from config_iso import ISO8583, choice, digits, gmt,get_gmtnow, InvalidIso8583
from time import gmtime, strftime
import time

from apps.module.getracenumber import getracenumber
import json, ast
import gevent
import requests
from luhn import *

##--Module---#
from apps.module.GenerateFillzero import GenerateFillzero

##--Function--#
from apps.module.Savelogs import save_logs

import datetime
import pytz
from datetime import date, datetime,timedelta

Issuer = Blueprint('Issuer', __name__)

#---------------Transaction---------------#
@Issuer.route("/api/v1/payment/qr-payment-credit-request", methods=('GET', 'POST'))
def qr_payment_credit_request_socket():
    from apps.socket_connection import s
    get_request = request.json

    get_month=date.today().month
    get_day=date.today().day
    get_day_se=GenerateFillzero(str(date.today().day+1),2)
    get_day=GenerateFillzero(str(get_day),2)
    get_month=GenerateFillzero(str(get_month),2)
    localtime=get_month+get_day
    settlement_date=get_month+get_day
    t = time.localtime()
    jakarta_time = pytz.timezone('Asia/Jakarta') 
    current_time = datetime.now(jakarta_time).strftime('%H%M%S')

    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Client
    iso.setBit(3,'266000')
    iso.setBit(4,str(GenerateFillzero(get_request["amount"],10)+'00'))
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
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
    elif get_request["input_tips"]==1:
        iso.setBit(28,'C00000000') 
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
    nns_acquirer=get_request["nns_acquirer"]
    authorization_identification_response=get_request["authorization_identification_response"]

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

    while True:
        from apps.socket_connection import payment_request
        if payment_request != "0":
            get_request=json.loads(payment_request)
            if (get_request["tracenumber"]==tracenumber):
                value = {
                    "tracenumber": get_request["tracenumber"],
                    "response_code":get_request["response_code"],
                    "invoice_number":get_request["invoice_number"],
                    "local_transaction_time": current_time,
                    "local_transaction_date": localtime,
                    "settlement_date":settlement_date,
                    "capture_date":localtime,
                    "point_service_entry":"011",
                    "acquiring_institution_id":"000"+nns_acquirer,
                    "issuer_id":"00093600823",
                    "approval_code":authorization_identification_response
                }
                return jsonify(status='waiting',error=False,
                description=("Payment Response"), message_request=message,data=value) 
                break

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

@Issuer.route("/api/v1/payment/qr-payment-check-status",  methods=('GET', 'POST'))
def qr_check_status_request_socket():
    from apps.socket_connection import s
    get_request = request.json

    iso = ISO8583()
    iso.setMTI('0200')
    iso.setBit(2,get_request["pan"]) #From Credit Request
    iso.setBit(3,'366000')
    iso.setBit(4,str(GenerateFillzero(get_request["amount"],10)+'00'))
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
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
    tracenumber=get_request["system_trance_audit_number"]
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

    while True:
        from apps.socket_connection import check_status_request
        if check_status_request != "0":
            get_request=json.loads(check_status_request)
            if (get_request["tracenumber"]==tracenumber):
                value = {
                    "tracenumber": get_request["tracenumber"],
                    "response_code":get_request["response_code"],
                    "invoice_number":get_request["invoice_number"]
                }
                return jsonify(status='waiting',error=False,
                description=("Payment Response"), message_request=message,data=value) 
                break

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
        if(processing_code != "206000"):
            url = "https://devserver3.paprika.co.id/api/v2/qris/callbacks"
            url2 = "http://api.jellytechno.com/api/save-log-callback-transaction-payment-request"
            response = requests.post(url, data=data_msg, headers=headers)
            response2 = requests.post(url2, data=data_msg, headers=headers)
            print(response)
            #print(data_msg)
            print("Success Callback")
            #Check If Refund Request
            getResponse = response.json()
            if(getResponse["is_refund"] == True):
                if(getResponse["refund"]=="success"):
                    approval_code=approval_code
                    status_refund="approved"
                    #qr_credit_refund_response_socket(data_msg,approval_code,status_refund)
                    print("Refund Success")
                else:
                    approval_code=approval_code
                    status_refund="decline"
                    print("Refund Decline")
                    #qr_credit_refund_response_socket(data_msg,approval_code,status_refund)
        else:
            print("Incomming Refund Response")
    except Exception as e:
        print(e)



def qr_credit_refund_response_socket(msg,approval_code,status_refund):
    from apps.socket_connection import s
    get_request=json.loads(msg)
    iso = ISO8583()
    iso.setMTI('0210')
    iso.setBit(2,get_request["pan"][2:]) #From Credit Request
    iso.setBit(3,'200060')
    iso.setBit(4,get_request["amount"]) #From Credit Request
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
    iso.setBit(11,get_request["system_trace_audit_number"]) # Random & unique
    iso.setBit(12,get_request["local_transaction_time"]) #Generate From Sistem
    iso.setBit(13,get_request["local_transaction_date"]) #From Credit Request
    #iso.setBit(15,get_request["settlement_date"]) #From Credit Request
    iso.setBit(17,get_request["capture_date"]) #From Credit Request
    iso.setBit(18,get_request["merchant_type"])  #From Credit Request
    iso.setBit(22,"011")
    iso.setBit(32,get_request["acquirer_institution"]) #From Credit Request
    iso.setBit(33,get_request["forwarding_institution_id"]) #From Credit Request
    iso.setBit(37,get_request["retrieval_reference_number"]) #From Credit Request
    #iso.setBit(38,approval_code) #From Credit Request
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

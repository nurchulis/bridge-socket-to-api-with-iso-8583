from flask import Blueprint, render_template, jsonify
from config_iso import ISO8583, choice, digits, gmt, get_gmtnow, InvalidIso8583
import datetime
from datetime import date, datetime,timedelta
from apps.module.getracenumber import getracenumber
import json, ast
import gevent

NNM = Blueprint('NNM', __name__)

from apps.module.Savelogs import save_logs


#----- Request------#
@NNM.route("/api/v1/network/login")
def logon_request():
    from apps.socket_connection import s, task
    print("Send Logon Frist")
    iso = ISO8583()
    tracenumber=getracenumber()
    iso.setMTI('0800')
    iso.setBit(7,get_gmtnow())
    iso.setBit(11,tracenumber)
    iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'001')

    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Logon... %s' % message)
        #with gevent.iwait((network_data)) as it:
        task()
        while True:
            from apps.socket_connection import network_data
            if network_data != "0":
                get_request=json.loads(network_data)
                if (get_request["tracenumber"]==tracenumber):

                    value = {
                        "tracenumber": get_request["tracenumber"],
                        "nmic": get_request["nmic"],
                        "response_code":get_request["response_code"]
                    }
                    return jsonify(status='waiting',error=False,
                    description=("Logon Response"), message_request=message,data=value) 
                    break
    except InvalidIso8583, ii:
        print ii

@NNM.route("/api/v1/network/logoff")
def log_out():
    from apps.socket_connection import s
    print("Send Logout...")
    iso = ISO8583()
    tracenumber=getracenumber()
    iso.setMTI('0800')
    iso.setBit(7,get_gmtnow())
    iso.setBit(11,tracenumber)
    iso.setBit(70,'002')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Logout... %s' % message)
        #with gevent.iwait((network_data)) as it:
        while True:
            from apps.socket_connection import network_data
            if network_data != "0":
                get_request=json.loads(network_data)
                if (get_request["tracenumber"]==tracenumber):
                    value = {
                        "tracenumber": get_request["tracenumber"],
                        "nmic": get_request["nmic"],
                        "response_code":get_request["response_code"]
                    }
                    return jsonify(status='waiting',error=False,
                    description=("Logoff Response"), message_request=message,data=value) 
                    break
    except InvalidIso8583, ii:
        print ii



@NNM.route("/api/v1/network/echo_test")
def echotest():
    from apps.socket_connection import s
    print("Send Echo Test")
    iso = ISO8583()
    tracenumber=getracenumber()
    iso.setMTI('0800')
    iso.setBit(7,datetime.utcnow().strftime("%m%d%H%M%S"))
    iso.setBit(11,tracenumber)
    #iso.setBit(48,'6011002112N003602')
    iso.setBit(70,'301')
    try:
        message = iso.getNetworkISO()
        s.send(message)
        print ('Sending Echo Test... %s' % message)
        #with gevent.iwait((network_data)) as it:
        save_logs(message)
        while True:
            from apps.socket_connection import network_data
            if network_data != "0":
                get_request=json.loads(network_data)
                if (get_request["tracenumber"]==tracenumber):
                    value = {
                        "tracenumber": get_request["tracenumber"],
                        "nmic": get_request["nmic"],
                        "response_code":get_request["response_code"]
                    }
                    return jsonify(status='waiting',error=False,
                    description=("Echo Response"), message_request=message,data=value) 
                    break
    except InvalidIso8583, ii:
        print ii

#----- Response------#
def echo_response(unique_id,system_trance_audit_number):
    print("Send Echo Response")
    from apps.socket_connection import s
    pack = ISO8583()
    pack.setMTI('0810')
    pack.setBit(7,get_gmtnow())
    pack.setBit(11,unique_id)
    pack.setBit(39,'00')
    pack.setBit(70,'301')
    try:
        message = pack.getNetworkISO()
        s.send(message)
        print ('Sending Echo Response... %s' % message)
        isoAns = ISO8583()
        isoAns.setNetworkISO(message)
        v1 = isoAns.getBitsAndValues()
        save_logs(message)
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
    from apps.socket_connection import s
    print("Send Logon Response")
    pack = ISO8583()
    pack.setMTI('0810')
    pack.setBit(7,get_gmtnow())
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
    from apps.socket_connection import s
    print("Send logoff Response")
    pack = ISO8583()
    pack.setMTI('0810')
    pack.setBit(7,get_gmtnow())
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
    from apps.socket_connection import s
    print("Send Cutover Response")
    try:
        pack = ISO8583()
        pack.setMTI('0810')
        pack.setBit(7,get_gmtnow())
        pack.setBit(11,unique_id)
        pack.setBit(15,settlement_date)
        pack.setBit(39,'00')
        pack.setBit(70,'201')
    
        message = pack.getNetworkISO()
        s.send(message)
        save_logs(message)
        print ('Sending ... %s' % message)
    except InvalidIso8583, ii:
        print ii


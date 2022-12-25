from flask import Blueprint, render_template, jsonify, request
from config_iso import ISO8583, choice, digits, gmt,get_gmtnow, InvalidIso8583
from time import gmtime, strftime
import time
from apps.socket_connection import s, task
from apps.module.getracenumber import getracenumber
import json, ast
import gevent
import requests
from luhn import *
import crcmod
#CRC Setting
crc16 = crcmod.mkCrcFun(0x11021, rev=False, initCrc=0xFFFF, xorOut=0x0000)

from apps.module.GenerateFillzero import GenerateFillzero

import datetime
import pytz
from datetime import date, datetime,timedelta

ScanQR = Blueprint('ScanQR', __name__)

@ScanQR.route("/api/v1/payment/qr-scan", methods=('GET', 'POST'))
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
                validation_crc=CheckCRC(details["qrcode"][:-4],details["qrcode"][-4:])
                if(validation_crc=="True"):
                    print ("Valid CRC")
                else:
                    message = {"message":"Invalid Format","description":validation_crc}
                    return jsonify(code=400,message="Validation Failed", error=message), 400 
                get_id_root_54=str(0)
                get_payload=details["qrcode"][0:6]
                print(get_payload)
                if(details["qrcode"][6:12]=="010211"):
                    type_qr="static"
                elif(details["qrcode"][6:12]=="010212"):
                    type_qr="dynamic"
                get_indicator_lenght=details["qrcode"][8:10]

                if_id_root_26=details["qrcode"][12:14]
                print(if_id_root_26)
                get_id_root_01=""
                get_id_root_02=""
                get_id_root_03=""
                get_id_51=""
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

                    get_root_62_sub_07=makeFillSpace(get_id_root_02,16)
                else:
                    lenght=12



                if_id_root_27=details["qrcode"][lenght:lenght+2]
                print(if_id_root_27)
                get_root_27_sub_01=""
                if(if_id_root_27=="27"):
                    get_lenght_id_root_27=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_27)
                    get_id_root_27=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_27)+4]
                    print(get_id_root_27)

                    lenght_id_root_27=lenght+4
                    get_id_root_27_sub_00=(details["qrcode"][lenght_id_root_27:lenght_id_root_27+2])
                    if(get_id_root_27_sub_00=="00"):
                        print(get_id_root_27_sub_00)
                        get_lenght_root_27_sub_00=details["qrcode"][lenght_id_root_27+2:lenght_id_root_27+4]
                        print(get_lenght_root_27_sub_00)
                        get_root_27_sub_00=details["qrcode"][lenght_id_root_27+4:lenght_id_root_27+int(get_lenght_root_27_sub_00)+4]
                        print(get_root_27_sub_00)
                        lenght_id_root_27=lenght_id_root_27+int(get_lenght_root_27_sub_00)+4
                        print(lenght_id_root_27)

                    
                    get_id_root_27_sub_01=details["qrcode"][lenght_id_root_27:lenght_id_root_27+2]
                    if(get_id_root_27_sub_01=="01"):
                        print(get_id_root_27_sub_01)
                        get_lenght_root_27_sub_01=details["qrcode"][lenght_id_root_27+2:lenght_id_root_27+4]
                        print(get_lenght_root_27_sub_01)
                        get_root_27_sub_01=details["qrcode"][lenght_id_root_27+4:lenght_id_root_27+int(get_lenght_root_27_sub_01)+4]
                        print(get_root_27_sub_01)
                        lenght_id_root_27=lenght_id_root_27+int(get_lenght_root_27_sub_01)+4
                        print(lenght_id_root_27)

                    get_id_root_27_sub_02=details["qrcode"][lenght_id_root_27:lenght_id_root_27+2]
                    if(get_id_root_27_sub_02=="02"):
                        print(get_id_root_27_sub_02)
                        get_lenght_root_27_sub_02=details["qrcode"][lenght_id_root_27+2:lenght_id_root_27+4]
                        print(get_lenght_root_27_sub_02)
                        get_root_27_sub_02=details["qrcode"][lenght_id_root_27+4:lenght_id_root_27+int(get_lenght_root_27_sub_02)+4]
                        print(get_root_27_sub_02)
                        lenght_id_root_27=lenght_id_root_27+int(get_lenght_root_27_sub_02)+4

                    get_id_root_27_sub_03=details["qrcode"][lenght_id_root_27:lenght_id_root_27+2]
                    if(get_id_root_27_sub_03=="03"):
                        print(get_id_root_27_sub_03)
                        get_lenght_root_27_sub_03=details["qrcode"][lenght_id_root_27+2:lenght_id_root_27+4]
                        print(get_lenght_root_27_sub_03)
                        get_root_27_sub_03=details["qrcode"][lenght_id_root_27+4:lenght_id_root_27+int(get_lenght_root_27_sub_03)+4]
                        print(get_root_27_sub_03)
                        lenght_id_root_27=lenght_id_root_27+int(get_lenght_root_27_sub_03)+4


                    print(details["qrcode"][lenght:lenght+2])
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
                    lengt_id_root_51=lenght+4
                    get_data_id_root_51_02=(details["qrcode"][lengt_id_root_51:lengt_id_root_51+2])
                    if(get_data_id_root_51_02=="00"):
                        print(get_data_id_root_51_02)
                        get_lenght_id_root_51_00=details["qrcode"][lengt_id_root_51+2:lengt_id_root_51+4]
                        print(get_lenght_id_root_51_00)
                        get_root_27_sub_00=details["qrcode"][lengt_id_root_51+4:lengt_id_root_51+int(get_lenght_id_root_51_00)+4]
                        print(get_root_27_sub_00)
                        lengt_id_root_51=lengt_id_root_51+int(get_lenght_id_root_51_00)+4
                        print(lengt_id_root_51)

                   
                    get_data_id_root_51_02=details["qrcode"][lengt_id_root_51:lengt_id_root_51+2]

                    print(get_data_id_root_51_02)
                    if(get_data_id_root_51_02=="02"):
                        print(get_data_id_root_51_02)
                        get_lenght_id_root_51_02=details["qrcode"][lengt_id_root_51+2:lengt_id_root_51+4]
                        print(get_lenght_id_root_51_02)
                        get_data_id_root_02_52=details["qrcode"][lengt_id_root_51+4:lengt_id_root_51+int(get_lenght_id_root_51_02)+4]
                        print(get_data_id_root_02_52)
                        get_id_51=get_data_id_root_02_52

                    lenght=lenght+int(get_lenght_id_root_51)+4



                get_lenght_id_root_52=details["qrcode"][lenght+2:lenght+4]
                print(get_lenght_id_root_52)
                get_id_root_52=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_52)+4]
                print(get_id_root_52)
                get_mcc=get_id_root_52
                lenght=lenght+int(get_lenght_id_root_52)+6
                print(lenght)

                get_lenght_id_root_53=details["qrcode"][lenght:lenght+2]
                print(get_lenght_id_root_53)
                get_id_root_53=details["qrcode"][lenght+2:lenght+int(get_lenght_id_root_52)+1]
                print(get_id_root_53)
                get_id=get_id_root_53
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
                input_tips=0
                if(if_id_root_55=="55"):
                    print(if_id_root_55)
                    get_lenght_id_root_55=details["qrcode"][lenght+2:lenght+4]
                    print(get_lenght_id_root_55)
                    get_id_root_55=details["qrcode"][lenght+4:lenght+int(get_lenght_id_root_55)+4]
                    print(get_id_root_55)
                    lenght=lenght+int(get_lenght_id_root_55)+4
                    print(lenght)
                    input_tips=1

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
                    get_merchant_name=get_id_root_59
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

                if(if_id_root_26!="26" and if_id_root_27!="27"):
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
                            print("One")
                            get_lenght_root_26_sub_01=get_inquiry_data[lenght_inquiry_26+2:lenght_inquiry_26+4]
                            print(get_lenght_root_26_sub_01)
                            get_root_26_sub_01_inquiry=get_inquiry_data[lenght_inquiry_26+4:lenght_inquiry_26+int(get_lenght_root_26_sub_01)+4]
                            print(get_root_26_sub_01_inquiry)
                            lenght_inquiry_26=lenght_inquiry_26+int(get_lenght_root_26_sub_01)+4

                        get_sub_id_inquiry_26_2=get_inquiry_data[lenght_inquiry_26:lenght_inquiry_26+2]
                        print(get_sub_id_inquiry_26_2)
                        if(get_sub_id_inquiry_26_2=="02"):
                            print("Two")
                            get_lenght_root_26_sub_02=get_inquiry_data[lenght_inquiry_26+2:lenght_inquiry_26+4]
                            print(get_lenght_root_26_sub_02)
                            get_root_26_sub_02_inquiry=get_inquiry_data[lenght_inquiry_26+4:lenght_inquiry_26+int(get_lenght_root_26_sub_02)+4]
                            print(get_root_26_sub_02_inquiry)
                            lenght_inquiry_26=lenght_inquiry_26+int(get_lenght_root_26_sub_02)+4

                        get_sub_id_inquiry_26_3=get_inquiry_data[lenght_inquiry_26:lenght_inquiry_26+2]
                        print(get_sub_id_inquiry_26_3)
                        if(get_sub_id_inquiry_26_3=="03"):
                            print("Three")
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
                            print("One 27")
                            get_lenght_root_27_sub_01=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_01)
                            get_root_27_sub_01_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_01)+4]
                            print(get_root_27_sub_01_inquiry)
                            lenght_inquiry_27=lenght_inquiry_27+int(get_lenght_root_27_sub_01)+4

                        get_sub_id_inquiry_27_2=get_inquiry_data[lenght_inquiry_27:lenght_inquiry_27+2]
                        print(get_sub_id_inquiry_27_2)
                        if(get_sub_id_inquiry_27_2=="02"):
                            print("Two 27")
                            get_lenght_root_27_sub_02=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_02)
                            get_root_27_sub_02_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_02)+4]
                            print(get_root_27_sub_02_inquiry)
                            lenght_inquiry_27=lenght_inquiry_27+int(get_lenght_root_27_sub_02)+4

                        get_sub_id_inquiry_27_3=get_inquiry_data[lenght_inquiry_27:lenght_inquiry_27+2]
                        print(get_sub_id_inquiry_27_3)
                        if(get_sub_id_inquiry_27_3=="03"):
                            print("Three 27")
                            get_lenght_root_27_sub_03=get_inquiry_data[lenght_inquiry_27+2:lenght_inquiry_27+4]
                            print(get_lenght_root_27_sub_03)
                            get_root_27_sub_03_inquiry=get_inquiry_data[lenght_inquiry_27+4:lenght_inquiry_27+int(get_lenght_root_27_sub_03)+4]
                            print(get_root_27_sub_03_inquiry)
                    #Set If Inquiry
                    get_id_root_01=get_root_26_sub_01_inquiry
                    get_id_root_26=""
                    get_id_root_02=get_root_26_sub_02_inquiry
                    get_id_root_03=get_root_26_sub_03_inquiry
                    
                    
            #IF DE 26 NOT FOUND
            if(get_id_root_01==""):
                get_id_root_01=get_root_27_sub_01
            if(get_id_root_02==""):
                get_id_root_02=get_root_27_sub_02
            if(get_id_root_03==""):
                get_id_root_03=get_root_27_sub_03
            if(get_id_root_26==""):
                get_id_root_26=get_root_27_sub_00

            #Get NNS If Paprika
            nns_acquirer=""
            if(get_root_27_sub_01[0:8]=="93600925"):
                nns_acquirer=get_root_27_sub_01[0:8]
                get_id_root_01=get_root_27_sub_01
            else:
                nns_acquirer=get_id_root_01[0:8]

            #Validation Scan QR
            check_validation = ValidationQR(get_payload,get_indicator_lenght,get_id_root_26,get_id_root_01,get_id_root_02,get_mcc,get_id,get_merchant_name,get_id_root_60,get_id_root_61,get_id_root_62)
            if(check_validation=="True"):
                print ("Valid QR")
            else:
                message = {"message":"Invalid Format","description":check_validation}
                return jsonify(code=400,message="Validation Failed", error=message), 400 


            value = {
                "type": type_qr,
                "pan": get_id_root_01+str(generate(get_id_root_01)), #Check
                "nns_acquirer": nns_acquirer,  #Check
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
                "account_identification":"9360082300000056382",
                "input_tips":input_tips,
                "id_51":get_id_51
            }
                 
            return jsonify(status='success',error=False, description=("Valid"), data=value) 
        except Exception as e:
            print (e)
            message = {"message":"Invalid Format"}
            return jsonify(code=400,message="Validation Failed", error=message), 400 

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

def CheckCRC(data_payload,crc):
    crc_data=hex(crc16(str(data_payload)))
    crc_string = crc.encode('ascii')
    crc_data_replace=crc_data[-4:].upper()
    crc_replace=crc_data.replace("x", "0")
    print("CRC",crc_replace.upper())
    print("CRC ..",crc_string[-4:])
    if(str(crc_replace.upper()[-4:])!=str(crc)):
        return ("Invalid CRC Data")
    return ("True")
        
def ValidationQR(get_payload,get_indicator_lenght,get_id_root_26,get_id_root_01,get_id_root_02,get_mcc,get_id,get_merchant_name,get_id_root_60,get_id_root_61,get_id_root_62):
    ##Check Payload Valid
    if(get_payload != "000201"):
        return ("Payload Not Match")

    ##Check Indicator Lenght Valid
    if(get_indicator_lenght != "02"):
        return ("lenght indicator not match")

    ##Check Domain Reserve Valid
    if(get_id_root_26[0:3]=="WWW"):
        return ("Domain is not reserve")

    ##Check MPAN is Valid
    if(get_id_root_01[0:4]=="9361"):
        return ("MPAN is not Valid")

    ##Check Lenght MPAN is Valid
    if(len(get_id_root_01)>=19):
        return ("MPAN include, check digiti and has maximum lenght")

    ##Check Lenght MID is Valid
    if(len(get_id_root_02)>15):
        return ("MID include, check digiti and has maximum lenght")

    if(len(get_mcc)>4):
        return ("MCC is not valid")

    if(get_id!="360"):
        return ("Not Use Rupiah")

    if(len(get_merchant_name)>25):
        return ("Merchant Name maximum character lenght")

    if(len(get_id_root_60)>15):
        return ("Merchant City maximum character 15 ")

    if(len(get_id_root_61)>10):
        return ("Merchant zip code maximum character 10")

    if(len(get_id_root_62[2:])<7):
        return ("ID 62 Not complete")


    return ("True")


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
    iso.setBit(7,get_gmtnow()) #Generate From Sistem
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
        #with gevent.iwait((inquiry_request)) as it:
        while True:
            from apps.socket_connection import inquiry_request
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
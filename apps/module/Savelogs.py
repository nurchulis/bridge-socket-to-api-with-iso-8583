from flask import Blueprint, render_template, jsonify, request
import json, ast
import requests
from config_iso import ISO8583, InvalidIso8583


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
   # url = "http://api.jellytechno.com/api/save-log"
   # response = requests.post(url, data=data_msg, headers=headers)
    #print (response)

from flask import Flask
import socket

#-----For ISO8383 Library-----#
from random import choice
from string import digits
from lib_ISO_8583.ISO8583 import ISO8583
from lib_ISO_8583.ISOErrors import *

from apps.network.NNM import NNM
from apps.issuer.ScanQR import ScanQR
from apps.issuer.Payment import Issuer
from apps.acquirer.Payment import Acquirer


def create_app():
	app = Flask(__name__)
	app.register_blueprint(NNM)
	app.register_blueprint(ScanQR)
	app.register_blueprint(Issuer)
	app.register_blueprint(Acquirer)
	return app

if __name__ == '__main__':
    create_app().run(host='0.0.0.0', port=1337, debug=True, use_reloader=False, threaded=True)
    #app.run
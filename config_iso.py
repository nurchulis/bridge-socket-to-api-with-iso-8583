from random import choice
from string import digits
from lib_ISO_8583.ISO8583 import ISO8583
from lib_ISO_8583.ISOErrors import *
import datetime
import pytz
from datetime import date, datetime,timedelta

def get_gmtnow():
	return datetime.utcnow().strftime("%m%d%H%M%S")
gmt=get_gmtnow()
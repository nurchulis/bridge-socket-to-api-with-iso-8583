import gevent
import gevent.server
import gevent.monkey
gevent.monkey.patch_all()

import socket
import string
import random
import filecmp
import os

"""
Example output:
$ python async-socket.py
new connection by ('127.0.0.1', 58020)
client got data!
client got data!
client data matches server
...forever
"""


HOST = '127.0.0.1'
PORT = 8001



def client():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    chunk_size = 512 * 1024  # how many bytes we want to process each loop
    while True:
        data = ''
        print 'client got data!'
        gevent.idle()
    s.close()




if __name__ == '__main__':
    # start client and wait
    c = gevent.spawn(client).join()
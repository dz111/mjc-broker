#!/usr/bin/env python

###############################################################################
# mjc-broker                                                                  #
# client.py                                                                   #
#                                                                             #
# (C) 2016 David Zhong                                                        #
#                                                                             #
# Permission is hereby granted, free of charge, to any person obtaining a     #
# copy of this software and associated documentation files (the "Software"),  #
# to deal in the Software without restriction, including without limitation   #
# the rights to use, copy, modify, merge, publish, distribute, sublicense,    #
# and/or sell copies of the Software, and to permit persons to whom the       #
# Software is furnished to do so, subject to the following conditions:        #
#                                                                             #
# The above copyright notice and this permission notice shall be included in  #
# all copies or substantial portions of the Software.                         #
#                                                                             #
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR  #
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,    #
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE #
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER      #
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING     #
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER         #
# DEALINGS IN THE SOFTWARE.                                                   #
###############################################################################

import asyncore
import json
import logging
import observable
import socket

usage = "usage: client.py <host> <port>"

class BrokerClient(asyncore.dispatcher_with_send, observable.Observable):
    def __init__(self, host, port):
        asyncore.dispatcher_with_send.__init__(self)
        observable.Observable.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addr = (host, port)
        self.buffer = ""
        self.name = None

    def send(self, data):
        asyncore.dispatcher_with_send.send(self, json.dumps(data))
        asyncore.dispatcher_with_send.send(self, "\r\n\r\n")

    def handle_read(self):
        self.buffer += self.recv(1024)
        packets = self.buffer.split("\r\n\r\n")
        self.buffer = packets[-1]
        [self.ProcessPDU(x) for x in packets[:-1]]

    def handle_close(self):
        self._sendMessage("status", "closed")
        self.close()

    def Connect(self):
        self.connect(self.addr)

    def DoRegister(self, name):
        if self.name is None:
            self.SendRegister(name)

    def DoRequestPair(self, name):
        if self.name is not None:
            self.SendPair(name)

    def ProcessPDU(self, packet):
        try:
            message = json.loads(packet)
        except ValueError:
            logging.warning("invalid packet: %s", packet)
            return
        try:
            typ = message["type"]
        except KeyError:
            logging.warning("invalid packet: %s", packet)
            return
        if typ == "fatal" or typ == "error":
            if "message" in message:
                err = message["message"]
            else:
                err = "no error specified"
            self._sendMessage(typ, err)
            if typ == "fatal":
                self.handle_close()
        elif typ == "pair":
            try:
                self._sendMessage("pair", (message["name"], message["address"], message["port"]))
            except KeyError:
                logging.error("problem with pair request: %s", packet)
        elif typ == "clients":
            try:
                self._sendMessage("clients", message["clients"])
            except KeyError:
                logging.error("problem with client list: %s", packet)
        elif typ == "registerok":
            try:
                self.name = message["name"]
            except KeyError:
                logging.error("problem with registerok: %s", packet)
            else:
                self._sendMessage("status", "registered")

    def SendRegister(self, name):
        packet = {
            "type": "register",
            "name": name
        }
        self.send(packet)

    def SendPair(self, name):
        packet = {
            "type": "pair",
            "respondent": name
        }
        self.send(packet)

def main():
    import sys
    import threading
    import traceback
    if len(sys.argv) < 3:
        print usage
        return
    HOST = sys.argv[1]
    try:
        PORT = int(sys.argv[2])
    except ValueError:
        print "invalid port"
        print usage
        return
    msg_queue = []
    def printfunc(s): print s
    client = BrokerClient(HOST, PORT)
    client.subscribe(lambda topic, message: printfunc("%s: %s" % (topic, message)))
    client.Connect()
    while True:
        x = raw_input("> ")
        if x:
            try:
                eval(x)
            except KeyboardInterrupt:
                return
            except:
                traceback.print_exc()
        asyncore.poll()

if __name__ == "__main__":
    main()

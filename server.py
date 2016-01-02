#!/usr/bin/env python

###############################################################################
# mjc-broker                                                                  #
# server.py                                                                   #
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
import random
import socket
import sys

usage = "usage: server.py <host> <port>"

class BrokerGeneralError(Exception): pass
class BrokerFatalError(Exception): pass

class BrokerHandler(asyncore.dispatcher_with_send):
    def __init__(self, sock, database):
        asyncore.dispatcher_with_send.__init__(self, sock)
        self.database = database
        self.name = None
        self.buffer = ""

    def send(self, data):
        asyncore.dispatcher_with_send.send(self, json.dumps(data))
        asyncore.dispatcher_with_send.send(self, "\r\n\r\n")

    def handle_read(self):
        self.buffer += self.recv(1024)
        packets = self.buffer.split("\r\n\r\n")
        self.buffer = packets[-1]
        [self.ProcessPDU(x) for x in packets[:-1]]

    def handle_close(self):
        if self.name is not None:
            self.database.RemoveClient(self.name)
        self.close()
        print "Closed connection from %s" % repr(self.addr)

    def GetAddress(self):
        return self.addr[0]

    def ProcessPDU(self, packet):
        try:
            message = json.loads(packet)
        except ValueError:
            return
        try:
            typ = message["type"]
        except KeyError:
            self.SendFatalError("packet did not contain a message type")
            return
        if typ == "register":
            action = self.ProcessRegister
        elif typ == "pair":
            action = self.ProcessPair
        else:
            self.SendFatalError("'%s' is not a valid message type" % typ)
            return
        try:
            action(message)
        except BrokerFatalError as e:
            self.SendFatalError(e.message)
            return
        except BrokerGeneralError as e:
            self.SendGeneralError(e.message)
            return

    def ProcessRegister(self, message):
        try:
            name = message["name"]
        except KeyError:
            raise BrokerFatalError("'register' packet must contain 'name'")
        self.name = name
        address = self.GetAddress()
        self.database.AddClient(name, address, self)
        self.SendRegisterOk()

    def ProcessPair(self, message):
        try:
            respondent = message["respondent"]
        except KeyError:
            raise BrokerFatalError("'pair' packet must contain 'respondent'")
        self.database.SendPairRequest(self.name, respondent)

    def SendFatalError(self, message):
        packet = {
            "type": "fatal",
            "message": message
        }
        self.send(packet)
        print "Fatal error from %s: %s" % (self.GetAddress(), message)
        self.handle_close()

    def SendGeneralError(self, message):
        packet = {
            "type": "error",
            "message": message
        }
        self.send(packet)

    def SendPairing(self, name, address, port):
        packet = {
            "type": "pair",
            "name": name,
            "address": address,
            "port": port
        }
        self.send(packet)

    def SendClientList(self, names):
        packet = {
            "type": "clients",
            "clients": names
        }
        self.send(packet)

    def SendRegisterOk(self):
        packet = {
            "type": "registerok",
            "name": self.name,
            "address": self.GetAddress()
        }
        self.send(packet)

class BrokerDatabase(object):
    def __init__(self):
        self.clients = {}

    def AddClient(self, name, address, handler):
        if name in self.clients:
            raise BrokerGeneralError("name already in use")
        self.clients[name] = (address, handler)
        self.RefreshClientList()

    def RemoveClient(self, name):
        if name in self.clients:
            del self.clients[name]
        self.RefreshClientList()

    def SendPairRequest(self, proponent, respondent):
        if proponent not in self.clients:
            raise BrokerFatalError("user not registered")
        if respondent not in self.clients:
            raise BrokerGeneralError("requested user no longer available")
        if respondent == proponent:
            raise BrokerGeneralError("cannot pair with self")
        r_address, r_handler = self.clients[respondent]
        p_address, p_handler = self.clients[proponent]
        p_port = r_port = random.randint(49200, 49300)
        while r_port == p_port:
            r_port = random.randint(49200, 49300)
        r_handler.SendPairing(proponent, p_address, p_port)
        p_handler.SendPairing(respondent, r_address, r_port)

    def RefreshClientList(self):
        client_names = self.clients.keys()
        [handler.SendClientList(client_names) for address, handler in self.clients.values()]

class BrokerServer(asyncore.dispatcher, BrokerDatabase):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        BrokerDatabase.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)
        print "Listening on %s:%d" % (host, port)

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            print "New connection from %s" % repr(addr)
            handler = BrokerHandler(sock, self)

def main():
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
    server = BrokerServer(HOST, PORT)
    asyncore.loop()

if __name__ == "__main__":
    main()


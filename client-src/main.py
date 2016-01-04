#!/usr/bin/env python

###############################################################################
# mjc-broker                                                                  #
# main.py                                                                     #
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
import subprocess
import wx
import sys

from client import BrokerClient
from version import TITLE, VERSION

class MainApp(wx.App):
    def OnInit(self):
        self.frame = AppFrame()
        self.frame.Show()
        return True

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title=TITLE + " - " + VERSION, size=(250,320))
        # Load config
        self.config = load_json("config.json")
        # Create panel elements
        self.panel = wx.Panel(self)
        wx.StaticText(self.panel, label="Name", pos=(5,5))
        wx.StaticText(self.panel, label="IP Addr", pos=(5,88))
        self.ctrl_name = wx.TextCtrl(self.panel, pos=(5,25), size=(230,-1))
        self.ctrl_ipaddr = wx.TextCtrl(self.panel, pos=(55,85), size=(180,-1), style=wx.TE_READONLY)
        self.ctrl_register = wx.Button(self.panel, pos=(5,55), label="Register")
        self.ctrl_pair = wx.Button(self.panel, pos=(5,245), label="Pair")
        self.ctrl_list = wx.ListBox(self.panel, pos=(5,115), size=(230,120), style=wx.LB_SINGLE)
        self.SetStatusBar(wx.StatusBar(self))
        # Set gui initial state
        self.ctrl_pair.Disable()
        self.SetStatusText("closed")
        # Bind element event handlers
        self.Bind(wx.EVT_BUTTON, lambda _: self.DoRegister(), self.ctrl_register)
        self.Bind(wx.EVT_BUTTON, lambda _: self.DoPair(), self.ctrl_pair)
        # Create client
        self.client = BrokerClient(self.config["server"]["address"], self.config["server"]["port"])
        self.client.subscribe(self.MessageHandler)
        self.client_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, lambda _: asyncore.poll(), self.client_timer)
        self.client_timer.Start(100)
        self.client.Connect()

    def MessageHandler(self, topic, message):
        if topic == "status":
            self.SetStatusText(message)
            if message == "registered":
                self.OnRegistered()
            else:
                self.OnDeregistered()
        elif topic == "address":
            self.SetIPAddress(message)
        elif topic == "clients":
            self.SetClientList(message)
        elif topic == "error":
            self.ShowError(message, False)
        elif topic == "fatal":
            self.ShowError(message, True)
        elif topic == "pair":
            self.ApplySettings(*message[1:])
            self.ShowPairResult(*message)

    def OnRegistered(self):
        self.ctrl_name.Disable()
        self.ctrl_register.Disable()
        self.ctrl_pair.Enable()

    def OnDeregistered(self):
        self.ctrl_name.Enable()
        self.ctrl_register.Enable()
        self.ctrl_pair.Disable()

    def SetIPAddress(self, addr):
        self.ctrl_ipaddr.SetValue(addr)

    def SetClientList(self, clients):
        self.ctrl_list.SetItems(clients)
        idx = self.ctrl_list.FindString(self.GetName())
        if idx >= 0:
            self.ctrl_list.Delete(idx)

    def ShowPairResult(self, name, local_port, remote_addr, remote_port):
        message = "Pairing with '%s'\nLocal port: %d\nRemote: %s:%d" % (name, local_port, remote_addr, remote_port)
        wx.MessageDialog(self, message=message, caption="Pairing Request", style=wx.OK|wx.ICON_INFORMATION).ShowModal()
        self.Close()

    def ShowWarning(self, message):
        wx.MessageDialog(self, message=message, caption="Warning", style=wx.OK|wx.ICON_WARNING).ShowModal()

    def ShowError(self, message, fatal):
        if fatal:
            caption = "Fatal Error"
        else:
            caption = "Error"
        wx.MessageDialog(self, message=message, caption=caption, style=wx.OK|wx.ICON_ERROR).ShowModal()
        if fatal:
            self.Close()

    def DoRegister(self):
        self.client.DoRegister(self.GetName())

    def DoPair(self):
        try:
            self.client.DoRequestPair(self.GetSelection())
        except IndexError:
            self.ShowWarning("Please select a partner")

    def ApplySettings(self, local_port, remote_addr, remote_port):
        pass

    def GetName(self):
        return self.ctrl_name.GetValue()

    def GetSelection(self):
        idx = self.ctrl_list.GetSelection()
        if idx < 0:
            raise IndexError("no selection has been made")
        return self.ctrl_list.GetString(idx)

def excepthook(etype, value, trace):
    with open("crash.log", "w") as fh:
        fh.write(''.join(traceback.format_exception(etype, value, trace)))
    sys.exit(1)

def load_json(filename):
    with open(filename) as fh:
        return json.load(fh)

def main():
    import logging
    logging.basicConfig(filename="mjc-broker.log", format="%(levelname)s:%(asctime)s:%(message)s")
    sys.excepthook = excepthook
    try:
        MainApp(redirect=True).MainLoop()
    except:
        logging.exception("fatal error")

if __name__ == "__main__":
    main()

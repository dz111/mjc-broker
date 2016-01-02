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

import wx

from client import BrokerClient

class MainApp(wx.App):
    def OnInit(self):
        self.frame = AppFrame()
        self.frame.Show()
        return True

class AppFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, parent=None, title="mjc-broker", size=(250,300))
        self.panel = wx.Panel(self)
        wx.StaticText(self.panel, label="Name", pos=(5,5))
        wx.StaticText(self.panel, label="IP Addr", pos=(5,88))
        self.ctrl_name = wx.TextCtrl(self.panel, pos=(5,25), size=(230,-1))
        self.ctrl_ipaddr = wx.TextCtrl(self.panel, pos=(55,85), size=(180,-1))
        self.ctrl_connect = wx.Button(self.panel, pos=(5,55), label="Connect")
        self.ctrl_pair = wx.Button(self.panel, pos=(5,245), label="Pair")
        self.ctrl_list = wx.ListBox(self.panel, pos=(5,115), size=(230,120), style=wx.LB_SINGLE)
        self.ctrl_pair.Disable()

def main():
    MainApp(redirect=False).MainLoop()

if __name__ == "__main__":
    main()

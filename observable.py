#!/usr/bin/env python

###############################################################################
# mjc-broker                                                                  #
# observable.py                                                               #
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

class Observable(object):
    def __init__(self):
        self.__subscribers = {None: []}

    def subscribe(self, handler, topic=None):
        assert(callable(handler))
        if topic not in self.__subscribers:
            self.__subscribers[topic] = []
        if handler not in self.__subscribers[topic]:
            self.__subscribers[topic].append(handler)

    def unsubscribe(self, handler, topic=None):
        if topic in self.__subscribers and handler in self.__subscribers[topic]:
            self.__subscribers[topic].remove(handler)

    def _sendMessage(self, topic, message):
        subscribers = [x for x in self.__subscribers[None]]
        if topic in self.__subscribers:
            [subscribers.append(x) for x in self.__subscribers[topic] if x not in subscribers]
        for handler in subscribers:
            try:
                import wx
                wx.CallAfter(handler, topic, message)
            except (NameError, AssertionError):
                handler(topic, message)

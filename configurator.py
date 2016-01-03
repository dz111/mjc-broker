#!/usr/bin/env python

###############################################################################
# mjc-broker                                                                  #
# configurator.py                                                             #
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

import ConfigParser
import os.path
import shutil
import _winreg as winreg

SimulatorRegistryPaths = [
    ("MSFSX", "Software\\Microsoft\\Microsoft Games\\Flight Simulator\\10.0"),
    ("P3Dv3", "Software\\Lockheed Martin\\Prepar3D v3"),
    ("P3Dv2", "Software\\Lockheed Martin\\Prepar3D v2"),
    ("P3Dv1", "Software\\Lockheed Martin\\Prepar3D"),
    ("FSXSE", "Software\\Microsoft\Microsoft Games\\Flight Simulator - Steam Edition\\10.0"),
]

def StripNullTerminated(s):
    idx = s.find("\0")
    if idx >= 0:
        return s[:idx]
    else:
        return s

def GetSimulator():
    sims = []
    for appname, regkey in SimulatorRegistryPaths:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, regkey)
        except WindowsError:
            continue
        try:
            path = winreg.QueryValueEx(key, "AppPath")[0]
        except WindowsError:
            continue
        path = StripNullTerminated(path)
        if os.path.isdir(path):
            sims.append((appname, path))
    return sims

def GetMJCPath(mjcrel="\\SimObjects\\Airplanes\\mjc8q400"):
    paths = []
    for sim, path in GetSimulator():
        mjcpath = path + mjcrel
        if os.path.isdir(mjcpath):
            paths.append((sim, mjcpath))
    return paths

def GetMJCIniPath(mjcroot=None, inirel="\\ini\\mjc84.ini"):
    if not mjcroot:
        mjcroot = GetMJCPath()[0][1]
    return mjcroot + inirel

def LoadConfig(path):
    config = ConfigParser.RawConfigParser()
    config.optionxform = str  # preserve case
    config.read(path)
    return config

def WriteConfig(config, path):
    with open(path, "w") as fh:
        config.write(fh)

def BackupFile(path, ext="bak", overwrite=True):
    backup_path = path + "." + ext
    if not os.path.isfile(path):
        raise IOError("No file at: '%s'" % path)
    if os.path.exists(backup_path) and not overwrite:
        return
    shutil.copyfile(path, backup_path)

def SetPairingData(local_port, remote_addr, remote_port, mjcroot=None):
    inipath = GetMJCIniPath(mjcroot)
    BackupFile(inipath, overwrite=False)
    config = LoadConfig(inipath)
    config.set("UDP_CONNECTOR_0", "UDP_BROADCAST_MASK", "%s:%d" % (remote_addr, remote_port))
    config.set("UDP_CONNECTOR_0", "UDP_RECEIVE_MASK", "0.0.0.0:%d" % local_port)
    WriteConfig(config, inipath)

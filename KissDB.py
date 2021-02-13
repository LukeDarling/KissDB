#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import sys, signal
from src.Daemon import *
from src.Config import *

daemon = Daemon.getInstance().start()

def signalHandler(signal, _):
    print("\r", end = "")
    daemon.stop()

signal.signal(signal.SIGINT, signalHandler)
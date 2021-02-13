#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import sys, signal
from src.Daemon import Daemon
from src.Logger import Logger

daemon = Daemon.getInstance().start()

def signalHandler(signal, _):
    print("\r", end = "")
    Logger.logNotice("Keyboard shutdown signal given.")
    daemon.stop()

signal.signal(signal.SIGINT, signalHandler)
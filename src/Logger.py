#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import datetime

class Logger:

    @classmethod
    def log(_, entry: str, color:str = None):
        """Takes a log entry and optional bash color code and prints it to standard output."""
        print("[" + datetime.datetime.now().strftime("%m/%d/%Y @ %I:%M:%S %p") + "] " + (("\033[" + color + "m") if not color == None else "") + entry + (("\u001b[0m") if not color == None else ""))

    @classmethod
    def logInfo(_, entry: str):
        """Takes an INFO log entry and prints it to standard output."""
        Logger.log("INFO: " + entry + "", color="1;37")

    @classmethod
    def logWarning(_, entry: str):
        """Takes a WARNING log entry and prints it to standard output."""
        Logger.log("WARNING: " + entry + "", color="0;33")

    @classmethod
    def logError(_, entry: str):
        """Takes an ERROR log entry and prints it to standard output."""
        Logger.log("ERROR: " + entry + "", color="0;31")

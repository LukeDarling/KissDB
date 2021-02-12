#!/usr/bin/env python3
# KissDB Database Daemon written by Luke Darling.
# All rights reserved.

# Imports
from __future__ import annotations
from typing import List
from src.Logger import Logger
from src.Constants import DEFAULT_CONFIG, ROOT_DIRECTORY, DATA_DIRECTORY, DB_DIRECTORY

class Daemon:

    def __init__(daemon):
        daemon.running = False

    def start(daemon, config: List) -> Daemon:

        Logger.logInfo("Starting KissDB Database Daemon...")

        # Main logic here

        daemon.running = True
        Logger.logInfo("KissDB Database Daemon started.")

        return daemon
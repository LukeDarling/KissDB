#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
from __future__ import annotations
import sys, os, socket, threading, time
from typing import List
from src.Logger import Logger
from src.Config import Config
from src.Request import Request
from src.Constants import DEFAULT_CONFIG, ROOT_DIRECTORY, DATA_DIRECTORY, DB_DIRECTORY

class Daemon:

    instance = None

    def __init__(daemon, config: List):
        daemon.running = False
        daemon.listener = None
        daemon.config = config
        Daemon.currentRequests = 0
        Daemon.instance = daemon



    def getInstance():

        if Daemon.instance == None:
            config = Config.load()
            if config == None:
                sys.exit(1)
            Daemon(config)

        return Daemon.instance



    def start(daemon) -> Daemon:

        Logger.logInfo("Starting KissDB daemon...")

        # Main logic here
        daemon.running = True
        Logger.logInfo("Checking database storage...")
        if not os.path.exists(DB_DIRECTORY):
            Logger.logWarning("Database storage not found.")
            try:
                os.mkdir(DB_DIRECTORY)
                Logger.logNotice("Database storage created.")
            except:
                Logger.logError("Could not create database storage.")
                daemon.stop()
        else:
            Logger.logInfo("Database storage found.")

        # Begin background threads
        #threading.Thread(target = journalingThread).start()
        #threading.Thread(target = cacheManagerThread).start()

        daemon.listener = threading.Thread(target = daemon.ListenerThread)
        daemon.listener.start()

        Logger.logInfo("KissDB daemon started.")

        dbCount = len(next(os.walk(DB_DIRECTORY))[1])
        Logger.logNotice("Handling " + "{:,}".format(dbCount) + " database" + ("." if dbCount == 1 else "s."))

        return daemon



    def stop(daemon, exitCode: int = 0):

        Logger.logInfo("Stopping KissDB daemon...")

        daemon.running = False

        # Stop listening for new requests
        if not daemon.listener == None:
            daemon.listener.join()

        # Wait for threads to finish
        lastRequestCount = Daemon.currentRequests + 1
        while Daemon.currentRequests > 0:
            if lastRequestCount > Daemon.currentRequests:
                Logger.logNotice("Waiting for " + str(Daemon.currentRequests) + " request" + ("" if Daemon.currentRequests == 1 else "s") + " to finish...")
                lastRequestCount = Daemon.currentRequests
            time.sleep(0.1)

        Logger.logInfo("KissDB daemon stopped.")



    def ListenerThread(daemon):

        # Prepare server
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(1)
            sock.bind(("127.0.0.1", daemon.config["server-bind-port"]))

            # Tell the server to begin listening and allow 128 backlogged requests in case of heavy server load (default maximum for Ubuntu)
            sock.listen(128)
            Logger.logInfo("Bound to 127.0.0.1:" + str(daemon.config["server-bind-port"]) + ".")
        except:
            Logger.logError("Could not bind to 127.0.0.1:" + str(daemon.config["server-bind-port"]) + ".")
            daemon.stop()
        
        while daemon.running:
            try:
                # Wait for request
                client, address = sock.accept()
                client.settimeout(daemon.config["request-timeout-seconds"])

                # Start a new thread to handle this client and go back to listening for requests
                Daemon.currentRequests += 1
                threading.Thread(target = daemon.RequestThread, args = (client, address)).start()
            except:
                pass

        Logger.logInfo("Unbound from 127.0.0.1:" + str(daemon.config["server-bind-port"]) + ".")



    def RequestThread(daemon, client: socket, address):
        Request(daemon, client, address)
        Daemon.currentRequests -= 1

#!/usr/bin/env python3

# Imports
import os, json, signal, datetime, fcntl

# Constants
CONFIG = {}

# Functions
def log(entry: str):
    print("[" + datetime.datetime.now().strftime("%b %d, %Y - %H:%M:%S") + "] " + entry)

def error(entry: str):
    log("\033[0;31mERROR: " + entry + "\033[0m")

def interrupt(_, __):
    print("\r" + (' ' * 128) + "\r", end="")
    signal.signal(signal.SIGINT, SIGINT)
    exitGracefully()

def exitGracefully():
    global running
    running = False
    log("Shutting down...")

# Setup
log("Starting server...")
running = True
SIGINT = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, interrupt)
log("Checking configuration...")
if not os.path.exists("data"):
    log("Configuration not found.")
    log("Creating configuration...")
    os.mkdir("data")
    os.mkdir("data/db")
    try:
        with open("data/config.json", "w") as f:
            json.dump(CONFIG, f)
        log("Configuration created!")
    except:
        error("Configuration could not be created.")
        log("Shutting down...")
        exit()
else:
    log("Configuration found!")

log("Loading configuration...")
try:
    with open("data/config.json", "r") as f:
        config = json.load(f)
    log("Configuration loaded!")
except:
    error("Configuration could not be loaded.")
    log("Shutting down...")
    exit()

log("Server successfully started.")
dbCount = len(next(os.walk("data/db/"))[1])
log("Handling " + str(dbCount) + " database" + ("." if dbCount == 1 else "s."))

while running:
    
    pass
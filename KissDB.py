#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, json, time, signal, datetime, fcntl, threading, socket


# Constants
CONFIG = {"bind-address":"127.0.0.1","bind-port":12345}

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

def encodeResponse(content: str):
    length = len(content.encode())
    # TODO: Testing, need to figure out exact/variable headers to send
    return ("HTTP/1.1 200 OK\r\nContent-type: application/json; charset=UTF-8\r\nContent-Length: " + str(length) + "\r\nConnection: closed\r\n\r\n" + content).encode()

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

def handleRequest(client, address):
    data = []
    while True:
        data.append(client.recv(1))
        if "\r\n\r\n" in b''.join(data).decode("UTF-8"):
            # Headers found
            break

    # TODO: To parse the request body, I need to get the Content-length header now

    client.send(encodeResponse("Hello, world!")) 
  
    client.close()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((config["bind-address"], config["bind-port"]))

# Tell the server to begin listening and allow 128 backlogged requests in case of heavy server load (default maximum for Ubuntu)
sock.listen(128)

while running:
    # Wait for request
    client, address = sock.accept()
    client.settimeout(60)
    # Start a new thread to handle this client and go back to listening for requests
    threading.Thread(target=handleRequest, args=(client, address)).start()
#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, json, time, signal, datetime, fcntl, threading, socket


# Constants
CONFIG = {"bind-address": "127.0.0.1","bind-port": 1700}

# Functions
def log(entry: str, color=None):
    print("[" + datetime.datetime.now().strftime("%m/%d/%Y @ %I:%M:%S %p") + "] " + (("\033[" + color + "m") if not color == None else "") + entry + (("\u001b[0m") if not color == None else ""))

def error(entry: str):
    log("ERROR: " + entry + "", color="0;31")

def warning(entry: str):
    log("WARNING: " + entry + "", color="0;31")

def interrupt(_, __):
    print("\r", end="")
    signal.signal(signal.SIGINT, SIGINT)
    exitGracefully()

def exitGracefully():
    global running
    running = False
    log("Shutting down...")
    warning("Forcibly shutting down after initial Ctrl-C could cause loss of data.")
    log("Finishing current requests. Please wait...")
    # Workaround to bypass blocking socket listener
    os.system("echo \"\r\n\r\n\" | telnet " + config["bind-address"] + " " + str(config["bind-port"]) + " > /dev/null 2> /dev/null")

def encodeResponse(content: str, status="200 OK"):
    length = len(content.encode())
    # TODO: Testing, need to figure out exact/variable headers to send
    return ("HTTP/1.0 " + status + "\r\nContent-type: application/json; charset=UTF-8\r\nContent-length: " + str(length) + "\r\nConnection: closed\r\n\r\n" + content).encode()

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
        log("Configuration created.")
        cd = os.path.split(os.path.realpath(__file__))[0]
        log("You can modify the configuration at " + cd + "/data/config.json")
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
    log("Configuration loaded.")
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
        try:
            data.append(client.recv(1))
        except:
            # Connection timed out
            client.close()
            return

        try:
            headers = b''.join(data).decode("UTF-8")
        except:
            error("Server killed in the middle of operation. Active data may have been lost.")
            return

        if "\r\n\r\n" in headers:
            # End of headers reached
            break
    
    headers = headers[:-4].replace("\r", "").split("\n")
    
    lengthFound = False
    length = 0
    head = headers[0].split(" ")
    if len(head) < 3:
        client.send(encodeResponse(json.dumps({"status": "error", "error": "Malformed request header."}), status="400 Bad Request"))
        client.close()
        return

    verb = head[0].upper()
    if not verb in ["POST", "GET", "PUT", "DELETE"]:
        client.send(encodeResponse(json.dumps({"status": "error", "error": "Invalid request verb."}), status="400 Bad Request"))
        client.close()
        return

    path = head[1]

    data = ""

    if verb == "POST" or verb == "PUT":
        for header in headers:
            if "content-length: " in header.lower():
                length = int(header.split(": ")[1])
                lengthFound = True
                break
        if not lengthFound:
            client.send(encodeResponse(json.dumps({"status": "error", "error": "Content length must be specified in the request header for request verbs which send body content. (POST, PUT)"}), status="411 Length Required"))
            client.close()
            return
    
        data = client.recv(length).decode("UTF-8")

    handleVerifiedRequest(client, verb, path, data)

    client.close()
    return

def handleVerifiedRequest(client, verb: str, path: str, data: str):

    path = path[1:].split("/")

    if len(path) > 3:
            client.send(encodeResponse(json.dumps({"status": "error", "error": "Path exceeds depth of structure."}), status="400 Bad Request"))
            client.close()
            return

    if len(path) == 0:
        # List databases
        pass

    # Create
    if verb == "POST":

        # Create database
        if len(path) == 1:

            # Database exists already, error
            if os.path.exists("data/db/" + path[0] + "/"):
                client.send(encodeResponse(json.dumps({"status": "error", "error": "Database already exists."}), status="409 Conflict"))
                client.close()
                return

            # Database does not exist, create it
            else:
                # TODO
                pass

        # Create table
        elif len(path) == 2:

            # Database exists
            if os.path.exists("data/db/" + path[0] + "/"):

                # Table exists already, error
                if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/"):
                    client.send(encodeResponse(json.dumps({"status": "error", "error": "Table already exists."}), status="409 Conflict"))
                    client.close()
                    return

                # Table does not exist, create it
                else:
                    # TODO
                    pass

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"status": "error", "error": "Database does not exist."}), status="404 Not Found"))
                client.close()
                return

        # Create row
        else:
            # Database exists
            if os.path.exists("data/db/" + path[0] + "/"):

                # Table exists
                if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/"):

                    # Row exists already, error
                    if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/" + path[2] + ".row"):
                        client.send(encodeResponse(json.dumps({"status": "error", "error": "Row already exists."}), status="409 Conflict"))
                        client.close()
                        return

                    # Row does not exist, create it
                    else:
                        # TODO
                        pass

                # Table does not exist, error
                else:
                    client.send(encodeResponse(json.dumps({"status": "error", "error": "Table does not exist."}), status="404 Not Found"))
                    client.close()
                    return

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"status": "error", "error": "Database does not exist."}), status="404 Not Found"))
                client.close()
                return

    # Read
    elif verb == "GET":
        pass
        

    # Update
    elif verb == "PUT":
        pass

    # Delete
    else:
        pass



    client.send(encodeResponse("Verb: " + verb + "; Path: " + path + "; Data: " + data + ";"))
    pass

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((config["bind-address"], config["bind-port"]))

# Tell the server to begin listening and allow 128 backlogged requests in case of heavy server load (default maximum for Ubuntu)
sock.listen(128)

while running:
    try:
        # Wait for request
        client, address = sock.accept()
        client.settimeout(60)
        # Start a new thread to handle this client and go back to listening for requests
        threading.Thread(target=handleRequest, args=(client, address)).start()
    except KeyboardInterrupt:
        pass
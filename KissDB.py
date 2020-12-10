#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, json, time, signal, datetime, fcntl, threading, socket, yaml


# Constants
CONFIG = {"bind-address": "127.0.0.1","bind-port": 1700}

# Functions
def log(entry: str, color:str = None):
    print("[" + datetime.datetime.now().strftime("%m/%d/%Y @ %I:%M:%S %p") + "] " + (("\033[" + color + "m") if not color == None else "") + entry + (("\u001b[0m") if not color == None else ""))

def logError(entry: str):
    log("ERROR: " + entry + "", color="0;31")

def logWarning(entry: str):
    log("WARNING: " + entry + "", color="0;33")

def logInfo(entry: str):
    log("INFO: " + entry + "", color="0;34")

def interrupt(_, __):
    print("\r", end = "")
    signal.signal(signal.SIGINT, SIGINT)
    exitGracefully()

def exitGracefully():
    global running
    running = False
    log("Shutting down...")
    logWarning("Forcibly shutting down after initial Ctrl-C could cause loss of data.")
    log("Finishing current requests. Please wait...")
    # Workaround to bypass blocking socket listener
    #os.system("echo \"\r\n\r\n\" | telnet " + config["bind-address"] + " " + str(config["bind-port"]) + " > /dev/null 2> /dev/null")
    exit()

def encodeResponse(content: str, status: str = "200 OK"):
    length = len(content.encode())
    # TODO: Testing, need to figure out exact/variable headers to send
    return ("HTTP/1.0 " + status + "\r\nContent-type: application/json; charset=UTF-8\r\nContent-length: " + str(length) + "\r\nConnection: closed\r\n\r\n" + content).encode()

# Create
def createDatabase(db: str) -> bool:
    # TODO
    return False

def createTable(db: str, table: str) -> bool:
    # TODO
    return False

def createBox(db: str, table: str, box: str, content: str = None) -> bool:
    # TODO
    return False

# Read
def readBox(db: str, table: str, box: str) -> str:
    # TODO
    raise Exception("Testing")
    return ""

# Update
def updateBox(db: str, table: str, box: str, content: str) -> bool:
    # TODO
    return False

# Delete
def deleteDatabase(db: str) -> bool:
    # TODO
    return False

def deleteTable(db: str, table: str) -> bool:
    # TODO
    return False

def deleteBox(db: str, table: str, box: str) -> bool:
    # TODO
    return False

# Setup
log("Starting server...")
running = True
SIGINT = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, interrupt)
log("Checking configuration...")
if not os.path.exists("data/config.yml"):
    if not os.path.exists("data/"):
        logWarning("Data folder not found.")
        log("Creating data folder...")
        try:
            os.mkdir("data/")
            log("Data folder created.")
        except:
            logError("Data folder could not be created.")
            exitGracefully()
    logWarning("Configuration not found.")
    log("Creating configuration...")
    try:
        with open("data/config.yml", "w") as f:
            f.write(yaml.dump(CONFIG, Dumper = yaml.Dumper))
        log("Configuration created.")
        cd = os.path.split(os.path.realpath(__file__))[0]
        logInfo("You can modify the configuration at " + cd + "/data/config.yml")
    except:
        logError("Configuration could not be created.")
        exitGracefully()
else:
    log("Configuration found.")

log("Loading configuration...")
try:
    with open("data/config.yml", "r") as f:
        config = yaml.load(f.read(), Loader = yaml.Loader)
    log("Configuration loaded.")
except:
    logError("Configuration could not be loaded.")
    exitGracefully()

log("Checking database storage...")
if not os.path.exists("data/db/"):
    logWarning("Database storage not found.")
    try:
        os.mkdir("data/db/")
        log("Database storage created.")
    except:
        logError("Could not create database storage.")
else:
    log("Database storage found.")

log("Server successfully started.")

dbCount = len(next(os.walk("data/db/"))[1])
logInfo("Handling " + "{:,}".format(dbCount) + " database" + ("." if dbCount == 1 else "s."))

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
            logError("Server killed in the middle of operation. Active data may have been lost.")
            return

        if "\r\n\r\n" in headers:
            # End of headers reached
            break
    
    headers = headers[:-4].replace("\r", "").split("\n")
    
    lengthFound = False
    length = 0
    head = headers[0].split(" ")
    if len(head) < 3:
        client.send(encodeResponse(json.dumps({"success": False, "result": "Malformed request header."}), status = "400 Bad Request"))
        client.close()
        return

    verb = head[0].upper()
    if not verb in ["POST", "GET", "PUT", "DELETE"]:
        client.send(encodeResponse(json.dumps({"success": False, "result": "Invalid request verb."}), status = "400 Bad Request"))
        client.close()
        return

    path = head[1]

    data = ""

    if verb == "POST" or verb == "PUT":
        for header in headers:
            if "content-length: " in header.lower():
                length = int(header.split(": ")[1])
                lengthFound = True
        if not lengthFound:
            client.send(encodeResponse(json.dumps({"success": False, "result": "Content length must be specified in the request header for request verbs which send body content. (POST, PUT)"}), status = "411 Length Required"))
            client.close()
            return
    
        data = client.recv(length).decode("UTF-8")

    handleVerifiedRequest(client, verb, path, data)

    client.close()
    return

def handleVerifiedRequest(client, verb: str, path: str, data: str):

    path = path.replace("/", " ").strip().split(" ")

    if len(path) > 3:
            client.send(encodeResponse(json.dumps({"success": False, "result": "Path exceeds depth of structure."}), status = "400 Bad Request"))
            client.close()
            return

    # Create
    if verb == "POST":

        # Create database
        if len(path) == 1:

            # Database exists already, error
            if os.path.exists("data/db/" + path[0] + "/"):
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database already exists."}), status = "409 Conflict"))
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
                    client.send(encodeResponse(json.dumps({"success": False, "result": "Table already exists."}), status = "409 Conflict"))
                    client.close()
                    return

                # Table does not exist, create it
                else:
                    # TODO
                    pass

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database does not exist."}), status = "404 Not Found"))
                client.close()
                return

        # Create row
        else:
            # Database exists
            if os.path.exists("data/db/" + path[0] + "/"):

                # Table exists
                if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/"):

                    # Box already exists, error
                    if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/" + path[2] + ""):
                        client.send(encodeResponse(json.dumps({"success": False, "result": "Box already exists."}), status = "409 Conflict"))
                        client.close()
                        return

                    # Box does not exist, create it
                    else:
                        # TODO
                        pass

                # Table does not exist, error
                else:
                    client.send(encodeResponse(json.dumps({"success": False, "result": "Table does not exist."}), status = "404 Not Found"))
                    client.close()
                    return

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database does not exist."}), status = "404 Not Found"))
                client.close()
                return

    # Read
    elif verb == "GET":

        # List databases
        if len(path) == 1 and path[0] == "":
            client.send(encodeResponse(json.dumps({"success": True, "result": next(os.walk("data/db/"))[1]})))
            client.close()
            return

        # List tables
        elif len(path) == 1:

            # Database exists, list its tables
            if os.path.exists("data/db/" + path[0] + "/"):
                client.send(encodeResponse(json.dumps({"success": True, "result": next(os.walk("data/db/" + path[0] + "/"))[1]})))
                client.close()
                return

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database does not exist."}), status = "404 Not Found"))
                client.close()
                return

        # List boxes
        elif len(path) == 2:

            # Database exists, check table
            if os.path.exists("data/db/" + path[0] + "/"):

                # Table exists, list its boxes
                if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/"):
                    client.send(encodeResponse(json.dumps({"success": True, "result": next(os.walk("data/db/" + path[0] + "/" + path[1] + "/"))[2]})))
                    client.close()
                    return

                # Table does not exist, error
                else:
                    client.send(encodeResponse(json.dumps({"success": False, "result": "Table does not exist."}), status = "404 Not Found"))
                    client.close()
                    return

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database does not exist."}), status = "404 Not Found"))
                client.close()
                return

        # Get box contents
        elif len(path) == 3:

            # Database exists, check table
            if os.path.exists("data/db/" + path[0] + "/"):

                # Table exists, check box
                if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/"):

                    # Box exists, get its contents
                    if os.path.exists("data/db/" + path[0] + "/" + path[1] + "/" + path[2]):
                        try:
                            data = readBox(path[0], path[1], path[2])
                        except:
                            logError("Unable to get box contents: " + "/".join(path))
                            data = None
                        if data == None:
                            client.send(encodeResponse(json.dumps({"success": False, "result": "Problem getting box contents."}), status = "500 Internal Server Error"))
                        else:
                            client.send(encodeResponse(json.dumps({"success": True, "result": data})))
                        client.close()
                        return

                    # Box does not exist, error
                    else:
                        client.send(encodeResponse(json.dumps({"success": False, "result": "Box does not exist."}), status = "404 Not Found"))
                        client.close()
                        return

                # Table does not exist, error
                else:
                    client.send(encodeResponse(json.dumps({"success": False, "result": "Table does not exist."}), status = "404 Not Found"))
                    client.close()
                    return

            # Database does not exist, error
            else:
                client.send(encodeResponse(json.dumps({"success": False, "result": "Database does not exist."}), status = "404 Not Found"))
                client.close()
                return

    # Update
    elif verb == "PUT":
        pass

    # Delete
    else:
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
        threading.Thread(target = handleRequest, args = (client, address)).start()
    except KeyboardInterrupt:
        pass

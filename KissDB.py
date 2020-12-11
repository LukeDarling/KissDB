#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, time, datetime, signal, fcntl, threading, socket
import json, yaml


# Constants
CONFIG = {"server-bind-port": 1700, "box-cache-seconds": 300, "request-timeout-seconds": 60}

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
    exit()

def sendResponse(client, success: bool, result: str, status: str = "200 OK"):
    content = json.dumps({"success": success, "result": result})
    length = len(content.encode())
    client.send(("HTTP/1.1 " + status + "\r\nContent-type: application/json; charset=UTF-8\r\nContent-length: " + str(length) + "\r\nConnection: closed\r\n\r\n" + content).encode())
    client.close()

# Exists?
# Does database exist?
def databaseExists(db: str) -> (bool, str):
    if os.path.exists("data/db/" + db + "/"):
        return (True, None)
    else:
        return (False, "Database does not exist.")

# Does table exist?
def tableExists(db: str, table: str) -> (bool, str):
    if os.path.exists("data/db/" + db + "/" + table + "/"):
        return (True, None)
    else:
        t = databaseExists(db)
        return (False, "Table does not exist." if t[0] else t[1])

# Does box exist?
def boxExists(db: str, table: str, box: str) -> (bool, str):
    if os.path.exists("data/db/" + db + "/" + table + "/" + box):
        return (True, None)
    else:
        t = tableExists(db, table)
        return (False, "Box does not exist." if t[0] else t[1])



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

logInfo("Server successfully started on localhost:" + str(config["server-bind-port"]) + ".")

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
        return sendResponse(client, success = False, result = "Malformed request header.", status = "400 Bad Request")

    verb = head[0].upper()
    if not verb in ["POST", "GET", "PUT", "DELETE"]:
        return sendResponse(client, success = False, result = "Invalid request verb.", status = "400 Bad Request")

    path = head[1]

    data = ""

    if verb == "POST" or verb == "PUT":
        for header in headers:
            if "content-length: " in header.lower():
                length = int(header.split(": ")[1])
                lengthFound = True
        if not lengthFound:
            return sendResponse(client, success = False, result = "Content length must be specified in the request header for request verbs which send body content. (POST, PUT)", status = "411 Length Required")
    
        data = client.recv(length).decode("UTF-8")

    handleVerifiedRequest(client, verb, path, data)

    client.close()
    return

def handleVerifiedRequest(client, verb: str, path: str, data: str):

    path = path.replace("/", " ").strip().split(" ")

    if len(path) > 3:
        return sendResponse(client, success = False, result = "Path exceeds depth of structure.", status = "400 Bad Request")

    # Create
    if verb == "POST":

        # Create database
        if len(path) == 1:

            # Database exists already, error
            if databaseExists(path[0])[0]:
                return sendResponse(client, success = False, result = "Database already exists.", status = "409 Conflict")

            # Database does not exist, create it
            else:
                try:
                    createDatabase(path[0])
                    return sendResponse(client, success = True, result = "Database successfully created.")
                except:
                    logError("Could not create database: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Database could not be created.", status = "500 Internal Server Error")

        # Create table
        elif len(path) == 2:

            # Database exists
            exists = databaseExists(path[0])
            if exists[0]:

                # Table exists already, error
                if tableExists(path[0], path[1])[0]:
                    return sendResponse(client, success = False, result = "Table already exists.", status = "409 Conflict")

                # Table does not exist, create it
                else:
                    try:
                        createTable(path[0], path[1])
                        return sendResponse(client, success = True, result = "Table successfully created.")
                    except:
                        logError("Could not create table: " + "/".join(path))
                        return sendResponse(client, success = False, result = "Table could not be created.", status = "500 Internal Server Error")

            # Database does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

        # Create row
        else:

            # Structure exists
            exists = tableExists(path[0], path[1])
            if exists[0]:

                # Box exists already, error
                if boxExists(path[0], path[1], path[2])[0]:
                    return sendResponse(client, success = False, result = "Box already exists.", status = "409 Conflict")

                # Box does not exist, create it
                else:
                    try:
                        createBox(path[0], path[1], path[2], data)
                        return sendResponse(client, success = True, result = "Box successfully created.")
                    except:
                        logError("Could not create box: " + "/".join(path))
                        return sendResponse(client, success = False, result = "Box could not be created.", status = "500 Internal Server Error")

            # Something in the structure does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

    # Read
    elif verb == "GET":

        # List databases
        if len(path) == 1 and path[0] == "":
            return sendResponse(client, success = True, result = next(os.walk("data/db/"))[1])

        # List tables
        elif len(path) == 1:

            # Check structure existence
            exists = databaseExists(path[0])
            if exists[0]:
                return sendResponse(client, success = True, result = next(os.walk("data/db/" + path[0] + "/"))[1])

            # Database does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

        # List boxes
        elif len(path) == 2:

            # Check structure existence
            exists = tableExists(path[0], path[1])
            if exists[0]:
                return sendResponse(client, success = True, result = next(os.walk("data/db/" + path[0] + "/" + path[1] + "/"))[2])

            # Database does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

        # Get box contents
        elif len(path) == 3:

            # Check structure existence
            exists = boxExists(path[0], path[1], path[2])
            if exists[0]:
                try:
                    data = readBox(path[0], path[1], path[2])
                    return sendResponse(client, success = True, result = data)
                except:
                    logError("Unable to get box contents: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Problem getting box contents.", status = "500 Internal Server Error")

            # Structure does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

    # Update
    elif verb == "PUT":
        pass

    # Delete
    else:
        pass



sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind(("127.0.0.1", config["server-bind-port"]))

# Tell the server to begin listening and allow 128 backlogged requests in case of heavy server load (default maximum for Ubuntu)
sock.listen(128)

while running:
    try:
        # Wait for request
        client, address = sock.accept()
        client.settimeout(config["request-timeout-seconds"])
        # Start a new thread to handle this client and go back to listening for requests
        threading.Thread(target = handleRequest, args = (client, address)).start()
    except KeyboardInterrupt:
        pass

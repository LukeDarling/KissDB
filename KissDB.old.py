#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, time, datetime, uuid, signal, shutil, fcntl, threading, socket
import json, yaml


# Constants
DEFAULTCONFIG = {"server-bind-port": 1700, "box-cache-seconds": 300, "request-timeout-seconds": 60, "log-color": True}
WRITE = 1
READ = 0
DELETE = -1

journal = []
cache = {}


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
def createDatabase(db: str):
    os.mkdir("data/db/" + db + "/")

def createTable(db: str, table: str):
    os.mkdir("data/db/" + db + "/" + table + "/")

def createBox(db: str, table: str, box: str, content: str = ""):
    updateBox(db, table, box, content)

# Read
def readBox(db: str, table: str, box: str) -> str:
    if not db + "/" + table + "/" + box in cache:
        global journal
        journal += [{"path": db + "/" + table + "/" + box, "action": READ, "requested": datetime.datetime.now().timestamp()}]
        while not db + "/" + table + "/" + box in cache:
            pass
    else:
        cache[db + "/" + table + "/" + box]["last-accessed"] = datetime.datetime.now().timestamp()
    return cache[db + "/" + table + "/" + box]["value"]

# Update
def updateBox(db: str, table: str, box: str, content: str):
    global journal
    journal += [{"path": db + "/" + table + "/" + box, "action": WRITE, "requested": datetime.datetime.now().timestamp(), "value": content}]

# Delete
def deleteDatabase(db: str):
    global journal
    journal += [{"path": db, "action": DELETE, "requested": datetime.datetime.now().timestamp()}]

def deleteTable(db: str, table: str):
    global journal
    journal += [{"path": db + "/" + table, "action": DELETE, "requested": datetime.datetime.now().timestamp()}]

def deleteBox(db: str, table: str, box: str):
    global journal
    journal += [{"path": db + "/" + table + "/" + box, "action": DELETE, "requested": datetime.datetime.now().timestamp()}]

def journalingThread():
    global journal
    global cache

    logInfo("Journaling thread started.")

    # Watch for journaling requests until server shuts down
    while running:

        # Wait
        time.sleep(0.01)

        # Check if there are any new journaling requests
        while len(journal) > 0:

            # Sort the journal requests to determine the oldest
            journal = sorted(journal, key=lambda k: k["requested"])
            # Grab the oldest journal request and start with it
            entry = journal.pop(0)

            timestamp = datetime.datetime.now().timestamp()

            # Handle journal WRITE requests
            if entry["action"] == WRITE:

                # Add the requested box value to the cache
                cache[entry["path"]] = {"last-accessed": timestamp, "value": entry["value"]}

                # Write the changes to disk
                with open("data/db/" + entry["path"], "w") as box:
                    box.write(entry["value"])

            # Handle journal READ requests
            elif entry["action"] == READ:

                # Read the requested box into the cache
                with open("data/db/" + entry["path"], "r") as box:
                    cache[entry["path"]] = {"last-accessed": timestamp, "value": box.read()}

            # Handle journal DELETE requests
            elif entry["action"] == DELETE:

                # Delete the requested entity from disk
                if os.path.isdir("data/db/" + entry["path"]):
                    shutil.rmtree("data/db/" + entry["path"])
                else:
                    os.remove("data/db/" + entry["path"])

                # Delete the requested entity from the cache
                if entry["path"] in cache:
                    del cache[entry["path"]]

    logInfo("Journaling thread finished.")

def cacheManagerThread():
    global cache
    
    logInfo("Cache manager thread started.")

    # Clean up cache regularly until server shuts down
    while running:

        # Wait a second
        time.sleep(1)

        # Loop through all cache entries
        for path in list(cache):
            # If the cache hasn't been accessed for the amount of time configured, remove it
            if cache[path]["last-accessed"] + config["box-cache-seconds"] < datetime.datetime.now().timestamp():
                del cache[path]
    
    logInfo("Cache manager thread finished.")

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

            # Database exists already
            if databaseExists(path[0])[0]:
                return sendResponse(client, success = True, result = "Database already exists.", status = "200 OK")

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

                # Table exists already
                if tableExists(path[0], path[1])[0]:
                    return sendResponse(client, success = True, result = "Table already exists.", status = "200 OK")

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

        # Create box
        else:

            # Check structure existence
            exists = tableExists(path[0], path[1])
            # Structure exists
            if exists[0]:

                # Box exists already
                if boxExists(path[0], path[1], path[2])[0]:
                    try:
                        # Try updating the box
                        updateBox(path[0], path[1], path[2], data)
                        return sendResponse(client, success = True, result = "Box successfully updated.")
                    except:
                        # Probably a permission problem
                        logError("Could not update box: " + "/".join(path))
                        return sendResponse(client, success = False, result = "Box could not be updated.", status = "500 Internal Server Error")

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

            # Structure exists
            if exists[0]:
                return sendResponse(client, success = True, result = next(os.walk("data/db/" + path[0] + "/" + path[1] + "/"))[2])

            # Structure does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

        # Get box contents
        elif len(path) == 3:

            # Check structure existence
            exists = boxExists(path[0], path[1], path[2])
            if exists[0]:
                try:
                    # Try reading box contents
                    data = readBox(path[0], path[1], path[2])
                    # Success, send the client the data
                    return sendResponse(client, success = True, result = data)
                except:
                    # Might be a filesystem permission problem
                    logError("Unable to get box contents: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Problem getting box contents.", status = "500 Internal Server Error")

            # Structure does not exist, error
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")
    # Update
    elif verb == "PUT":
        return handleVerifiedRequest(client, "POST", path, data)

    # Delete
    else:

        # Delete all databases
        if len(path) == 1 and path[0] == "":
            dbs = next(os.walk("data/db/"))[1]
            total = len(dbs)
            success = 0
            for db in dbs:
                try:
                    deleteDatabase(db)
                    success += 1
                except:
                    logError("Could not delete database: /" + db)
            if total == success:
                sendResponse(client, success = True, result = "All databases successfully deleted.")
            else:
                return sendResponse(client, success = False, result = (str(success) + " of " + str(total) + " database" + ("" if total == 1 else "s") + " successfully deleted. " + str(total - success) + " of " + str(total) + " database" + ("" if total == 1 else "s") + " could not be deleted."), status = "500 Internal Server Error")

        # Delete database
        elif len(path) == 1:
            exists = databaseExists(path[0])
            if exists[0]:
                try:
                    deleteDatabase(path[0])
                    return sendResponse(client, success = True, result = "Database successfully deleted.")
                except:
                    logError("Database could not be deleted: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Database could not be deleted.", status = "500 Internal Server Error")
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")

        # Delete table
        elif len(path) == 2:
            exists = tableExists(path[0], path[1])
            if exists[0]:
                try:
                    deleteTable(path[0], path[1])
                    return sendResponse(client, success = True, result = "Table successfully deleted.")
                except:
                    logError("Table could not be deleted: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Table could not be deleted.", status = "500 Internal Server Error")
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")
                
        # Delete box
        elif len(path) == 3:
            exists = boxExists(path[0], path[1], path[2])
            if exists[0]:
                try:
                    deleteBox(path[0], path[1], path[2])
                    return sendResponse(client, success = True, result = "Box successfully deleted.")
                except:
                    logError("Box could not be deleted: " + "/".join(path))
                    return sendResponse(client, success = False, result = "Box could not be deleted.", status = "500 Internal Server Error")
            else:
                return sendResponse(client, success = False, result = exists[1], status = "404 Not Found")


# Setup
log("Starting server...")
running = True
SIGINT = signal.getsignal(signal.SIGINT)
signal.signal(signal.SIGINT, interrupt)




while running:
    try:
        # Wait for request
        client, address = sock.accept()
        client.settimeout(config["request-timeout-seconds"])

        # Start a new thread to handle this client and go back to listening for requests
        threading.Thread(target = handleRequest, args = (client, address)).start()
    except KeyboardInterrupt:
        pass

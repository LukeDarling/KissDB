#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
from typing import List
from flask import Flask, request, jsonify
from datetime import datetime
import os, time, uuid, signal, shutil, fcntl, threading, socket, json, yaml

cache = {}
requests = []

DATABASE_PATH = "data/db/"

class ReadRequest:

    database = None
    table = None
    box = None
    data = None
    isComplete = False
    requestedAt = 0

    def ReadRequest(self, database, table, box):
        self.requestedAt = datetime.now().timestamp()
        self.database = database
        self.table = table
        self.box = box
        requests.append(self)


class WriteRequest:

    path = None
    data = None
    isComplete = False
    requestedAt = 0

    def WriteRequest(self, database, table, box, data):
        self.requestedAt = datetime.now().timestamp()
        self.database = database
        self.table = table
        self.box = box
        self.data = data
        requests.append(self)

app = Flask(__name__)

def objectList(path: str) -> List(str):

    path = os.path.join(DATABASE_PATH, path)

    return next(os.walk(path))[1]



def objectMake(path: str, data: str = "") -> bool:

    path = os.path.join(DATABASE_PATH, path)

    if os.path.exists(path):
        return False

    if os.path.split(path).length == 3:
        try:
            with open(path + ".box", "w") as f:
                f.write(data)
            return True
        except:
            return False

    else:
        try:
            os.mkdir(path)
            return True
        except:
            return False



def objectDelete(path: str):

    path = os.path.join(DATABASE_PATH, path)

    if os.path.split(path).length == 3:
        path += ".box"

    if not os.path.exists(path):
        return

    shutil.rmtree(path)



def objectExists(path: str) -> bool:

    path = os.path.join(DATABASE_PATH, path)

    if os.path.split(path).length == 3:
        path += ".box"

    return os.path.exists(path)










# Handle /

# List all databases
@app.route("/", methods=["GET"])
def rootList():

    return jsonify({"success": True, "message": "Database list successfully retrieved.", "result": jsonify(list("/"))})




# Handle /<database>

@app.route("/<database>", methods=["GET"])
def databaseList(database):

    path = database

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectExists(path):
        return jsonify({"success": True, "message": "Table list successfully retrieved.", "result": jsonify(objectList(path))})
        
    else:
        return jsonify({"success": False, "message": "Database does not exist."})




@app.route("/<database>", methods=["POST", "PUT"])
def databaseCreate(database):

    path = database

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectMake(path):
        return jsonify({"success": True, "message":"Database successfully created."})

    else:
        return jsonify({"success": False, "message":"Database could not be created."})



@app.route("/<database>", methods=["DELETE"])
def databaseDelete(database):

    path = database

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectExists(path):
        objectDelete(path)
        return jsonify({"success": True, "message": "Database successfully deleted."})

    else:
        return jsonify({"success": False, "message": "Database did not exist, so not deleted."})







# Handle /<database>/<table>

@app.route("/<database>/<table>", methods=["GET"])
def tableList(database, table):

    path = os.path.join(database, table)

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectExists(path):
        return jsonify({"success": True, "message": "Box list successfully retrieved.", "result": jsonify(objectList(path))})

    else:
        return jsonify({"success": False, "message": "Table does not exist."})




@app.route("/<database>/<table>", methods=["POST", "PUT"])
def tableUpdate(database, table):

    path = os.path.join(database, table)

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectMake(path):
        return jsonify({"success": True, "message":"Table successfully created."})

    else:
        return jsonify({"success": False, "message":"Table could not be created."})



@app.route("/<database>/<table>", methods=["DELETE"])
def tableDelete(database, table):

    path = os.path.join(database, table)

    if ".." in path:
        return jsonify({"success": False, "message": "Disallowed operator: `..`."})

    if objectExists(path):
        objectDelete(path)
        return jsonify({"success": True, "message": "Table successfully deleted."})
    
    else:
        return jsonify({"success": False, "message": "Table did not exist, so not deleted."})








# Handle /<database>/<table>/<box>

@app.route("/<database>/<table>/<box>", methods=["GET"])
def tableRead(database, table, box):

    if os.path.join(database, table, box) in cache:
        cache[os.path.join(database, table, box)]["last-accessed"] = datetime.now().timestamp()
        return jsonify({"success": True, "message": "Box successfully retrieved.", "result": cache[os.path.join(database, table, box)]["data"]})

    req = ReadRequest(database, table, box)

    while not req.isComplete:
        continue

    cache[os.path.join(database, table, box)] = {"last-accessed": datetime.now().timestamp(), "data": req.data}
    return jsonify({"success": True, "message": "Box successfully retrieved.", "result": req.data})



@app.route("/<database>/<table>/<box>", methods=["POST", "PUT"])
def tableUpdate(database, table, box):
    
    cache[os.path.join(database, table, box)] = {"last-accessed": datetime.now().timestamp(), "data": request.get_data()}
    WriteRequest(database, table, box, request.get_data())




@app.route("/<database>/<table>/<box>", methods=["DELETE"])
def tableDelete(database, table, box):
    del cache[os.path.join(database, table, box)]
    objectDelete(os.path.join(database, table, box))






#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
from flask import Flask, jsonify
from datetime import datetime
import os, time, uuid, signal, shutil, fcntl, threading, socket, json, yaml

class ReadRequest:

    path = None
    data = None
    isComplete = False
    requestedAt = 0

    def ReadRequest(self, path):
        self.requestedAt = datetime.now().timestamp()
        self.path = path

app = Flask(__name__)

# Handle /

# List all databases
@app.route("/", methods=["GET"])
def rootRead():
    return jsonify({"success": True, "result": jsonify(next(os.walk("data/db/"))[1])})


# Handle /<database>

@app.route("/<database>", methods=["GET"])
def databaseRead(database):
    pass

@app.route("/<database>", methods=["POST"])
def databaseUpdate(database):
    pass

@app.route("/<database>", methods=["DELETE"])
def databaseDelete(database):
    pass

# Handle /<database>/<table>

@app.route("/<database>/<table>", methods=["GET"])
def tableRead(database, table):
    pass

@app.route("/<database>/<table>", methods=["POST"])
def tableUpdate(database, table):
    pass

@app.route("/<database>/<table>", methods=["DELETE"])
def tableDelete(database, table):
    pass


# Handle /<database>/<table>/<box>

@app.route("/<database>/<table>/<box>", methods=["GET"])
def tableRead(database, table, box):
    pass

@app.route("/<database>/<table>/<box>", methods=["POST"])
def tableUpdate(database, table, box):
    pass

@app.route("/<database>/<table>/<box>", methods=["DELETE"])
def tableDelete(database, table, box):
    pass




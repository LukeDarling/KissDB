#!/usr/bin/env python3
# KissDB Database Daemon written by Luke Darling.
# All rights reserved.

# Imports
import os

# Constants
DEFAULT_CONFIG = {"server-bind-port": 1700, "box-cache-seconds": 300, "request-timeout-seconds": 60, "log-color": True}
ROOT_DIRECTORY = os.path.split(os.path.split(os.path.realpath(__file__))[0])[0] + "/"
DATA_DIRECTORY = ROOT_DIRECTORY + "data/"
DB_DIRECTORY = DATA_DIRECTORY + "db/"
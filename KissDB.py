#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
from src.Daemon import *
from src.Config import *

config = Config.load()
if(config == None):
    exit(1)

daemon = Daemon().start(config)
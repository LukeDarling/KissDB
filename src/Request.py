#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import socket, time


class Request:

    def __init__(this, daemon, client: socket, address):
        time.sleep(15)
        client.close()

#!/usr/bin/env python3

import os, json

os.mkdir("data")
os.mkdir("data/db")
with open("data/config.json", "w") as f:
    f.write(json.dumps(CONFIG))
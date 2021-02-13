#!/usr/bin/env python3
# KissDB written by Luke Darling.
# All rights reserved.

# Imports
import os, yaml
from typing import List
from src.Constants import DEFAULT_CONFIG, ROOT_DIRECTORY, DATA_DIRECTORY, DB_DIRECTORY
from src.Logger import Logger

class Config:
    def load() -> List:
        # Verify config exists
        if not os.path.exists(DATA_DIRECTORY + "config.yml"):
            # Configuration does not exist

            # Verify data folder exists
            if not os.path.exists(DATA_DIRECTORY):
                # Data folder does not exist
                Logger.logWarning("Data folder not found.")
                Logger.logInfo("Creating data folder...")
                try:
                    os.mkdir(DATA_DIRECTORY)
                    Logger.logNotice("Data folder created.")
                except:
                    Logger.logError("Data folder could not be created.")
                    return None

            Logger.logWarning("Configuration not found.")
            Logger.logInfo("Creating configuration...")
            try:
                with open(DATA_DIRECTORY + "config.yml", "w") as f:
                    f.write(yaml.dump(DEFAULT_CONFIG, Dumper = yaml.Dumper))
                Logger.logNotice("Configuration created.")
                Logger.logNotice("You can modify the configuration at " + DATA_DIRECTORY + "config.yml")
            except:
                Logger.logError("Configuration could not be created.")
                return None
        else:
            # Configuration exists
            Logger.logInfo("Configuration found.")

        Logger.logInfo("Loading configuration...")
        try:
            with open("data/config.yml", "r") as f:
                config = yaml.load(f.read(), Loader = yaml.Loader)
                Logger.logInfo("Configuration loaded.")
        except:
            Logger.logError("Configuration could not be loaded.")
            return None

        return config
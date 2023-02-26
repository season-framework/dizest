from dizest import util
from abc import *
import sys
import os
import subprocess
import multiprocessing as mp
import random
import socketio
import requests
import json
import signal
import time
import psutil

class SimpleSpawner(BaseSpawner):
    def __init__(self, kernelspec=None, cwd=None, user=None):
        super().__init__(kernelspec=kernelspec, cwd=cwd)
        self.name = "simple"
        self.user = user
        
    def start(self):
        kernelspec = self.kernelspec
        cwd = self.cwd
        user = self.user

        port = random.randrange(10000, 60000)
        while util.os.port(port):
            port = random.randrange(10000, 60000)
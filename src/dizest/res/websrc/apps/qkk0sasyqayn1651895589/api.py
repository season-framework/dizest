import season
import dizest

import os
import time
import psutil
import platform
import resource

def kill(wiz):
    process = psutil.Process(os.getpid())
    children = process.children(recursive=True)
    for child in children:
        childp = psutil.Process(child.pid)
        childp.terminate()
    wiz.response.status(200)
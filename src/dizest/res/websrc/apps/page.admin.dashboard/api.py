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
        try:
            child.terminate()
            child.kill()
            child.wait()
        except Exception as e:
            pass
        
    wiz.response.status(200)
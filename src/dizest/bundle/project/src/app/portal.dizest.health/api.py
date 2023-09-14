import season
import dizest
import os
import time
import psutil
import platform
import subprocess
import json

config = wiz.model("portal/dizest/config")
stdClass = season.util.std.stdClass

DEFAULT_ATTRIBUTES = (
    'index',
    'uuid',
    'name',
    'timestamp',
    'memory.total',
    'memory.free',
    'memory.used',
    'utilization.gpu',
    'utilization.memory'
)

def get_gpu_info(nvidia_smi_path='nvidia-smi', keys=DEFAULT_ATTRIBUTES, no_units=True):
    try:
        nu_opt = '' if not no_units else ',nounits'
        cmd = '%s --query-gpu=%s --format=csv,noheader%s' % (nvidia_smi_path, ','.join(keys), nu_opt)
        output = subprocess.check_output(cmd, shell=True)
        lines = output.decode().split('\n')
        lines = [ line.strip() for line in lines if line.strip() != '' ]

        return [ { k: v for k, v in zip(keys, line.split(', ')) } for line in lines ]
    except:
        return []

def health():
    process = psutil.Process(os.getpid())

    data = stdClass() 
    data.deploy = []
    data.deploy.append(dict(key='Python Version', value=platform.python_version()))
    data.deploy.append(dict(key='Dizest Version', value=dizest.version))
    data.deploy.append(dict(key='Wiz Version', value=season.version))

    data.system = []
    data.system.append(dict(key='CPU', value=psutil.cpu_percent(), format="1.0-2", unit="%"))

    memory = str(int(psutil.virtual_memory().used / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    memory = memory + " / " + str(int(psutil.virtual_memory().total / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    data.system.append(dict(key='Memory', value=memory))
    
    hdd = psutil.disk_usage(config.disk)
    disk = str(int(hdd.used / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    disk = disk + " / " + str(int(hdd.total / 1024 / 1024 / 1024 * 100) / 100) + ' GB'
    data.system.append(dict(key='Disk', value=disk))

    data.gpu = get_gpu_info()

    wiz.response.status(200, data)

from argh import arg, expects_obj
import os
import sys
import time
import subprocess
import psutil
import season
import dizest
import multiprocessing as mp
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import platform

PATH_WIZ = season.path.lib
PATH_DIZEST = os.path.dirname(os.path.dirname(__file__))

PATH_WORKINGDIR = os.getcwd()
PATH_WORKINGDIR_WEBSRC = os.path.join(PATH_WORKINGDIR, "websrc")
PATH_WORKINGDIR_PACKAGE = os.path.join(PATH_WORKINGDIR, "dizest.json")
PATH_WORKINGDIR_CONFIG = os.path.join(PATH_WORKINGDIR, "config.py")

cache = dict()

class Instance:
    def __init__(self, data):
        self._data = data
        self._output = dict()

    def input(self, name, default=None, id=None):
        try:
            inputs = self._data['inputs']
            if name not in inputs:
                return default
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                if ivalue is not None and len(ivalue) > 0:
                    return ivalue
                else:
                    return default
            
            # load from previous output
            res = []
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    continue

                linked_output = cache[fid]._output
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            if len(res) == 0: res = None
            elif len(res) == 1: res = res[0]
            if id is not None: return res[int(id)]

            return res
        except Exception as e:
            pass
        
        return default

    def inputs(self, name):
        try:
            res = []
            inputs = self._data['inputs']
            if name not in inputs:
                return res
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                return res
            
            # load from previous output
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    res.append(None)
                    continue

                linked_output = cache[fid]._output
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            return res
        except Exception as e:
            pass

        return []

    def output(self, name, value=None):
        self._output[name] = value

    def drive(self, *path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, *path)
        return dizest.util.os.storage(cwd)

@arg('--host', default=None, help='0.0.0.0')
@arg('--port', default=0, help='3000')
@arg('-f', default=None, help='workflow.dzw')
def run(f=None, host="0.0.0.0", port=0):
    if f is not None:
        workflow = dizest.Workflow.load(f)
        flows = workflow.flows()
        for flow_id in flows:
            flow = workflow.flow(flow_id)
            if flow.active() == False:
                continue
            
            flow_id, code, inputs, outputs = flow.data()

            data = dict()
            data['flow_id'] = flow_id
            data['inputs'] = inputs
            data['outputs'] = outputs

            dizesti = Instance(data)
            cache[flow_id] = dizesti

            env = dict()
            env['dizest'] = dizesti
            exec(code, env)

    port = int(port)
    fs = dizest.util.os.storage(PATH_WORKINGDIR_WEBSRC)
    if fs.exists() is False:
        print("dizest not installed")
        return
    
    config = fs.read.json("dizest.json", dict())
    
    if port < 1000:
        if 'port' in config:
            port = int(config['port'])
        else:
            port = 3000
    
    # set host
    if 'host' in config and host is None: host = config['host']
    if host is None: host = '0.0.0.0'

    config['port'] = port
    config['host'] = host
    config['path'] = PATH_WORKINGDIR

    # save dizest config
    fs.write.json("dizest.json", config)

    # build config
    PATH_CONFIG_BASE = os.path.join(PATH_DIZEST, 'res', 'wiz', 'server.py')
    PATH_CONFIG = os.path.join(PATH_WORKINGDIR_WEBSRC, 'config', 'server.py')

    data = fs.read.text(PATH_CONFIG_BASE)
    data = data.replace("__PORT__", str(port))
    data = data.replace("__HOST__", str(host))
    fs.write.text(PATH_CONFIG, data)
    
    # copy config
    fs.copy(os.path.join(PATH_DIZEST, 'res', 'wiz', 'wiz.py'), os.path.join("config", "wiz.py"))
    fs.copy(os.path.join(PATH_DIZEST, 'res', 'wiz', 'socketio.py'), os.path.join("config", "socketio.py"))

    # run server
    publicpath = os.path.join(PATH_WORKINGDIR_WEBSRC, 'public')
    apppath = os.path.join(publicpath, 'app.py')

    if os.path.isfile(apppath) == False:
        print("Invalid Project path: dizest structure not found in this folder.")
        return

    def run_ctrl():
        env = os.environ.copy()
        env['WERKZEUG_RUN_MAIN'] = 'true'
        cmd = str(sys.executable) + " " +  str(apppath)
        subprocess.call(cmd, env=env, shell=True)

    ostype = platform.system().lower()
    if ostype == 'linux':
        while True:
            try:
                proc = mp.Process(target=run_ctrl)
                proc.start()
                proc.join()
            except KeyboardInterrupt:
                for child in psutil.Process(proc.pid).children(recursive=True):
                    child.kill()
                return
            except:
                pass
    else:
        run_ctrl()
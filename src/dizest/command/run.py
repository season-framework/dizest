from argh import arg, expects_obj
import os
import sys
import time
import subprocess
import psutil
import season
import dizest
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import datetime
import platform
import signal
import atexit
import contextlib
import multiprocessing as mp

PATH_WIZ = season.path.lib
PATH_DIZEST = os.path.dirname(os.path.dirname(__file__))

PATH_WORKINGDIR = os.getcwd()
PATH_WORKINGDIR_PID = os.path.join(PATH_WORKINGDIR, "dizest.pid")
PATH_WORKINGDIR_WEBSRC = os.path.join(PATH_WORKINGDIR, "websrc")
PATH_WORKINGDIR_PACKAGE = os.path.join(PATH_WORKINGDIR, "dizest.json")
PATH_WORKINGDIR_CONFIG = os.path.join(PATH_WORKINGDIR, "config.py")

cache = dict()

class Daemon:
    def __init__(self, pidfile, target=None, stdout='/dev/null', stderr='/dev/null'):
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile
        self.run = target
       
    def daemonize(self):
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        os.chdir("/")
        os.setsid()
        os.umask(0)

        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        sys.stdout.flush()
        sys.stderr.flush()

        so = open(self.stdout, 'w')
        se = open(self.stderr, 'w')
        contextlib.redirect_stdout(so)
        contextlib.redirect_stderr(se)

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile, 'w').write("%s\n" % pid)

    def delpid(self):
        os.remove(self.pidfile)
 
    def start(self):
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            sys.exit(1)
        
        self.daemonize()
        self.run()

    def stop(self):
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return

        try:
            counter = 0
            for child in psutil.Process(pid).children(recursive=True):
                counter = counter + 1
                child.kill()
            print(f"killed {counter} dizest subprocess")
        except:
            pass

        try:
            while 1:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                sys.exit(1)

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

def runnable():
    publicpath = os.path.join(PATH_WORKINGDIR_WEBSRC, 'public')
    apppath = os.path.join(publicpath, 'app.py')

    while True:
        try:
            env = os.environ.copy()
            env['WERKZEUG_RUN_MAIN'] = 'true'
            process = subprocess.Popen([str(sys.executable), str(apppath)], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate()
        except Exception as e:
            pass
        except:
            counter = 0
            for child in psutil.Process(os.getpid()).children(recursive=True):
                counter = counter + 1
                child.kill()
            sys.exit(0)

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
        print("dizest not installed. run `dizest install` first.")
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

    print(f"DIZEST Hub running on http://{host}:{port}")
    runnable()

@arg('action', default=None, help="start|stop|restart")
@arg('--host', default=None, help='0.0.0.0')
@arg('--port', default=0, help='3000')
def server(action, host="0.0.0.0", port=0):
    port = int(port)
    fs = dizest.util.os.storage(PATH_WORKINGDIR_WEBSRC)
    if fs.exists() is False:
        print("dizest not installed. run `dizest install` first.")
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

    daemon = Daemon(PATH_WORKINGDIR_PID, target=runnable)
    if action == 'start':
        print(f"DIZESThub server running on http://{host}:{port}")
        daemon.start()
    elif action == 'stop':
        print(f"DIZESThub server stop")
        daemon.stop()
    elif action == 'restart':
        print("stopping running DIZESThub server...")
        try:
            daemon.stop()
        except:
            pass
        
        print(f"DIZESThub server restarted at http://{host}:{port}")
        daemon.start()
    else:
        print(f"`dizest server` not support `{action}`. (start|stop|restart)")

import season
import os
import pty
import subprocess
import termios
import struct
import fcntl
import shlex
import select
import psutil

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

def getCache(wiz, zone, namespace):
    if 'terminal' not in wiz.server.app: 
        wiz.server.app.terminal = season.util.std.stdClass()
    cache = wiz.server.app.terminal
    if zone not in cache:
        cache[zone] = season.util.std.stdClass()
    if namespace not in cache[zone]:
        cache[zone][namespace] = season.util.std.stdClass()
    return cache[zone][namespace]

class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self, wiz):
        pass

    def close(self, wiz, data, io):
        config = wiz.model("portal/dizest/config")
        wiz.session = wiz.model("portal/season/session")
        zone = data['zone']
        if config.acl(wiz, zone) == False:
            return

        namespace = data['namespace']
        cache = getCache(wiz, zone, namespace)
        if cache["child_pid"] is not None:
            ppid = cache["child_pid"]
            parent = psutil.Process(ppid)
            for child in parent.children(recursive=True):
                pid = child.pid
                os.system(f"kill -9 {pid} > /dev/null")
            os.system(f"kill -9 {ppid} > /dev/null")

    def join(self, wiz, data, io):
        config = wiz.model("portal/dizest/config")
        wiz.session = wiz.model("portal/season/session")
        zone = data['zone']
        if config.acl(wiz, zone) == False:
            return
        
        branch = wiz.branch()
        cache_namespace = data['namespace']
        cache = getCache(wiz, zone, cache_namespace)
        namespace = f"/wiz/app/{branch}/portal.dizest.editor.terminal"
        to = f"{zone}-{cache_namespace}"
        io.join(to)

    def create(self, wiz, data, io):
        wiz.session = wiz.model("portal/season/session")
        config = wiz.model("portal/dizest/config")
        branch = wiz.branch()
        zone = data['zone']
                
        if config.acl(wiz, zone) == False:
            return

        user_id = config.user_id(wiz, zone)
        cwd = config.storage_path(wiz, zone)
        cache_namespace = data['namespace']
        cache = getCache(wiz, zone, cache_namespace)
        namespace = f"/wiz/app/{branch}/portal.dizest.editor.terminal"
        to = f"{zone}-{cache_namespace}"
        socketio = wiz.server.app.socketio
        
        def read_and_forward_pty_output():
            max_read_bytes = 1024 * 20
            while True:
                socketio.sleep(0.01)
                try:
                    if cache["fd"]:
                        timeout_sec = 0
                        (data_ready, _, _) = select.select([cache["fd"]], [], [], timeout_sec)
                        if data_ready:
                            branch = wiz.branch()
                            output = os.read(cache["fd"], max_read_bytes).decode(errors="ignore")
                            io.emit("ptyoutput", {"output": output}, to=to, namespace=namespace, broadcast=True)
                except Exception as e:
                    cache["fd"] = None
                    break

        if "child_pid" not in cache: 
            cache["child_pid"] = None
        if "fd" not in cache: 
            cache["fd"] = None

        cache["cmd"] = f"sudo -u {user_id} bash".split(" ")
        if cache["child_pid"]:
            return

        (child_pid, fd) = pty.fork()

        if child_pid == 0:
            subprocess.run(cache["cmd"])
        else:
            cache["fd"] = fd
            cache["child_pid"] = child_pid
            set_winsize(fd, 50, 50)
            cmd = " ".join(shlex.quote(c) for c in cache["cmd"])
            socketio.start_background_task(target=read_and_forward_pty_output)
        
    def ptyinput(self, wiz, data):
        config = wiz.model("portal/dizest/config")
        wiz.session = wiz.model("portal/season/session")
        zone = data['zone']
        if config.acl(wiz, zone) == False:
            return

        namespace = data['namespace']
        cache = getCache(wiz, zone, namespace)
        if cache["fd"]:
            os.write(cache["fd"], data["input"].encode())

    def resize(self, wiz, data):
        config = wiz.model("portal/dizest/config")
        wiz.session = wiz.model("portal/season/session")
        zone = data['zone']
        if config.acl(wiz, zone) == False:
            return
            
        namespace = data['namespace']
        cache = getCache(wiz, zone, namespace)
        if cache["fd"]:
            set_winsize(cache["fd"], data["rows"], data["cols"])

import season
import os
import pty
import subprocess
import termios
import struct
import fcntl
import shlex
import select

def set_winsize(fd, row, col, xpix=0, ypix=0):
    winsize = struct.pack("HHHH", row, col, xpix, ypix)
    fcntl.ioctl(fd, termios.TIOCSWINSZ, winsize)

class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self, wiz):
        session = wiz.model("portal/season/session").use()
        if session.get("role") != "admin":
            return

        app = wiz.server.app.flask
        socketio = wiz.server.app.socketio

        def read_and_forward_pty_output():
            max_read_bytes = 1024 * 20
            while True:
                socketio.sleep(0.01)
                try:
                    if app.config["fd"]:
                        timeout_sec = 0
                        (data_ready, _, _) = select.select([app.config["fd"]], [], [], timeout_sec)
                        if data_ready:
                            branch = wiz.branch()
                            namespace = f"/wiz/app/{branch}/page.terminal"
                            output = os.read(app.config["fd"], max_read_bytes).decode(errors="ignore")
                            socketio.emit("ptyoutput", {"output": output}, namespace=namespace)
                except Exception as e:
                    app.config["child_pid"] = None
                    app.config["fd"] = None

        if "child_pid" not in app.config: app.config["child_pid"] = None
        if "fd" not in app.config: app.config["fd"] = None
        app.config["cmd"] = "bash"

        if app.config["child_pid"]:
            return

        (child_pid, fd) = pty.fork()
        
        if child_pid == 0:
            subprocess.run(app.config["cmd"])
        else:
            app.config["fd"] = fd
            app.config["child_pid"] = child_pid
            set_winsize(fd, 50, 50)
            cmd = " ".join(shlex.quote(c) for c in app.config["cmd"])
            socketio.start_background_task(target=read_and_forward_pty_output)
        
    def ptyinput(self, wiz, data):
        session = wiz.model("portal/season/session").use()
        if session.get("role") != "admin":
            return

        app = wiz.server.app.flask
        if app.config["fd"]:
            os.write(app.config["fd"], data["input"].encode())

    def resize(self, wiz, data):
        session = wiz.model("portal/season/session").use()
        if session.get("role") != "admin":
            return

        app = wiz.server.app.flask
        if app.config["fd"]:
            set_winsize(app.config["fd"], data["rows"], data["cols"])
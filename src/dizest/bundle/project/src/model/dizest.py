import os
import sys
import season
import json
import urllib
import requests
import dizest

class Broker:
    def __init__(self, namespace, io_host, io_namespace):
        self.namespace = namespace
        self.io_namespace = io_namespace
        self.io = wiz.server.app.socketio

    def __call__(self, logs):
        namespace = self.namespace
        io_namespace = self.io_namespace
        for log in logs:
            try:
                mode = log['mode']
                wpid = log['workflow_id']
                to = self.namespace + "-" + wpid
                io = wiz.server.app.socketio
                io.emit(mode, log, to=to, namespace=io_namespace, broadcast=True)
            except Exception as e:
                pass

class Model:
    VERSION = "v2022.10.18.1547"

    def __init__(self, name):
        self.name = name
        self.branch = branch = wiz.branch()
        self.namespace = f"/wiz/app/{branch}/component.dizest.workflow"
        
    @classmethod
    def load(cls, name):
        return cls(name)

    def server(self, user=None, info=False):
        name = self.name
        if user is None:
            if wiz.session.has("id") == False:
                return None
            if wiz.session.get("id") is None:
                return None
            user = wiz.session.get("id")

        config = wiz.config("config")
        
        server_options = dict()
        server_options['user'] = user
        server_options['cwd'] = f'/home/{user}'
        if config.cwd:
            server_options['cwd'] = config.cwd(user)
        
        if config.executable:
            server_options['executable'] = config.executable

        if config.spawner_class:
            server_options['spawner_class'] = dizest.spawner.SudoSpawner

        server = dizest.server(name, **server_options)

        host = config.host
        if config.host is None:
            host = urllib.parse.urlparse(wiz.request.request().base_url)
            host = f"{host.scheme}://{host.netloc}"

        if server.config('broker') is None:
            broker = Broker(self.name, host, self.namespace)
            server.config(broker=broker)

        kernelspecs = [dict(name="base", title="python", kernel="$EXECUTABLE $LIBSPEC_PATH/python/kernel.py $PORT", package_install="$EXECUTABLE -m pip install --upgrade $PACKAGE", package_list="$EXECUTABLE -m pip freeze", language="python")]
        if config.kernelspec:
            kernelspecs = config.kernelspec
        server.clear_kernelspec()
        for kernelspec in kernelspecs:
            server.set_kernelspec(**kernelspec)

        # just return to server, not start
        if info:
            return server

        if server.is_running() == False:
            server.start()

        return server
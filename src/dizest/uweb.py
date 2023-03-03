import sys
import signal
import os
import flask
import logging

from dizest.server.drive import DriveServer
from dizest.server.workflow import WorkflowServer
from dizest.config.uweb import uWebConfig

class uWeb:
    def __init__(self, **config):
        self.events = dict()
        self.config = uWebConfig(config)
        self.flask = flask
        self.app = app = flask.Flask('__main__', static_url_path='')
        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.logger.disabled = True
        os.environ["WERKZEUG_RUN_MAIN"] = "false"
        self.bind()

    def on(self, eventname, fn):
        self.events[eventname] = fn
        return self

    def query(self, key=None, default=None):
        data = dict(flask.request.values)
        if key is None: return data
        if key in data: return data[key]
        return default

    def bind(self):
        app = self.app

        @app.route('/health', methods=['GET'])
        def health():
            return {'code': 200}

        DriveServer(self).bind()
        WorkflowServer(self).bind()

    def start(self):
        host = self.config.host
        port = self.config.port
        self.app.run(host=host, port=port, threaded=False)

import os
import flask
import logging
import dizest
from dizest.api.binding.workflow import WorkflowBinding
from dizest.api.binding.flow import FlowBinding
from dizest.api.binding.drive import DriveBinding
from dizest.base.config import BaseConfig

class Config(BaseConfig):
    DEFAULT_VALUES = {
        'cwd': (None, os.getcwd()),
        'max_log_size': (int, 50),
        'host': (str, '127.0.0.1'),
        'port': (int, 8000)
    }

class Serve:
    def __init__(self, **config):
        self.config = Config(config)
        self.workflow = dizest.Workflow(dict(apps=[], flow=[]), **self.config)
        self.flask = flask
        self.app = app = flask.Flask('__main__', static_url_path='')
        log = logging.getLogger('werkzeug')
        log.disabled = True
        app.logger.disabled = True
        os.environ["WERKZEUG_RUN_MAIN"] = "false"
        self.bind()

    def on(self, name, fn):
        self.workflow.on(name, fn)

    def query(self, key=None, default=None):
        data = dict(flask.request.values)
        if key is None: return data
        if key in data: return data[key]
        return default

    def bind(self):
        app = self.app

        @app.errorhandler(Exception)
        def handle_exception(e):
            return {"code": 500, "data": str(e)}

        @app.route('/health', methods=['GET'])
        def health():
            return {'code': 200}
        
        WorkflowBinding(self).bind()
        FlowBinding(self).bind()
        DriveBinding(self).bind()
        
    def run(self):
        host = self.config.host
        port = self.config.port
        self.app.run(host=host, port=port, threaded=False)

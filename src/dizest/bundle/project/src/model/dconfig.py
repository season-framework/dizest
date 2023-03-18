import os
import urllib
from season.util.std import stdClass

class dConfig:

    def user(self):
        session = wiz.model("portal/season/session").use()
        return session.get("id")

    def kernel_user(self):
        session = wiz.model("portal/season/session").use()
        user = session.get("id")
        role = session.get("role")
        if role == 'admin':
            return 'root'
        return user

    def channel(self, zone=None, workflow_id=None, **data):
        data['zone'] = zone
        data['workflow_id'] = workflow_id
        user = self.user()
        channel = user + "-" + data['zone'] + "-" + data['workflow_id']
        return channel

    def cwd(self):
        return os.path.expanduser('~')

    def kernel(self):
        fs = self.configfs()
        kernel = fs.read.json("kernel.json", [])
        if len(kernel) == 0:
            kernel.append(dict(name="base"))
        return kernel

    def dsocket(self):
        branch = wiz.branch()

        host = urllib.parse.urlparse(wiz.request.request().base_url)
        host = f"{host.scheme}://{host.netloc}"

        fs = self.configfs()
        config = fs.read.json("config.json", dict())
        if 'dsocket_host' in config:
            host = config['dsocket_host']

        dsocket_api = f"{host}/wiz/app/{branch}/portal.dizest.workflow.ui"
        return dsocket_api

    def cron_host(self):
        fs = self.configfs()
        config = fs.read.json("config.json", dict())
        if 'cron_host' in config:
            return config['cron_host']
        return "http://127.0.0.1:3000"

    def getWorkflowSpec(self, workflow_id, zone=None):
        user = self.user()
        db = wiz.model("portal/season/orm").use("workflow")
        sfspec = db.get(id=workflow_id, user_id=user)
        return sfspec

    def updateWorkflowSpec(self, workflow_id, data, zone=None):
        db = wiz.model("portal/season/orm").use("workflow")
        user = self.user()
        db.update(data, id=workflow_id, user_id=user)
    
    def configfs(self):
        return wiz.workspace().fs(wiz.server.path.root, "config", "dizest")
    
    def databaseConfig(self):
        fs = self.configfs()
        database = fs.read.json("database.json", dict(type="sqlite", path="dizest.db"))
        if 'port' in database:
            database['port'] = int(database['port'])
        return database

Model = dConfig()
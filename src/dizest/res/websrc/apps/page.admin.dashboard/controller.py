import season
import dizest

import os
import time
import psutil
import platform
import resource

db = season.stdClass()
db.app = wiz.model("dizest/db").use("app")
db.workflow = wiz.model("dizest/db").use("workflow")
db.user = wiz.model("dizest/db").use("user")

config = wiz.model("dizest/config").load()
process = psutil.Process(os.getpid())

data = season.stdClass()
data.deploy = season.stdClass()
data.deploy.dizest_version = dizest.version
data.deploy.wiz_version = season.version
data.deploy.python_version = platform.python_version()
data.deploy.database = config.db.type
data.deploy.pid = os.getpid()

data.system = season.stdClass()
data.system.uptime = int(time.time() - psutil.boot_time())
data.system.started = int(time.time() - process.create_time())

data.system.memory = season.stdClass()
data.system.memory.usage = psutil.virtual_memory().used
data.system.memory.dizest_usage = process.memory_info().rss
data.system.memory.total = psutil.virtual_memory().total

data.system.cpu = season.stdClass()
data.system.cpu.count = psutil.cpu_count()
data.system.cpu.usage = psutil.cpu_percent()
data.system.cpu.dizest_usage = process.cpu_percent()

data.system.disk = season.stdClass()
hdd = psutil.disk_usage('/')
data.system.disk.total = hdd.total
data.system.disk.used = hdd.used
data.system.disk.free = hdd.free

children = process.children(recursive=True)
processes = []
for child in children:
    obj = dict()
    obj['status'] = child.status()
    obj['pid'] = child.pid
    obj['parent'] = child.parent().pid
    obj['cmd'] = child.name()
    obj['time'] = int(time.time() - child.create_time())
    processes.append(obj)

data.process = season.stdClass()
data.process.children = processes

data.dizest = season.stdClass()
data.dizest.users = db.user.count()
data.dizest.workflows = db.workflow.count()
data.dizest.apps = db.app.count()

kwargs['data'] = dict(data)
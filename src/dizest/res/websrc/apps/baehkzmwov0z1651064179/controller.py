import os
import psutil
current_process = psutil.Process()
children = current_process.children(recursive=True)
processes = []
for child in children:
    obj = dict()
    obj['pid'] = child.pid
    obj['parent'] = child.parent().pid
    obj['cmd'] = " ".join(child.cmdline())
    processes.append(obj)

kwargs['processes'] = processes
kwargs['processid'] = os.getpid()

config = wiz.model("dizest/config").load()
kwargs['config'] = config
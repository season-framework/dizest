import multiprocessing as mp
import time
import traceback
from io import StringIO 
import sys

mp.set_start_method('fork')
processes = {}

class process:
    def __init__(self, namespace, sync=False, logger=print):
        self.namespace = namespace
        self.sync = sync
        self.logger = logger

    def __call__(self, func):
        def decorator(*args, **kwargs):
            return self.run(func, args, kwargs)
        return decorator

    def fnwrap(self, q, func, args, kwargs):
        result = None
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            stderr = traceback.format_exc()
            if self.sync:
                q.put((e, stderr))
            else:
                self.logger(stderr)

        if self.sync:
            q.put((None, result))

    def is_running(self):
        namespace = self.namespace
        if namespace in processes:
            if processes[namespace].exitcode is not None:
                del processes[namespace]
                return False
            return True
        return False

    def run(self, func, args, kwargs):
        namespace = self.namespace

        if namespace in processes:
            if processes[self.namespace].exitcode is not None:
                del processes[namespace]
            else:
                raise Exception("exists running process")
        
        q = mp.Queue()
        p = mp.Process(target=self.fnwrap, args=[q, func, args, kwargs])
        p.name = namespace

        processes[namespace] = p
        p.start()

        if self.sync:
            err, result = q.get()
            p.join()

            if err is not None:
                raise err

            del processes[namespace]
            return result

    def kill(self):
        namespace = self.namespace

        if namespace not in processes:
            return 
        p = processes[namespace]
        try: p.kill()
        except: pass

        while p.exitcode is None:
            continue

        del processes[namespace]
        
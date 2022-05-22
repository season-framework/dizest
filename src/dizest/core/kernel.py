from dizest import util
from dizest.core.obj import Workflow

import json
import os
import multiprocessing as mp
import psutil
import signal
import traceback

# kernel manager
def _manager(q):
    q.send(str(os.getpid()))

    msg = json.loads(q.recv())
    mode = msg['mode']
    data = msg['data']
 
    workflow = Workflow(data['package'], **data['opts'])
    kernel = workflow.kernel()

    kernel.event_start()

    is_stopped = False
    while True:
        try:
            msg = json.loads(q.recv())
            mode = msg['mode']
            if 'data' in msg: data = msg['data']
            else: data = None

            if mode == 'wpdata':
                workflow.update(data['package'], **data['opts'])
            elif mode == 'run':
                if is_stopped == False:
                    workflow.status.set(status='running')
                    workflow.status.send()
                    kernel.event_run(data)
                else:
                    workflow.flow(data).status.set(status="ready", code=0, message="")
                    workflow.flow(data).status.send()
            elif mode == 'sync':
                try:
                    workflow.flow(data).output.save()
                except:
                    pass
                q.send(data)
            elif mode == 'stop':
                is_stopped = False
        except KeyboardInterrupt:
            is_stopped = True
            workflow.flow().output.clear()
            workflow.flow().status.set(status="ready", code=0, message="")
            workflow.flow().status.send()
            kernel.event_stop()
        except Exception as e:
            pass

        try:
            workflow.status.set(status='stop')
            workflow.status.send()
        except:
            pass
        
class Base:
    def __init__(self, workflow):
        self.workflow = workflow
        self.init()

    # init kernel
    def init(self):
        self.p = None
        self.q = None
        self.workflow.status.clear()

    def __del__(self):
        self.kill()

    # interface functions
    def event_start(self):
        pass

    def event_stop(self):
        pass

    def event_run(self, flow_id):
        pass

    # kernel api functions

    # start process
    def start(self):
        if self.p is not None:
            raise Exception("Process already running")

        workflow = self.workflow
        self.init()
        
        ctx = mp.get_context(workflow.opts.kernel_mode)
        if workflow.opts.kernel_mode == 'spawn':
            ctx.set_executable(workflow.opts.kernel_env)
        sender, receiver = mp.Pipe()
        self.p = ctx.Process(target=_manager, args=(receiver,))
        self.p.start()
        self.q = sender
        cpid = sender.recv()
        self.update()

    # send action to process
    def send(self, mode, data=None):
        try:
            msg = dict()
            msg['mode'] = mode
            msg['data'] = data
            msg = json.dumps(msg, default=util.string.json_default)
            self.q.send(msg)
        except Exception as e:
            pass

    # stop process
    def stop(self):
        childpid = self.p.pid
        child = psutil.Process(childpid)
        child.send_signal(signal.SIGINT)

        # cancel waiting works signal
        self.send("stop")
        return True
        
    def kill(self):
        try:
            self.p.kill()
            self.p.join()
        except:
            pass
        processstate = self.is_alive()
        if processstate:
            return False
        self.init()

        workflow = self.workflow
        for flow_id in workflow.flows():
            flow = workflow.flow(flow_id)
            flow.status.set(status="ready", code=0, message="")
            flow.status.send()
        return True

    # update kernel data to process
    def update(self):
        if self.p is not None:
            wpdata = dict(self.workflow.info())
            self.send("wpdata", wpdata)

    # run dizest code
    def run(self, flow_id):
        if self.p is None:
            self.init()
            raise Exception("no running process")
        if self.is_alive() == False:
            self.init()
            raise Exception("no running process")

        flow = self.workflow.flow(flow_id)
        flow.status.set(code=0, status='pending', message='')
        flow.status.send()
        self.send("run", flow_id)
        return self

    # sync output using pickle
    def sync(self, flow_id):
        if self.q is None:
            return
        self.send("sync", flow_id)
        fid = self.q.recv()
        flow = self.workflow.flow(fid)
        flow.output.load()

    # check process is alive
    def is_alive(self):
        try:
            if self.p is None:
                return False
            return self.p.is_alive()
        except:
            return False

class Single(Base):
    def event_start(self):
        pass

    def event_run(self, flow_id):
        flow = self.workflow.flow(flow_id)
        flow.run()

    def event_stop(self):
        pass
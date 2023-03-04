class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, data, io):
        dconfig = wiz.model("portal/dizest/dconfig")
        channel = dconfig.channel(**data)
        io.join(channel)
    
    def leave(self, flask, data, io):
        io.leave(data)

    def wplog(self, data, io):
        branch = wiz.branch()
        namespace = f"/wiz/app/{branch}/component.dizest.workflow"

        for log in data:
            event = log['event']
            workflow_id = log['workflow_id']
            to = log['channel']
            del log['channel']
            del log['workflow_id']
            del log['event']
            io.emit(event, log, to=to, namespace=namespace, broadcast=True)

    def disconnect(self, flask, io):
        pass
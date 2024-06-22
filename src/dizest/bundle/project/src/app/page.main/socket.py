class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, data, io):
        config = wiz.model("portal/dizest/config")
        wiz.session = wiz.model("portal/season/session")
        zone = data['zone']
        workflow_id = data['workflow_id']

        if config.acl(wiz, zone) == False:
            return

        Kernel = wiz.model("portal/dizest/kernel")
        config = wiz.model("portal/dizest/config")
        kernel = Kernel(zone)
        workflow = kernel.workflow(workflow_id)
        status = workflow.status()
        io.join(workflow.spawner_id())
    
    def wplog(self, data, io):
        project = wiz.project()
        socketNamespace = f"/wiz/app/{project}/page.main"

        for log in data:
            event = log['event']
            workflow_id = log['workflow_id']
            to = log['namespace']
            del log['namespace']
            del log['workflow_id']
            del log['event']
            io.emit(event, log, to=to, namespace=socketNamespace)

    def disconnect(self, flask, io):
        pass
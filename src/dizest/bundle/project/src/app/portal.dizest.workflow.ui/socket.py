class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, data, io):
        KernelClass = wiz.model("portal/dizest/kernel")
        config = wiz.model("portal/dizest/config")
        kernel_id = config.kernel_id(**data)
        kernel = KernelClass.getInstance(kernel_id)
        if kernel is None:
            return
        
        namespace = data['namespace']
        workflow = kernel.workflow(namespace)
        status = workflow.status()
        
        if status is None:
            return

        io.join(namespace)
    
    def wplog(self, data, io):
        branch = wiz.branch()
        socketNamespace = f"/wiz/app/{branch}/component.dizest.workflow"

        for log in data:
            event = log['event']
            workflow_id = log['workflow_id']
            to = log['namespace']
            del log['namespace']
            del log['workflow_id']
            del log['event']
            io.emit(event, log, to=to, namespace=socketNamespace, broadcast=True)

    def disconnect(self, flask, io):
        pass
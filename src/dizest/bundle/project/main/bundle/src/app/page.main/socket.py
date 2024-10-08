class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, data, io):
        wiz.session = wiz.model("portal/season/session")
        struct = wiz.model("portal/dizest/struct")
        config = struct.config
        try:
            config.acl()
        except:
            return
        io.join(data)

    def leave(self, data, io):
        wiz.session = wiz.model("portal/season/session")
        struct = wiz.model("portal/dizest/struct")
        config = struct.config
        try:
            config.acl()
        except:
            return
        io.leave(data)
    
    def wplog(self, data, io):
        project = wiz.project()
        socketNamespace = f"/wiz/app/{project}/page.main"

        for log in data:
            event = log['event']
            to = log['id']
            io.emit(event, log, to=to, namespace=socketNamespace)

    def disconnect(self, flask, io):
        pass
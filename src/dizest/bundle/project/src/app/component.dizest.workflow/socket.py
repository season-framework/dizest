class Controller:
    def __init__(self, server):
        self.server = server

    def connect(self):
        pass

    def join(self, data, io):
        session = wiz.model("session").use()
        user = session.get("id")
        namespace = data['namespace']
        workflow_id = data['workflow_id']
        room = f"{namespace}-{user}-{workflow_id}"
        io.join(room)

    def leave(self, flask, data, io):
        io.leave(data)

    def disconnect(self, flask, io):
        pass
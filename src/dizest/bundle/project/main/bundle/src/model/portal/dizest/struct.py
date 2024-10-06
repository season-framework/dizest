Kernel = wiz.model("portal/dizest/struct/kernel")
Config = wiz.model("portal/dizest/struct/config")

class Model:
    config = Config

    def __init__(self):
        if 'dizest' not in wiz.server.app: 
            wiz.server.app.dizest = season.util.stdClass()
        
        self.kernel = Kernel(self)

    def cache(self):
        return wiz.server.app.dizest
    
Model = Model()
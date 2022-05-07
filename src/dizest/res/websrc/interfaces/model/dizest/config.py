import os
import season

BASEPATH = os.path.realpath(season.core.PATH.PROJECT + "/..")

class Model:
    @staticmethod
    def load():
        try:
            fs = wiz.model("dizest/storage").use(BASEPATH)
            config = fs.read.json("dizest.json")
            config = season.stdClass(config)
            return config
        except:
            return None
    
    @staticmethod
    def status():
        config = Model.load()
        if config is None:
            return False
        try:
            db = wiz.model("dizest/db").use("user")
            count = db.count()
            if count == 0:
                return False
        except:
            return False
        return True

    def update(config):
        fs = wiz.model("dizest/storage").use(BASEPATH)
        config = fs.write.json("dizest.json", config)

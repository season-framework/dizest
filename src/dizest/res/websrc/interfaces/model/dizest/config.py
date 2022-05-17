import os
import season
import dizest

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

    @staticmethod
    def version():
        config = Model.load()
        if config is None:
            return False

        try:
            current = config['version']
            current_index = dizest.versions.index(current)
            target = dizest.version
            target_index = dizest.versions.index(target)

            if current == target:
                return True

            dbchanges = []
            for i in range(target_index - current_index):
                pos = current_index + i + 1
                vcheck = dizest.versions[pos]
                try:
                    wiz.model(f"dizest/orm/{vcheck}/base")
                    dbchanges.append(vcheck)
                except:
                    pass
            
            config = Model.load()
            if len(dbchanges) == 0:
                config['version'] = dizest.version
                Model.update(config)
                return True
        except:
            pass

        # TODO: db update page        
        return True

    @staticmethod
    def update(config):
        fs = wiz.model("dizest/storage").use(BASEPATH)
        config = fs.write.json("dizest.json", config)

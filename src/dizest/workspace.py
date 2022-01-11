import dizest

class workspace:
    def __init__(self, basepath, **config):
        self.BASEPATH = basepath
        self.storage = dizest.util.storage(basepath)
        self.data = self.storage.use("data")
        self.config = dizest.core.config(**config)
        package = self.storage.read.json("package.dz", {})
        self.package = dizest.core.package(**package)
        self.dataset = dizest.dataset(self)
        self.snapshot = dizest.snapshot(self)
        self.stage = dizest.stage(self)

    def update(self, **kwargs):
        for key in kwargs:
            self.package.set(key, kwargs[key])
        package = self.package.to_dict()
        self.storage.write.json("package.dz", package, indent=4)

    def get(self, key=None):
        if key is None:
            package = self.package.to_dict()
            return package
        return self.package.get(key)

    def build(self):
        stage = self.stage
        stage.build()

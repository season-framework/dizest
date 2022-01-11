import json
import dizest

class obj:
    def __init__(self, workspace, stage_id):
        self.workspace = workspace
        package = workspace.storage.use(f"stage/{stage_id}").read.json("stage.dz", {"id": stage_id, "title": stage_id, "code": ""})
        if 'code' not in package:
            package['code'] = ""
        self.package = dizest.util.stdClass(**package)
        self.id = stage_id
        self.env = None
        self.stroage = workspace.storage.use(f"storage/{stage_id}")

    def __call__(self, data=None, **opts):
        return self.process(data, **opts)
    
    def load(self):
        self.workspace.stage.current = self
        storage = self.workspace.storage.use(f"stage/{self.package.id}")
        code = storage.read("code.py", "")
        compiler = dizest.util.compiler()
        compiler.set_logger(self.workspace.config.logger())
        compiler.set(dizest=self.workspace)
        self.env = compiler.compile(code)
        return self

    def process(self, data=None, **opts):
        self.load()
        env = self.env
        
        data_index = -1
        if data is None:
            data_index = self.workspace.stage.dataset_index
            if data_index >= 0 and len(self.workspace.dataset) > 0:
                data = self.workspace.dataset[data_index]

        result = env['process'](data=data, **opts)
        if data_index >= 0:
            self.workspace.dataset[data_index] = result

        return result

    def set(self, **kwargs):
        for key in kwargs:
            self.package[key] = kwargs[key]

        updated = False
        for i in range(len(self.workspace.package.stage)):
            stage = self.workspace.package.stage[i]
            if stage['id'] == self.package.id:
                self.workspace.package.stage[i] = dict(self.package)
                updated = True
        
        if updated is False:
            self.workspace.package.stage.append(dict(self.package))

        storage = self.workspace.storage.use(f"stage/{self.package.id}")
        storage.write.json("stage.dz", self.package, indent=4)
        storage.write("code.py", self.package.code)

        self.workspace.package.set('stage', self.workspace.package.stage)
        self.workspace.update()

        return self

    def get(self, key=None, default=None):
        if key is None:
            return dict(self.package)
        if key in self.package:
            return self.package[key]
        return default

class stage:
    def __init__(self, workspace):
        self.workspace = workspace
        self.storage = storage = workspace.storage.use("stage")
        self.stages = stages = workspace.package.stage
        self.__cached__ = dict()
        self.current = None
        self.dataset_index = -1

        storage.remove()
        for stage in stages:
            if 'code' not in stage:
                stage['code'] = ""
            stage_id = stage['id']
            storage.write.json(f"{stage_id}/stage.dz", stage, indent=4)
            storage.write(f"{stage_id}/code.py", stage['code'])

    def __getattr__(self, key):
        if key in self.__cached__:
            return self.__cached__[key]
        self.__cached__[key] =  obj(self.workspace, key)
        return self.__cached__[key]

    def __getitem__(self, index):
        if type(index) == int:
            if index >= len(self.stages) or index < 0:
                raise IndexError
            if 'id' not in self.stages[index]:
                raise KeyError
            index = self.stages[index]['id']
        return self.__getattr__(index)

    def __len__(self):
        return len(self.stages)

    def get(self, key):
        return self.__getitem__(key)
    
    def set(self, index):
        self.dataset_index = index
        return self

    def process(self, index):
        self.set(index)
        for i in range(len(self)):
            if i == 0: continue
            self[i]()
        return self.workspace.dataset[index]
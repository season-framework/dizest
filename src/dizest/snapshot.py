import dizest

class snapshot:
    def __init__(self, workspace):
        self.workspace = workspace
        self.__data__ = dizest.util.stdClass()
        self.__data__.cached = dict()
        self.__current__ = None

    def load(self, snapshot_id):
        data = snapshot(self.workspace)
        data.__current__ = snapshot_id
        data.__indexes__ = data.fs().read.pickle("__indexes__", list())
        data.__index__ = 0
        return data
        
    def fs(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        return self.workspace.storage.use(f"snapshot/{self.__current__}")

    def clear(self):
        if self.__current__ is None:
            self.workspace.storage.use("snapshot").remove()
        else:
            self.fs().remove()

    def save(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        self.workspace.dataset.save() # save dataset
        fs = self.fs()
        fs.remove() # remove previous snapshot
        copypath = self.workspace.storage.use("dataset").abspath()
        fs.copy(copypath, "") # copy dataset
        return self

    def __getitem__(self, index):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")

        key = self.__indexes__[index]

        if type(key) == list:
            res = []
            for idx in key:
                res.append(self.__getitem__(idx))
            return res

        if key in self.__data__.cached:
            return self.__data__.cached[key]

        fs = self.fs()
        item = fs.read.pickle(str(key), ValueError)

        if item is not ValueError:
            self.__data__.cached[key] = item

        return item
    
    def __iter__(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")

        self.__index__ = 0
        return self

    def __next__(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")

        if self.__index__ >= len(self):
            raise StopIteration
        item = self.__getitem__(self.__index__)
        self.__index__ += 1
        return item

    def __len__(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        return len(self.__indexes__)

    def last(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        return self.__indexes__[-1]

    def tolist(self):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        res = []
        for i in range(len(self)):
            res.append(self[i])
        return res

    def exists(self, index=None):
        if self.__current__ is None: raise Exception("dizest: Snapshot not defined")
        if index is None:
            return self.fs().isdir()
        key = self.__indexes__[index]
        if key in self.__data__.cached:
            return True
        fs = self.fs()
        if fs.isfile(str(key)):
            return True
        return False

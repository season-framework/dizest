import datetime
import dizest as sd

# - mode: default, stream

class data:
    def __init__(self, fs):
        self.fs = fs
        self.__data__ = sd.util.stdClass()
        self.__data__.deleted = dict()
        self.__data__.updated = dict()
        self.__data__.cached = dict()

        self.__indexes__ = fs.read.pickle("__indexes__", list())

        self.__index__ = 0

    def set(self, prev):
        self.__indexes__ = prev.__indexes__

    def __update__(self, key, value):
        if key in self.__data__.deleted: 
            del self.__data__.deleted[key]
        self.__data__.updated[key] = value
        self.__data__.cached[key] = value

    def __getitem__(self, index):
        if index not in self.__indexes__:
            raise IndexError

        key = self.__indexes__[index]

        if type(key) == list:
            res = []
            for idx in key:
                res.append(self.__getitem__(idx))
            return res

        if key in self.__data__.updated:
            return self.__data__.updated[key]

        if key in self.__data__.cached:
            return self.__data__.cached[key]

        fs = self.fs
        item = fs.read.pickle(str(key), ValueError)

        if item is not ValueError:
            self.__data__.cached[key] = item

        return item

    def __setitem__(self, index, value):
        if index < 0:
            raise IndexError
        key = self.__indexes__[index]
        self.__update__(key, value)

    def __delitem__(self, index):
        key = self.__indexes__[index]
        if key in self.__data__.updated: del self.__data__.updated[key]
        if key in self.__data__.cached: del self.__data__.cached[key]
        self.__data__.deleted[key] = True
        
        del self.__indexes__[index]
    
    def __iter__(self):
        self.__index__ = 0
        return self

    def __next__(self):
        if self.__index__ >= len(self):
            raise StopIteration
        item = self.__getitem__(self.__index__)
        self.__index__ += 1
        return item

    def __len__(self):
        return len(self.__indexes__)

    def updated(self):
        return len(self.__data__.updated)

    def save(self):
        fs = self.fs

        updated = self.__data__.updated
        for key in updated:
            item = updated[key]
            if item is not None:
                fs.write.pickle(str(key), item)
            self.__data__.cached[key] = item
        self.__data__.updated = dict()

        deleted = self.__data__.deleted
        for key in deleted:
            try:
                fs.delete(str(key))
                del self.__data__.cached[key]
            except:
                pass
        self.__data__.deleted = dict()

        fs.write.pickle("__indexes__", self.__indexes__)

    def revert(self):
        self.__data__.updated = dict()
        self.__data__.cached = dict()
        self.__data__.deleted = dict()

        self.__indexes__ = fs.read.pickle("__indexes__", list())

    def push(self, *args):
        self.append(**args)

    def append(self, *args):
        for arg in args:
            if len(self.__indexes__) == 0: index = 0
            else: index = self.__indexes__[-1] + 1
            self.__update__(index, arg)
            self.__indexes__.append(index)

    def remove(self, index):
        self.__delitem__(index)

    def last(self):
        return self.__indexes__[-1]

    def tolist(self):
        res = []
        for i in range(len(self)):
            res.append(self[i])
        return res

    def exists(self, index=None):
        if index is None:
            return self.fs.isdir()
        key = self.__indexes__[index]
        if key in self.__data__.updated:
            return True
        if key in self.__data__.cached:
            return True
        fs = self.fs
        if fs.isfile(str(key)):
            return True
        return False
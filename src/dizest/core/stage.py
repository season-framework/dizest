import datetime
import traceback

import dizest as sd
from dizest.core import data as sddata

class _data:
    def __init__(self, stage):
        self.__stage__ = stage
        self.__cache__ = dict()
        self.__build__ = None

    def save(self):
        if self.__build__ is not None:
            self.__build__.save()
        
        for namespace in self.__cache__:
            cache = self.__cache__[namespace]
            cache.save()

    def __call__(self, namespace=None):
        return self.get(namespace=namespace)

    def __getitem__(self, index):
        data = self.get()
        return data[index]

    def __setitem__(self, index, value):
        data = self.get()
        data.__setitem__(index, value)

    def __delitem__(self, index):
        data = self.get()
        data.__delitem__(index)

    def __len__(self):
        data = self.get()
        return len(data)

    def get(self, namespace=None):
        stage = self.__stage__

        if namespace is None:
            namespace = stage.namespace
        
        if namespace in self.__cache__:
            return self.__cache__[namespace]

        fs = stage.__dataset__.__storage__.use(f"stage/{stage.namespace}")
        item = sddata(fs)
        self.__cache__[stage.namespace] = item
        return item

    def build(self):
        if self.__build__ is not None:
            return self.__build__
        
        stage = self.__stage__
        fs = stage.__dataset__.__storage__.use(f"stage/build")
        item = sddata(fs)
        self.__build__ = item
        return item

    def prev(self):
        stage = self.__stage__
        index = stage.index()
        index = index - 1

        if index < 0:
            return self.build()

        namespaces = stage.namespaces()
        ns = namespaces[index]
        return self.get(namespace=ns)

class stage:
    def __init__(self, dataset):
        self.__dataset__ = dataset
        self.__index__ = None
        self.namespace = None
        self.__current__ = None

        self.data = _data(self)

    def __getitem__(self, index):
        return self.get(index)

    def __iter__(self):
        self.__index__ = -1
        return self

    def __next__(self):
        self.__index__ += 1
        if self.__index__ >= len(self):
            raise StopIteration

        stage = self.__getitem__(self.__index__)
        return stage

    def __len__(self):
        return len(self.__dataset__.__regist__)

    def __call__(self, index=None, reload=False):
        if self.__index__ is None:
            return self.build()
        return self.process(index, reload=reload)
        
    def get(self, index=None):
        if index == 'build': index = None
        if index is None:
            self.__index__ = None
            self.namespace = "build"
            self.__current__ = self.__dataset__.__builder__
            return self

        # if index is namespace, transform to list index
        if type(index) == str:
            namespaces = self.namespaces()
            if index in namespaces:
                index = namespaces.index(index)
            else:
                raise IndexError

        # find stage
        self.__index__ = index
        self.__current__ = self.__dataset__.__regist__[index]
        self.namespace = self.__current__['namespace']

        return self

    def last(self):
        return self[-1]

    def build(self):
        try:
            self.get()
            data = self.data.build()
            process = self.__current__['process']().process
            process(data)
            return data
        except Exception as e:
            msg = traceback.format_exc()
            self.__dataset__.logger(msg)
            raise e
        
    def process(self, index=None, reload=False):
        try:
            prev = self.data.prev()
            data = self.data.get()
            data.set(prev)
            
            process = self.__current__['process']().process

            if index is None:
                for item in prev:
                    item = process(item)
                return prev

            if reload == False and data.exists(index):
                return data
            
            item = prev[index]
            data[index] = process(item)
            return data
        except Exception as e:
            msg = traceback.format_exc()
            self.__dataset__.logger(msg)
            raise e

    def namespaces(self):
        return [x['namespace'] for x in self.__dataset__.__regist__]

    def has(self, namespace):
        namespaces = self.namespaces()
        if namespace in namespaces:
            return True
        return False

    def index(self):
        return self.__index__

    def save(self):
        self.data.save()

    def storage(self):
        if self.namespace is None:
            return None
        return self.__dataset__.__storage__.use(f"stage/{self.namespace}/storage")

from abc import *

class BaseSpawner(metaclass=ABCMeta):
    def __init__(self, **meta):
        self.name = 'base'
        self.meta = dict(status='stop')
        self.setMeta(**meta)

    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def getMeta(self, key, default=None):
        if key in self.meta:
            return self.meta[key]
        return default
    
    def setMeta(self, **kwargs):
        for key in kwargs:
            self.meta[key] = kwargs[key]

    def setKernelSpec(self, kernelspec):
        self.setMeta('kernelspec', kernelspec)
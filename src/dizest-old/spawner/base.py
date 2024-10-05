from abc import *

class BaseSpawner(metaclass=ABCMeta):
    def __init__(self, **meta):
        self.name = 'base'
        self.meta = dict(status='stop')
        self.set(**meta)

    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass

    def restart(self):
        self.stop()
        self.start()

    def get(self, key, default=None):
        if key in self.meta:
            return self.meta[key]
        return default
    
    def set(self, **kwargs):
        for key in kwargs:
            self.meta[key] = kwargs[key]

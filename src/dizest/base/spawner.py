from abc import *
from dizest.base.config import BaseConfig

class BaseSpawner(metaclass=ABCMeta):
    NAMESPACE = 'base'
    CONFIGCLASS = BaseConfig

    def __init__(self, **kwargs):
        self.config = self.CONFIGCLASS(kwargs)

    @abstractmethod
    def start(self):
        pass
    
    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def uri(self):
        pass

    @abstractmethod
    def port(self):
        pass
    
    @abstractmethod
    def status(self):
        pass

    def restart(self):
        self.stop()
        self.start()

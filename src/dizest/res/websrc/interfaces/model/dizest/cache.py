import season

CACHE_NAMESPACE = 'dizest_cache'

class Model:
    def __init__(self, namespace):
        self.framework = season
        self.namespace = namespace
        if CACHE_NAMESPACE not in self.framework.cache:
            self.framework.cache[CACHE_NAMESPACE] = season.stdClass()
        if namespace not in self.framework.cache[CACHE_NAMESPACE]:
            self.framework.cache[CACHE_NAMESPACE][namespace] = season.stdClass()
    
    def keys(self):
        namespace = self.namespace
        keys = []
        cache = self.framework.cache[CACHE_NAMESPACE][namespace]
        for key in cache:
            keys.append(key)
        return keys

    def has(self, key):
        namespace = self.namespace
        cache = self.framework.cache[CACHE_NAMESPACE][namespace]
        if key in cache:
            return True
        return False
    
    def delete(self, key):
        namespace = self.namespace
        if self.has(key):
            del self.framework.cache[CACHE_NAMESPACE][namespace][key]
    
    def set(self, key, value):
        namespace = self.namespace
        self.framework.cache[CACHE_NAMESPACE][namespace][key] = value
    
    def get(self, key, default=None):
        namespace = self.namespace
        if key in self.framework.cache[CACHE_NAMESPACE][namespace]:
            return self.framework.cache[CACHE_NAMESPACE][namespace][key]
        return default

    def clear(self):
        namespace = self.namespace
        self.framework.cache[CACHE_NAMESPACE][namespace] = season.stdClass()

    @classmethod
    def use(cls, namespace):
        return cls(namespace)
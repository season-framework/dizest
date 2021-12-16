import dizest as sd

class config:
    def __init__(self, **kwargs):
        self.data = sd.util.stdClass(**kwargs)
        
        self.defaults = sd.util.stdClass()
        self.defaults.cache = "memory"

    def __getattr__(self, key):
        def fn(value=None):
            if value is None:
                value = self.data[key]
                if value is None:
                    value = self.defaults[key]
                return value

            self.data[key] = value
            return self.data[key]
        return fn
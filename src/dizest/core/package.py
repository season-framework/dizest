import dizest

class package:
    def __init__(self, **kwargs):
        self.data = dizest.util.stdClass(**kwargs)
        self.defaults = dizest.util.stdClass()
        self.defaults.stage = list()

    def __getattr__(self, key):
        value = self.data[key]
        if value is None:
            value = self.defaults[key]
        if type(value) == dict:
            return package(**value)
        return value

    def get(self, key):
        return self.__getattr__(key)()

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def to_dict(self):
        return dict(self.data)
import requests

class Model:
    def __init__(self, kernel):
        self.kernel = kernel

    def __request__(self, fnname, **kwargs):
        kwargs["url"] = self.kernel.uri() + "/drive/" + fnname
        kwargs["allow_redirects"] = False
        return requests.request(**kwargs)

    def ls(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"ls/{path}", method="GET", timeout=3)

    def create(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"create/{path}", method="POST", data=data, timeout=3)

    def rename(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"rename/{path}", method="POST", data=data, timeout=3)

    def remove(self, path, data):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"remove/{path}", method="POST", data=data, timeout=3)
    
    def upload(self, path, **kwargs):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"upload/{path}", **kwargs)

    def download(self, path):
        if len(path) > 0:
            if path[0] == "/": 
                path = path[1:]
        return self.__request__(f"download/{path}", method="GET")

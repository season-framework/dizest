from abc import *
import inspect

class BaseBinding:
    NAMESPACE = 'base'
    PREFIX = ""

    def __init__(self, serve):
        self.serve = serve
        self.app = serve.app
        self.query = serve.query

    def bind(self):
        serve = self.serve
        app = serve.app
        
        for attr_name in dir(self):
            if attr_name in ["bind", "app", "query"]:
                continue

            attr = getattr(self, attr_name)
            prefix = ""
            if len(self.PREFIX) > 0:
                prefix = self.PREFIX + "_"

            if callable(attr) and not attr_name.startswith("__") and attr_name.startswith(prefix):
                uri = attr_name[len(prefix):].split("_")
                uri.insert(0, self.NAMESPACE)
                endpoint = attr_name[len(prefix):].split("_")
                endpoint.insert(0, self.NAMESPACE)
                signature = inspect.signature(attr)
                parameters = signature.parameters

                baseuri = "/" + "/".join(uri)
                baseendpoint = "_".join(endpoint)
                for param_name, param in parameters.items():
                    uri.append(f"<{param_name}>")
                    endpoint.append(f"_{param_name}")
                
                uri = "/" + "/".join(uri)
                endpoint = "_".join(endpoint)

                uri = uri.replace("path", "path:path")

                if baseuri != uri:
                    app.add_url_rule(baseuri, baseendpoint, attr, methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])
                app.add_url_rule(uri, endpoint, attr, methods=['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH'])

from dizest.util import stdClass

import time
import builtins

_compile = compile
_print = print

class compiler:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.logger = _print

    def set_logger(self, logger):
        self.logger = logger

    def set(self, **kwargs):
        for key in kwargs:
            self.kwargs[key] = kwargs[key]
        
    def compile(self, code):
        kwargs = self.kwargs
        logger = self.logger

        env = dict()
        local_env = dict()

        for key in kwargs: env[key] = kwargs[key]
        env['__builtins__'] = builtins
        env['print'] = logger
        exec(code, env, local_env)

        codes = []
        for key in local_env:
            codes.append(f"__builtins__.{key} = {key}")
        codes = "\n".join(codes)
        exec(codes, env, local_env)  

        return env

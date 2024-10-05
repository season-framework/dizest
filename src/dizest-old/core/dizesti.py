from dizest import util
import time
import os

class DizestInstance:
    def __init__(self, flow, data, flask=None, path=None):
        self._timestamp = time.time()
        self._flow = flow
        self._data = data
        self._output = dict()
        
        if flask is not None:
            self.response = util.web.Response(flask)
            self.request = util.web.Request(flask, path)
        else:
            self.response = None
            self.request = None

    def __bind__(self, flask, path):
        self.response = util.web.Response(flask)
        self.request = util.web.Request(flask, path)

    def __unbind__(self):
        self.response = None
        self.request = None

    def __isbind__(self):
        return self.response is not None

    def __changed__(self, flow, data):
        self._flow = flow
        self._data = data

    def clear(self):
        self._flow.logger.clear_log()

    def input(self, name, default=None):
        try:
            cache = self._flow.workflow.cache
            inputs = self._data['inputs']
            if name not in inputs:
                return default

            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                inputtype = None
                if 'inputtype' in inputs[name]: 
                    inputtype = inputs[name]['inputtype']
                if ivalue is not None and len(ivalue) > 0:
                    try:
                        if inputtype == 'number':
                            ivalue = float(ivalue)
                    except:
                        pass
                    return ivalue
                else:
                    return default
            
            # load from previous output
            res = None
            _timestamp = 0
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    continue

                if _timestamp < cache[fid]._timestamp:
                    _timestamp = cache[fid]._timestamp
                    linked_output = cache[fid]._output
                    if oname in linked_output:
                        res = linked_output[oname]
                    else:
                        res = None

            return res
        except Exception as e:
            pass
        
        return default

    def inputs(self, name):
        try:
            cache = self._flow.workflow.cache
            res = []
            inputs = self._data['inputs']
            if name not in inputs:
                return res
            
            itype = inputs[name]['type']
            ivalue = inputs[name]['data']

            # load from variable
            if itype == 'variable':
                return res
            
            # load from previous output
            for iv in ivalue:
                fid = iv[0]
                oname = iv[1]
                if fid not in cache:
                    res.append(None)
                    continue

                linked_output = cache[fid]._output
                if oname in linked_output:
                    res.append(linked_output[oname])
                else:
                    res.append(None)
            
            return res
        except Exception as e:
            pass

        return []

    def output(self, *args, **kwargs):
        # if arguments exists
        if len(args) == 1:
            name = args[0]
            if name in self._output:
                return self._output[name]
            return None

        if len(args) >= 2:
            name = args[0]
            value = None
            if len(args) > 1:
                value = args[1]
            
            # update if process running
            self._output[name] = value
            return value
        
        # if set kwargs, update output
        for name in kwargs:
            value = kwargs[name]
            self._output[name] = value

    def drive(self, *path):
        cwd = os.getcwd()
        cwd = os.path.join(cwd, *path)
        return util.os.storage(cwd)


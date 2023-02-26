from dizest import util
import time
import os

class DizestInstance:
    def __init__(self, flow, data):
        self._timestamp = time.time()
        self._flow = flow
        self._data = data
        self._output = dict()
    
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
                if ivalue is not None and len(ivalue) > 0:
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
        cache = self._flow.workflow.cache

        # if arguments exists
        if len(args) > 0:
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


class Flow:
    def __init__(self, workflow, flow_id):
        self.__id__ = flow_id
        self.workflow = workflow
        self.process = None
    
    def package(self):
        return self.workflow.__package__['flow'][self.__id__]

    def update(self, **kwargs):
        for key in kwargs:
            self.package()[key] = kwargs[key]
    
    # getter
    def id(self):
        return self.package()['id']

    def title(self):
        title = None
        if 'title' in self.package():
            title = self.package()['title'] 
        if title is None or len(title) == 0:
            return self.app().title()
        return 'Unknown'

    def active(self):
        if 'active' in self.package() and self.package()['active']:
            return True
        return False
    
    def app(self):
        return self.workflow.app(self.package()['app_id'])

    def inputs(self):
        flow = self.package()
        app = self.app()
        appinput = app.inputs()
        inputs = dict()
        for val in appinput:
            vtype = val['type']
            inputtype = val['inputtype'] if 'inputtype' in val else None
            vname = val['name']
            if vtype == 'output':
                try:
                    cons = [[x['node'], x['input']] for x in flow['inputs'][vname]['connections']]
                    inputs[vname] = {"type": vtype, "data": cons}
                except:
                    pass
            elif vtype == 'variable':
                if vname in flow['data']:
                    inputs[vname] = ({"type": vtype, "data": flow['data'][vname], "inputtype": inputtype})
                else:
                    inputs[vname] = ({"type": vtype, "data": None, "inputtype": inputtype})
        return inputs

    def previous(self):
        inputs = self.inputs()
        previous_flows = []
        for key in inputs:
            if inputs[key]['type'] == 'output':
                links = inputs[key]['data']
                for link in links:
                    if link[0] not in previous_flows:
                        previous_flows.append(link[0])
        return previous_flows
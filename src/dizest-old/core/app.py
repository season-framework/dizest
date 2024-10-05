class App:
    def __init__(self, workflow, app_id):
        self.workflow = workflow
        self.package = workflow.__package__['apps'][app_id]

    # update
    def update(self, **kwargs):
        for key in kwargs:
            self.package[key] = kwargs[key]

    def clean(self):
        allowed = ['id', 'title', 'version', 'description', 'code', 'api', 'inputs', 'outputs', 'meta', 'uimode']
        keys = [key for key in self.package]
        for key in keys:
            if key not in allowed:
                del self.package[key]
        return self
        
    # getter
    def id(self):
        return self.package['id']

    def title(self):
        return self.package['title']
    
    def version(self):
        return self.package['version']
        
    def description(self):
        return self.package['description']
    
    def desc(self):
        return self.description()

    def code(self):
        return self.package['code']

    def api(self):
        return self.package['api']

    def outputs(self):
        return [x['name'] for x in self.package['outputs']]

    def inputs(self):
        return self.package['inputs']

    # setter
    def set_title(self, value):
        self.update(title=value)

    def set_version(self, value):
        self.update(version=value)

    def set_description(self, value):
        self.update(description=value)
    
    def set_desc(self, value):
        self.set_description(value)

    def set_code(self, value):
        self.update(code=value)

    def set_api(self, value):
        self.update(api=value)
    
    def set_outputs(self, value):
        self.update(outputs=value)
    
    def set_inputs(self, value):
        self.update(inputs=value)
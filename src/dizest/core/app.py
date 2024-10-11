class App:
    def __init__(self, workflow, app_id):
        self.workflow = workflow
        self.__package__ = workflow.__package__['apps'][app_id]

    # update
    def update(self, **kwargs):
        for key in kwargs:
            self.__package__[key] = kwargs[key]
    
    # getter
    def id(self):
        return self.__package__['id']

    def title(self):
        if 'title' not in self.__package__ or len(self.__package__['title']) == 0:
            return "Unknown"
        return self.__package__['title']
    
    def code(self):
        return self.__package__['code']

    def api(self):
        return self.__package__['api']

    def outputs(self):
        return [x['name'] for x in self.__package__['outputs']]

    def inputs(self):
        return self.__package__['inputs']

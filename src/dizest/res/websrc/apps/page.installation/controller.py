config = wiz.model("dizest/config").load()
if config is None: 
    config = dict()
    config['db'] = dict()
    config['db']['type'] = 'sqlite'
kwargs['config'] = config
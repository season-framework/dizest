def bootstrap(app, config):
    pass

secret_key = "season-dizest-secret"

socketio = dict()
socketio['async_mode'] = 'threading'
socketio['cors_allowed_origins'] = '*'
socketio['async_handlers'] = True
socketio['always_connect'] = False
socketio['manage_session'] = True

run = dict()
run['allow_unsafe_werkzeug'] = True
run['host'] = "0.0.0.0"
run['port'] = 4000
run['use_reloader'] = False
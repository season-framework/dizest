import season

config = season.stdClass()

config.app = season.stdClass()
config.app.cors_allowed_origins = "*"
config.app.async_handlers = True
config.app.always_connect = False
config.app.manage_session = True
# config.app.message_queue = "redis://localhost:6379"

config.run = season.stdClass()
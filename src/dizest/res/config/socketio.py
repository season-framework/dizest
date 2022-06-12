import season

app = season.stdClass()
app.cors_allowed_origins = "*"
app.async_handlers = True
app.always_connect = False
app.manage_session = True
# app.message_queue = "redis://localhost:6379"

run = season.stdClass()
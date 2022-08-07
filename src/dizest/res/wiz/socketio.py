import season

app = season.stdClass()
app.cors_allowed_origins = "*"
app.async_handlers = True
app.always_connect = False
app.manage_session = True
run = season.stdClass()

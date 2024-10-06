struct = wiz.model("portal/dizest/struct")
config = struct.config

segment = wiz.request.match("/api/dizest/auth/<action>/<path:path>")
if segment.action == 'logout':
    config.logout(segment.path)
else:
    segment = wiz.request.match("/api/dizest/auth/<path:path>")
    config.authenticate(segment.path)
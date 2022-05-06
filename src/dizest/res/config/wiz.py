import season
config = season.stdClass()

config.themepath = 'modules/themes'

config.pug = season.stdClass()
config.pug.variable_start_string = '{$'
config.pug.variable_end_string = '$}'

config.category = [{"id": "page", "title": "Page"}, {"id": "view", "title": "View"}, {"id": "widget", "title": "Widget"}, {"id": "modal", "title": "Modal"}]

config.topmenus = [{"title": "HOME", "url": "/"}, {"title": "WIZ", "url": "/wiz"}]

config.supportfiles = {".py": "python", ".js": "javascript", ".ts": "typescript", ".css": "css", ".less": "less", ".sass": "scss", ".scss": "scss", ".html": "html", ".pug": "pug", ".json": "json", ".svg": "html", ".txt": ".text", ".map": ".json", ".crt": ".text", ".key": ".text", ".sql": ".text"}

def acl(framework):
    return True
    try:
        role = framework.flask.session['role']
        if role == 'admin':
            return True
    except:
        pass
    framework.response.abort(401)
config.acl = acl

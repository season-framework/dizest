import sass

def compile(wiz, css, data):
    if 'render_id' in data:
        render_id = data['render_id']
        css = "#" + render_id + " { " + css + " }"
    css = sass.compile(string=css)
    css = str(css)
    return css
import lesscpy
from io import StringIO

def compile(wiz, css, data):
    if 'render_id' in data:
        render_id = data['render_id']
        css = "#" + render_id + " { " + css + " }"
    css = lesscpy.compile(StringIO(css), minify=True)
    css = str(css)
    return css
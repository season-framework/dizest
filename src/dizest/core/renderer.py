import html
from dizest.extends import render

class Renderer:
    renderers = [render.PyPlotRenderer, render.PILRenderer, render.HTMLRenderer]
    
    def __init__(self, renderers=None):
        if renderers is not None:
            self.renderers = renderers

    def __call__(self, value, **kwargs):
        res = value

        is_rendered = False
        for renderer in self.renderers:
            renderer = renderer()
            if renderer.check(value, **kwargs):
                res = renderer.render(value, **kwargs)
                is_rendered = True
        
        if is_rendered is False:
            res = str(res)
            res = html.escape(res)
            size = kwargs['size'] if 'size' in kwargs else 2000
            if len(res) > size and size > 0: 
                res = res[:size - 50] + " ... " + res[-50:]
        return res
        
    def add(self, renderer):
        self.renderers.insert(0, renderer)
    
    def delete(self, renderer):
        self.renderers.remove(renderer)

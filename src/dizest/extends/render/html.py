from dizest.base.render import BaseRenderer

class HTMLRenderer(BaseRenderer):
    hasAttribute = ['to_html']

    def __render__(self, value, **kwargs):
        try:
            if 'max_rows' not in kwargs: kwargs['max_rows'] = 10
            if 'max_cols' not in kwargs: kwargs['max_cols'] = 10
            val = value.to_html(**kwargs).replace("\n", "")
        except:
            val = value.to_html().replace("\n", "")
        if len(val) > 10000: return f"<div class='text-red'>Output is too long</div>"
        return val
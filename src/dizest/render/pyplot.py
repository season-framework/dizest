from dizest.render.base import BaseRenderer
from matplotlib import pyplot
import io
import base64
import traceback

class PyPlotRenderer(BaseRenderer):
    className = [pyplot]

    def __render__(self, v, **kwargs):
        img = io.BytesIO()
        v.savefig(img, format='png', bbox_inches='tight')
        img.seek(0)
        encoded = base64.b64encode(img.getvalue())
        pyplot.figure().clear()
        return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))

    def __error__(self, value, err, **kwargs):
        stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
        stderr = f"<div class='text-red'>{stderr}</div>"
        return stderr
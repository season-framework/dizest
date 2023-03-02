from matplotlib import pyplot
import io
import base64
from PIL import Image
import html
import traceback
import numpy as np

class Renderer:
    def render(self, v):
        try:
            if v == pyplot:
                img = io.BytesIO()
                v.savefig(img, format='png', bbox_inches='tight')
                img.seek(0)
                encoded = base64.b64encode(img.getvalue())
                pyplot.figure().clear()
                return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
        except Exception as e:
            pass

        try:
            if isinstance(v, Image.Image):
                height, width = np.array(v).shape[:2]
                if width > 256:
                    v = v.resize((256, int(256 * height / width)))

                img = io.BytesIO()
                v.save(img, format='PNG')
                img.seek(0)
                encoded = base64.b64encode(img.getvalue())
                return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))
        except Exception as e:
            stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
            stderr = f"<div class='text-red'>{stderr}</div>"
            return stderr
        
        try:
            if hasattr(v, 'to_html'):
                val = v.to_html().replace("\n", "")
                if len(val) > 20000:
                    return f"<div class='text-red'>Output is too long</div>"
                return val
        except Exception as e:
            pass

        v = str(v)
        v = html.escape(v)
        return v
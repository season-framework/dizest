from dizest.render.base import BaseRenderer
from PIL import Image
import io
import base64
import numpy as np
import traceback

class PILRenderer(BaseRenderer):
    className = [Image.Image]

    def __render__(self, v, **kwargs):
        height, width = np.array(v).shape[:2]
        if width > 256:
            v = v.resize((256, int(256 * height / width)))

        img = io.BytesIO()
        v.save(img, format='PNG')
        img.seek(0)
        encoded = base64.b64encode(img.getvalue())
        return '<img src="data:image/png;base64, {}">'.format(encoded.decode('utf-8'))

    def __error__(self, value, err, **kwargs):
        stderr = traceback.format_exc().replace("\n", "<br>").replace("\t", "&nbsp;&nbsp;&nbsp;&nbsp;").replace(" ", "&nbsp;").strip()
        stderr = f"<div class='text-red'>{stderr}</div>"
        return stderr
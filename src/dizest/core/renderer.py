from matplotlib import pyplot
import io
import base64
from PIL import Image
import html

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
            pass
        
        try:
            if hasattr(v, 'to_html'):
                return v.to_html().replace("\n", "")
        except Exception as e:
            pass

        v = str(v)
        v = html.escape(v)
        return v
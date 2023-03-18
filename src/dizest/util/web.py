import dizest
import io
import json
import os
import flask

class ResponseException(Exception):
    def __init__(self, code=200, response=None):
        super().__init__("dizest.exception.response")
        self.code = code
        self.response = response

    def get_response(self):
        return self.code, self.response

class Response:
    def __init__(self, _flask):
        self.headers = self._headers()
        self.cookies = self._cookies()
        self.status_code = None
        self.mimetype = None
        self.pil_image = self.PIL
        self._flask = _flask
    
    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def abort(self, code=500):
        self._flask.abort(code)

    def error(self, code=404, response="ERROR"):
        event = ResponseException(code=code, response=response)
        raise event
    
    def response(self, resp):
        return self._build(resp)

    def PIL(self, pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None):
        img_io = io.BytesIO()
        pil_image.save(img_io, type)
        img_io.seek(0)
        resp = self._flask.send_file(img_io, mimetype=mimetype, as_attachment=as_attachment, attachment_filename=filename)
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        if os.path.isfile(filepath):
            resp = self._flask.send_file(filepath, as_attachment=as_attachment, attachment_filename=filename)
            return self._build(resp)
        self._flask.abort(404)
    
    def send(self, message, content_type=None):
        resp = self._flask.Response(str(message))
        if content_type is not None:
            self.headers.set('Content-Type', content_type)
        return self._build(resp)

    def json(self, obj):
        try:
            obj = dict(obj)
        except Exception as e:
            pass
        obj = json.dumps(obj, default=dizest.util.string.json_default, ensure_ascii=False)
        resp = self._flask.Response(str(obj))
        self.headers.set('Content-Type', 'application/json')
        return self._build(resp)

    def status(self, *args, **kwargs):
        data = dict()
        if len(args) == 0:
            status_code = 200
        elif len(args) == 1:
            status_code = args[0]
            for key in kwargs:
                data[key] = kwargs[key]
        elif len(args) > 1:
            status_code = args[0]
            data = args[1]

        res = dict()
        res['code'] = status_code
        if data is not None:
            res['data'] = data
        res = json.dumps(res, default=dizest.util.string.json_default, ensure_ascii=False)
        return self.send(res, content_type='application/json')

    class _headers:
        def __init__(self):
            self.headers = {}
        
        def get(self):
            return self.headers

        def set(self, key, value):
            self.headers[key] = value

        def load(self, headers):
            self.headers = headers

        def flush(self):
            self.headers = {}

    class _cookies:
        def __init__(self):
            self.cookies = {}
        
        def get(self):
            return self.cookies

        def set(self, key, value):
            self.cookies[key] = value

        def load(self, cookies):
            self.cookies = cookies

        def flush(self):
            self.cookies = {}

    def _build(self, response):
        headers = self.headers.get()
        for key in headers:
            response.headers[key] = headers[key]

        cookies = self.cookies.get()
        for key in cookies:
            response.set_cookie(key, cookies[key])
        
        if self.status_code is not None:
            response.status_code = self.status_code
        else:
            response.status_code = 200

        if self.mimetype is not None:
            response.mimetype = self.mimetype

        event = ResponseException(code=response.status_code, response=response)
        raise event

class Request:
    def __init__(self, _flask, urlpath):
        self._flask = _flask
        self.urlpath = urlpath

    def uri(self):
        urlpath = self.urlpath
        if urlpath is None:
            return ""
        return urlpath

    def method(self):
        return self._flask.request.method

    def ip(self):
        return self.client_ip()

    def client_ip(self):
        return self._flask.request.environ.get('HTTP_X_REAL_IP', self._flask.request.remote_addr)

    def lang(self):
        return self.language()

    def language(self):
        try:
            lang = "DEFAULT"
            cookies = dict(self._flask.request.cookies)
            headers = dict(self._flask.request.headers)
            if 'framework-language' in cookies:
                lang = cookies['framework-language']
            elif 'Accept-Language' in headers:
                lang = headers['Accept-Language']
                lang = lang[:2]
            return lang.upper()
        except Exception as e:
            return "DEFAULT"

    def match(self, pattern):
        uri = self.uri()
        x = re.search(pattern, uri)
        if x: return True
        return False

    def query(self, key=None, default=None):
        request = self.request()
        formdata = dict(request.values)

        if key is None:
            return formdata

        if key in formdata:
            return formdata[key]
        
        if default is True:
            self._flask.abort(400)
            
        return default

    def headers(self, key, default=None):
        headers = dict(self._flask.request.headers)
        if key in headers:
            return headers[key]
        return default

    def cookies(self, key, default=None):
        cookies = dict(self._flask.request.cookies)
        if key in cookies:
            return cookies[key]
        return default

    def file(self, namespace='file'):
        try:
            return self._flask.request.files[namespace]
        except Exception as e:
            return None

    def files(self, namespace='file'):
        try:
            return self._flask.request.files.getlist(f'{namespace}[]')
        except Exception as e:
            return []

    def request(self):
        return self._flask.request

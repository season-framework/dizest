import io
import json
import os
import flask

class ResponseException(Exception):
    def __init__(self, clsname, response, code=200):
        super().__init__("dizest.exception.response." + clsname)
        self.code = code
        self.name = clsname
        self.response = response
    
    def get(self):
        return self.name, self.code, self.response

class response:
    def __init__(self):
        self.headers = self._headers()
        self.cookies = self._cookies()
        self.status_code = 200
        self.mimetype = None
        self.pil_image = self.PIL

    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def error(self, code=404, response="ERROR"):
        resp = dict()
        resp['kwargs'] = dict()
        resp['kwargs']['code'] = code
        resp['kwargs']['response'] = response
        self._build(response, name="error")

    def redirect(self, url):
        resp = dict()
        resp['args'] = [url]
        self._build(resp, name="redirect")

    def PIL(self, pil_image, type='JPEG', mimetype='image/jpeg', as_attachment=False, filename=None):
        resp = dict()
        resp['args'] = [pil_image]
        resp['kwargs'] = dict()
        resp['kwargs']['type'] = type
        resp['kwargs']['mimetype'] = mimetype
        resp['kwargs']['as_attachment'] = as_attachment
        resp['kwargs']['download_name'] = filename
        self._build(resp, name="PIL")

    def download(self, filepath, as_attachment=True, filename=None):
        resp = dict()
        resp['args'] = [filepath]
        resp['kwargs'] = dict()
        resp['kwargs']['as_attachment'] = as_attachment
        resp['kwargs']['download_name'] = filename
        self._build(resp, name="download")
    
    def send(self, message, content_type=None):
        resp = dict()
        resp['args'] = [message]
        resp['kwargs'] = dict()
        resp['kwargs']['content_type'] = content_type
        self._build(resp, name="text")

    def json(self, obj):
        resp = dict()
        resp['args'] = [obj]
        self._build(resp, name="json")

    def status(self, *args, **kwargs):
        resp = dict()
        resp['args'] = args
        resp['kwargs'] = kwargs
        self._build(resp, name="status")

    # internal classes
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

    def _build(self, response, name="default"):
        response['headers'] = self.headers.get()
        response['cookies'] = self.cookies.get()
        response['mimetype'] = self.mimetype
        raise ResponseException(name, response, code=self.status_code)
import peewee as pw
import json

class JSONField(pw.TextField):
    def db_value(self, value):
        return json.dumps(value)

    def python_value(self, value):
        try:
            if value is not None:
                return json.loads(value)
        except:
            pass
        return []

class Model(wiz.model("dizest/orm/2.0.0/base")):
    class Meta:
        db_table = 'app'

    id = pw.CharField(primary_key=True, max_length=32)
    user_id = pw.CharField(index=True, max_length=32)
    title = pw.CharField(index=True, max_length=96)
    version = pw.CharField(index=True, max_length=24)
    mode = pw.CharField(index=True, max_length=32)
    visibility = pw.CharField(index=True, max_length=16)
    
    description = pw.TextField()
    code = pw.TextField()
    sample = pw.TextField()
    api = pw.TextField()
    pug = pw.TextField()
    js = pw.TextField()
    css = pw.TextField()
    logo = pw.TextField()
    featured = pw.TextField()
    inputs = JSONField() # json fields
    outputs = JSONField() # json fields

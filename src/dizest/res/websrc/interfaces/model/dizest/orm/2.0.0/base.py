import peewee as pw

class Model(pw.Model):
    class Meta:
        database = wiz.model("dizest/orm").db()

import peewee as pw
import bcrypt

class PasswordField(pw.TextField):
    def db_value(self, value):
        value = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        return value

    def python_value(self, value):
        if value is None:
            return None
        value = value.encode('utf-8')
        def check_password(password):
            password = password.encode('utf-8')
            return bcrypt.checkpw(password, value)
        return check_password

class Model(wiz.model("dizest/orm/2.0.0/base")):
    class Meta:
        db_table = 'user'

    id = pw.CharField(primary_key=True, max_length=32)
    username = pw.CharField(max_length=32)
    email = pw.CharField(unique=True, max_length=192)
    role = pw.CharField(index=True, max_length=16)
    password = PasswordField()

import os
import peewee as pw

class Model:
    def __init__(self):
        self.cache = dict()

    @staticmethod
    def db():
        config = wiz.model("dizest/config").load()
        dbconfig = config.db
        if dbconfig.config is None: dbconfig.config = dict()
        if dbconfig.type == 'mysql':
            db = pw.MySQLDatabase(dbconfig.database, **dbconfig.config)
        else:
            BASEPATH = season.path.project
            sqlitedb = os.path.realpath(os.path.join(BASEPATH, '..', 'dizest.db'))
            db = pw.SqliteDatabase(sqlitedb)
        return db
    
    @classmethod
    def use(cls):
        return cls()
    
    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, key):
        if key in self.cache:
            return self.cache[key]
        ormpath = os.path.join("dizest/orm", key)
        self.cache[key] = wiz.model(ormpath)
        return self.cache[key]
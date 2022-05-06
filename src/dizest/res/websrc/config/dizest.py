from season import stdClass

config = stdClass()
# config.db = stdClass()
# config.db.type = 'sqlite'
# config.db.database = '/var/www/dizest.season/dizest/dizest.db'

config.db = stdClass()
config.db.type = 'mysql'
config.db.database = 'dizest'
config.db.config = stdClass()
config.db.config.host = '127.0.0.1'
config.db.config.user = 'season'
config.db.config.passwd = 'season123!@'
config.db.config.port = 3306

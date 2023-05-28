import season

class BaseConfig(season.util.std.stdClass):
    DEFAULT_VALUES = dict()

    def __init__(self, values=dict()):
        default = self.DEFAULT_VALUES
        for key in default:
            _type, val = default[key]
            if key not in values:
                if _type is not None:
                    val = _type(val)
                values[key] = val
            else:
                if _type is not None:
                    values[key] = _type(values[key])
        super(BaseConfig, self).__init__(values)
        
    def __getattr__(self, attr):
        val = super(BaseConfig, self).__getattr__(attr)
        if attr in self.DEFAULT_VALUES:
            _type, _default = self.DEFAULT_VALUES[attr]
            if val is None: val = _default
            if _type is not None: val = _type(val)
        return val

def session_user_id():
    session = wiz.model("portal/season/session")
    return session.get("id")

class Config(BaseConfig):
    DEFAULT_VALUES = {
        # database config
        'orm_base': (str, "db/"),
        
        # smtp config
        'smtp_host': (None, None),
        'smtp_port': (int, 587),
        'smtp_sender': (None, None),
        'smtp_password': (None, None),

        # session config
        'session_user_id': (None, session_user_id),
        
        # auth config
        'auth_logout_uri': (None, None),
        'auth_baseuri': (str, '/auth'),
        'auth_saml_use': (bool, False),
        'auth_saml_entity': (str, 'season'),
        'auth_saml_base_path': (str, 'config/auth/saml'),
        'auth_saml_acs': (None, None),
        'auth_saml_error_uri': (str, '/'),
    }

config = wiz.config("season")
Model = Config(config)
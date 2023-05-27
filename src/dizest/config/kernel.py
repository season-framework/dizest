from dizest.config.base import BaseConfig

class KernelConfig(BaseConfig):
    DEFAULT_VALUES = {
        'host': (str, '0.0.0.0'),
        'port': (int, 3000),
        'dsocket': (None, None),
        'async_mode': (str, 'threading'),
        'cors_allowed_origins': (str, '*'),
        'async_handlers': (bool, True),
        'always_connect': (bool, False),
        'manage_session': (bool, True)
    }

import json
from logger import log


try:
    conf = json.load( open( "config.json" ) )
except Exception as e:
    log('Config load failed')
    conf = {
        'tenant_id': '',
        'client_id':'',
        'token':'',
    }


class Config(object):

    SCOPES = 'offline_access user.read group.read.all group.readwrite.all'

    def __init__(self):
        self._config = conf # set it to conf

    def __getattr__(self, name):
        return self.get_property(name)

    def change(self, name, value):
        self._config[name] = value
        self.store_config()

    def _config(self, name, value):
        self._config[name] = value

    def get_property(self, property_name: str):
        if property_name not in self._config.keys(): # we don't want KeyError
            return None  # just return None if not found
        return self._config[property_name]

    def store_config(self):
        json.dump(self._config, open("config.json", 'w'))

    def get_dict(self):
        params = {
            'tenant_id': self.tenant_id,
            'client_id': self.client_id,
            'group_id': self.group_id,
            'secret': self.secret,
            'refresh_token': self.refresh_token,
            'SCOPES': self.SCOPES
        }
        return params


config = Config()

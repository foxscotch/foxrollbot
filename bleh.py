from os import environ


class ConfigMeta(type):
    def __new__(cls, class_name, parents, attrs, app_name=None):
        cls._app_name = app_name.upper() if app_name else None
        attrs = {a.upper(): attrs[a] for a in attrs if not a.startswith('_')}
        return super().__new__(cls, class_name, parents, attrs)

    def __getattribute__(cls, attr):
        attr = attr.upper()
        app_name = super().__getattribute__('_app_name')
        env_attr = '_'.join([app_name, attr])
        if app_name and env_attr in environ:
            return environ[env_attr]
        return super().__getattribute__(attr)
    
    def __setattribute__(cls, attr, value):
        print(attr)
        super().__setattribute__(attr, value)


class BaseConfig(metaclass=ConfigMeta):
    Hello = 10


class Config(BaseConfig, app_name='test'):
    Hello = 12
    GOODBYE = 14


print(Config.HELLO)
print(Config.GOODBYE)
print(Config.STUFF)

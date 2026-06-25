from profiles import default_settings, profile_settings
from custom_logger import get_logger

settings = {**default_settings, **profile_settings}


class Settings(object):
    _instance = None

    def __new__(cls, iterable=(), **kwargs):
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance.__dict__.update(iterable, **kwargs)
            logger_name = getattr(cls._instance, 'logger_name', 'birthday_bot')
            log_level = getattr(cls._instance, 'log_level', 20)
            log_to_file = getattr(cls._instance, 'log_to_file', True)
            cls._instance.log = get_logger(
                name=logger_name,
                level=log_level,
                log_to_file=log_to_file,
            )
        return cls._instance

    def __str__(self):
        return str(self.__dict__)


def get_settings():
    return Settings(settings)


app_settings = get_settings()
if hasattr(app_settings, 'DEBUG') and app_settings.DEBUG:
    print(f"app_settings: {app_settings}")

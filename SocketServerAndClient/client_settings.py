# from pathlib import Path

# Here are two ways to define variables DEBUG and PROFILE
# 1. Directly in the file SETTINGS.py
DEBUG = True
PROFILE = 'DEV'  # PROFILE = DEV, PROD, TEST

# 2. Using environment variables
# debug = os.getenv('DEBUG')
# if debug == "True" or debug.upper() == "TRUE":
#     DEBUG = True
# else:
#     DEBUG = False

# profile = os.getenv('PROFILE')
# if profile:
#     PROFILE = profile.upper()
# else:admin
#     raise Exception("Environment variable APP_PROFILE not defined")
#     exit(1)

# print(f"DEBUG={DEBUG}")
# print(f"PROFILE={PROFILE}")

# Базовая папка
# BASE_DIR = Path(__file__).resolve().parent.parent
# print(f"BASE_DIR={BASE_DIR}")

if DEBUG:
    LOG_LEVEL = "DEBUG"
else:
    LOG_LEVEL = "INFO"

default_settings = dict(
    DEBUG=DEBUG,
    PROFILE=PROFILE,
    LOG_LEVEL=LOG_LEVEL,
    server_ip='172.26.12.111',
    server_port=12345,
)

if PROFILE == 'DEV':
    profile_settings = dict(
    )

if PROFILE == 'PROD':
    profile_settings = dict(
    )

# Combining default settings and specific profile settings
# We can use: In Python 3.5 or greater: z = {**x, **y}; In Python 3.9.0 or greater: z = x | y
settings = {**default_settings, **profile_settings}


# print(settings)

# You can also create an instance of the class and work with it (see below)
class Settings(object):
    """
    Класс настроек приложения.
    """

    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def __str__(self):
        return str(self.__dict__)

    def get_settings(self):
        return self.__dict__


app_settings = Settings(settings)

if __name__ == '__main__':
    import pprint

    pp = pprint.PrettyPrinter(indent=2)
    print(f"DEBUG={DEBUG}")
    print(f"PROFILE={PROFILE}")
    print(f"LOG_LEVEL={LOG_LEVEL}")
    print("\n" + "=" * 80 + "\nDefault settings\n" + "=" * 80)
    pp.pprint(default_settings)
    print("\n" + "=" * 80 + f"\nProfile {PROFILE} settings\n" + "=" * 80)
    pp.pprint(profile_settings)
    # These settings will be used in the application
    print("\n" + "=" * 80 + "\nApp Settings\n" + "=" * 80)
    pp.pprint(app_settings.get_settings())

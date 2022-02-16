"""
SETTINGS.py - .py file for getting profile with settings of application. You can set multiple profiles with settings.

Attention!!! IF THE FILE CONTAINS SECRET DATA (for example, passwords)
             This file should never be stored in repository git, so it must be added to .gitignore immediately
             This file copy between computers manually.
             Backup copies of this file should be stored in a secure vault (you can use a password-protected archive)

How to use:
import SETTINGS

gb = PASSWORDS.settings['git_branch']

if SETTINGS.DEBUG:
    log_level = logging.DEBUG
else:
    log_level = logging.INFO

"""

# Here are two ways to define variables DEBUG and PROFILE
# 1. Directly in the file SETTINGS.py
DEBUG = True
PROFILE = 'DEV'

# 2. Using environment variables
# debug = os.getenv('CI_DEBUG')
# if debug or debug.upper() == "TRUE":
#     DEBUG = True
# else:
#     DEBUG = False
# profile = os.getenv('CI_PROFILE')
# if profile:
#     PROFILE = profile.upper()
# else:
#     raise Exception("Environment variable CI_PROFILE not defined")
#     exit(1)


# Default settings. Common for all profiles.
default_settings = dict(
    DEBUG=DEBUG,  # Here you can set the default value for DEBUG
    profile=PROFILE,  # Here you can set the default value for PROFILE
    log_to_file=False,  # bool
    log_file_period_days=1,  # int
    log_file_keep_days=30,  # int
    git_branch='develop',  # string
)

# Profile specific settings

# DEV profile
if PROFILE == 'DEV':
    profile_settings = dict(
        DEBUG=DEBUG,  # Here you can set the default value for DEBUG
        profile=PROFILE,  # Here you can set the default value for PROFILE
        log_to_file=False,  # bool
        log_file_period_days=0,  # int
        log_file_keep_days=3,  # int
        git_branch='develop',  # string
    )

# STAGE profile
if PROFILE == 'STAGE':
    profile_settings = dict(
        DEBUG=DEBUG,  # Here you can set the default value for DEBUG
        profile=PROFILE,  # Here you can set the default value for PROFILE
        log_to_file=True,  # bool
        log_file_period_days=1,  # int
        log_file_keep_days=30,  # int
        git_branch='staging',  # string
    )

# Combining default settings and specific profile settings
# We can use: In Python 3.5 or greater: z = {**x, **y}; In Python 3.9.0 or greater: z = x | y
settings = {**default_settings, **profile_settings}


# You can also create an instance of the class and work with it (see below)
class Settings(object):
    """
    Класс настроек приложения.
    """

    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def __str__(self):
        return str(self.__dict__)


def get_settings():
    """
    Процедура возвращает настройки приложения.
    :return:
    """
    return Settings(settings)


if __name__ == '__main__':
    import pprint

    pp = pprint.PrettyPrinter(indent=2)
    print(f"DEBUG={DEBUG}")
    print(f"PROFILE={PROFILE}")
    print("\n" + "=" * 80 + "\nDefault settings\n" + "=" * 80)
    pp.pprint(default_settings)
    print("\n" + "=" * 80 + f"\nProfile {PROFILE} settings\n" + "=" * 80)
    pp.pprint(profile_settings)
    # These settings will be used in the application
    print("\n" + "=" * 80 + "\nApp Settings\n" + "=" * 80)
    pp.pprint(settings)

    # Use class
    s = Settings(settings)
    print("\n" + "=" * 80 + "\nClass Settings\n" + "=" * 80)
    pp.pprint(s.__dict__)

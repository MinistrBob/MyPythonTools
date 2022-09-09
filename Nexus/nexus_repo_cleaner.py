import logging
import os
import sys
import traceback

from nexus_helper.nexus_helper import NexusHelper


# Program settings
settings = {}
# Program logger
logger = logging.getLogger()


def main():
    # Get app settings
    try:
        get_settings()
    except Exception:
        print(f"ERROR: app cannot get settings\n{traceback.format_exc()}")
        exit(1)
    # Create app logger
    set_logger()
    logger.debug(settings)
    # work
    nexus = NexusHelper(settings, logger)
    result = nexus.get_list_component_items()
    print(f"Всего {len(result)} items")
    print(result)


class Settings(object):
    """
    Program settings like class
    """

    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def __str__(self):
        return str(self.__dict__)


def get_settings():
    global settings
    # Enable DEBUG mode?
    settings['DEBUG'] = os.getenv("NX_DEBUG", 'False').lower() in 'true'
    settings['nexus_host'] = os.getenv('NX_HOST', "Unknown")
    settings['nexus_username'] = os.getenv('NX_USERNAME', "Unknown")
    settings['nexus_password'] = os.getenv('NX_PASSWORD', "Unknown")
    settings['nexus_repo'] = os.getenv('NX_REPO', "Unknown")
    settings = Settings(settings)


def set_logger():
    # Log to stdout
    global logger
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    stdout_log_formatter = logging.Formatter('%(asctime)s|%(levelname)-5s|%(funcName)s| %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_log_formatter)
    logger.addHandler(stdout_handler)


if __name__ == '__main__':
    main()

from __future__ import print_function

import logging
import sys

import SETTINGS
from nexus_helper.nexus_helper import NexusHelper

# Program settings
settings = {}
# Program logger
logger = logging.getLogger()


def main():
    # Get app settings
    global settings
    settings = SETTINGS.get_settings()
    settings.work_dir = sys.path[0]
    # Create app logger
    set_logger()
    logger.debug(settings)
    # create an instance of the API class
    nexus = NexusHelper(settings, logger)
    #
    # nexus.get_list_component_pages()
    #
    nexus.upload_tags(local_file=r"c:\!SAVE\tags.yaml", nexus_raw_filename="test777.yaml")
    #
    # nexus.download_tags()


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

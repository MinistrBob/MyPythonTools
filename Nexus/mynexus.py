from __future__ import print_function
import os
import time
import logging
import sys
import json
import requests
import swagger_client
from swagger_client.rest import ApiException
from pprint import pprint

# Program settings
settings = {}
# Program logger
logger = logging.getLogger()


def main():
    # Get app settings
    try:
        get_settings()
    except Exception:
        print(f"ERROR: app cannot get settings")
        exit(1)
    # Create app logger
    set_logger()
    logger.debug(settings)
    # create an instance of the API class
    configuration = swagger_client.Configuration()
    configuration.host = settings.NX_HOST
    configuration.username = settings.NX_USERNAME
    configuration.password = settings.NX_PASSWORD
    configuration.debug = settings.NX_DEBUG
    bat = configuration.get_basic_auth_token()
    logger.debug(bat)
    api_client = swagger_client.ApiClient(configuration=configuration, header_name='Authorization', header_value=bat)
    #
    # upload_file(api_client)
    #
    # Download all files from RAW repo
    result = get_components(api_client)
    # show_raw(result)
    show_docker(result)


def show_docker(result):
    for page in result:
        for item in page.items:  # PageComponentXO
            if True:
            # if item.name == "platform-public-front/platform-public-front":
                tag = f"{item.name}\t{item.id}\t{item.version}"
                for asset in item.assets:  # ComponentXO
                    print(f"{tag}\t{asset.last_modified}")
            else:
                continue


def show_raw(result):
    for page in result:
        for item in page.items:  # PageComponentXO
            for asset in item.assets:  # ComponentXO
                print("=========================================")
                pprint(asset)
                pprint(asset.path)
                pprint(asset.download_url)
                # download_file(r'versions/tags.yaml', r'http://172.26.12.108:8081/repository/raw-test/tags.yaml')
                download_file(asset.path, asset.download_url)


def download_file(path, download_url):
    file_name = os.path.basename(path)
    logger.debug(file_name)
    r = requests.get(download_url, auth=(settings.NX_USERNAME, settings.NX_PASSWORD))
    logger.debug(f"{r.status_code}")
    with open(os.path.join(r"c:\!SAVE", file_name), "wb") as code:
        code.write(r.content)


def upload_file(api_client):
    api_instance = swagger_client.ComponentsApi(api_client)
    api_instance.upload_component(repository=settings.NX_REPO, raw_directory='/', raw_asset1=r'c:\!SAVE\tags.yaml',
                                  raw_asset1_filename='tags.yaml')


def get_components(api_client):
    api_instance = swagger_client.ComponentsApi(api_client)
    repository = settings.NX_REPO  # str
    result = []
    i = 0
    page = None
    while 1 == 1:
        try:
            if i == 0:
                page = api_instance.get_components(repository=repository)
            else:
                page = api_instance.get_components(repository=repository, continuation_token=continuation_token)
            # print(page)
        except ApiException as e:
            logger.error("Exception when calling ComponentsApi->get_components: %s\n" % e)
        result.append(page)
        i += 1
        logger.info(f"Страница {i}")
        if page.continuation_token is None:
            break
        else:
            continuation_token = page.continuation_token
    pprint(result)
    return result


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
    settings['NX_DEBUG'] = os.getenv("NX_DEBUG", 'False').lower() in 'true'
    settings['NX_HOST'] = os.getenv('NX_HOST', "Unknown")
    settings['NX_USERNAME'] = os.getenv('NX_USERNAME', "Unknown")
    settings['NX_PASSWORD'] = os.getenv('NX_PASSWORD', "Unknown")
    # settings['NX_REPO'] = os.getenv('NX_REPO', "Unknown")

    #settings['NX_DEBUG'] = os.getenv("NX_DEBUG", 'False').lower() in 'true'
    #settings['NX_HOST'] = ''
    #settings['NX_USERNAME'] = ''
    #settings['NX_PASSWORD'] = ''
    settings['NX_REPO'] = ''

    settings = Settings(settings)


def set_logger():
    # Log to stdout
    global logger
    if settings.NX_DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    stdout_log_formatter = logging.Formatter('%(asctime)s|%(levelname)-5s|%(funcName)s| %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_log_formatter)
    logger.addHandler(stdout_handler)


if __name__ == '__main__':
    main()

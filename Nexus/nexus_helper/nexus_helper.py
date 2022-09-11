import os
from typing import List, NoReturn

import requests
import swagger_client
from swagger_client import PageComponentXO
from swagger_client.rest import ApiException
from .Class_NexusComponent import NexusComponent


class NexusHelper(object):
    def __init__(self, settings, log):
        self.log = log
        self.configuration = swagger_client.Configuration()
        self.configuration.host = settings.nexus_host
        self.configuration.username = settings.nexus_username
        self.configuration.password = settings.nexus_password
        self.configuration.debug = settings.DEBUG
        self.nexus_repo = settings.nexus_repo
        self.tags_yaml_file = None  # tags.yaml в nexus
        self.tags_yaml = None  # локальный tags.yaml
        self.bat = self.configuration.get_basic_auth_token()
        self.api_client = swagger_client.ApiClient(configuration=self.configuration, header_name='Authorization',
                                                   header_value=self.bat)

    def __str__(self):
        return f"host={self.configuration.host}|username={self.configuration.username}|bat={self.bat}"

    def download_tags(self, download_url=None) -> NoReturn:
        """
        Скачать файл tags.yaml из Nexus.

        Args:
            download_url: URL для скачивания.
        """
        if download_url is None:
            download_url = self.tags_yaml_file
        r = requests.get(download_url, auth=(self.configuration.username, self.configuration.password))
        self.log.debug(f"{r.status_code}")
        with open(self.tags_yaml, "wb") as code:
            code.write(r.content)

    def upload_tags(self,
                    local_file=None,
                    nexus_raw_directory=r'/',
                    nexus_raw_filename=r'tags.yaml') -> NoReturn:
        """
        Закачать файл tags.yaml в Nexus. По умолчанию, закачивается локальный tags.yaml в корень репозитория '/'.

        Args:
            local_file: Полный путь к локальному файлу tags.yaml.
            nexus_raw_filename: Имя файла в Nexus репо.
            nexus_raw_directory: Имя папки в Nexus репо.
        """
        if local_file is None:
            local_file = self.tags_yaml
        api_instance = swagger_client.ComponentsApi(self.api_client)
        api_instance.upload_component(repository=self.nexus_repo, raw_directory=nexus_raw_directory,
                                      raw_asset1=local_file, raw_asset1_filename=nexus_raw_filename)

    def get_list_component_pages(self) -> List[PageComponentXO]:
        """
        List of PageComponentXO
        :return:
        """
        api_instance = swagger_client.ComponentsApi(self.api_client)
        result = []
        i = 1
        page = None
        continuation_token = ''
        while 1 == 1:
            self.log.debug(f"Страница {i}")
            try:
                if i == 1:
                    page = api_instance.get_components(repository=self.nexus_repo)
                else:
                    page = api_instance.get_components(repository=self.nexus_repo,
                                                       continuation_token=continuation_token)
                self.log.debug(page)
            except ApiException as e:
                self.log.error("Exception when calling ComponentsApi->get_components: %s\n" % e)
            result.append(page)
            i += 1
            if page.continuation_token is None:
                break
            else:
                continuation_token = page.continuation_token
        self.log.debug(result)
        return result

    def get_list_component_items(self) -> List[NexusComponent]:
        """
        Dict of items
        :return:
        """
        api_instance = swagger_client.ComponentsApi(self.api_client)
        result = {}
        page_count = 1
        page = None
        continuation_token = ''
        while 1 == 1:
            self.log.debug(f"Страница {page_count}")
            try:
                if page_count == 1:
                    page = api_instance.get_components(repository=self.nexus_repo)
                else:
                    page = api_instance.get_components(repository=self.nexus_repo,
                                                       continuation_token=continuation_token)
                self.log.debug(page)
            except ApiException as e:
                self.log.error("Exception when calling ComponentsApi->get_components: %s\n" % e)
            for item in page.items:
                if item.name not in result.keys():
                    result[item.name] = []
                nc = NexusComponent(item.id, item.name, item.version, item.assets[0].download_url, item.assets[0].last_modified)
                # result.append(nc)
                result[item.name].append(nc)

            # break
            page_count += 1
            if page.continuation_token is None:
                break
            else:
                continuation_token = page.continuation_token
        self.log.debug(result)
        return result


if __name__ == '__main__':
    pass

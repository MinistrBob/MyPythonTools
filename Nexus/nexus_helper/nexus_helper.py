import datetime
from typing import List, NoReturn
from dateutil.tz import tzutc

import requests
import swagger_client
from dateutil.tz import tzutc
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

    def delete_component(self, comp_id=None):
        api_instance = swagger_client.ComponentsApi(self.api_client)
        api_instance.delete_component(id=comp_id)

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
                nc = NexusComponent(item.id, item.name, item.version, item.assets[0].download_url,
                                    item.assets[0].last_modified)
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

    def fake_get_list_component_items(self):
        result = {"platform-public-front/platform-public-front": []}
        comp1 = NexusComponent("bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng111",
                               "platform-public-front/platform-public-front",
                               "latest",
                               "http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/latest",
                               datetime.datetime(2022, 9, 9, 21, 8, 55, 867000, tzinfo=tzutc()))
        comp2 = NexusComponent("bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng222",
                               "platform-public-front/platform-public-front",
                               "sha-222222",
                               "http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/sha-222222",
                               datetime.datetime(2022, 9, 10, 22, 8, 55, 867000, tzinfo=tzutc()))
        comp3 = NexusComponent("bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng333",
                               "platform-public-front/platform-public-front",
                               "sha-333333",
                               "http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/sha-333333",
                               datetime.datetime(2022, 9, 11, 23, 8, 55, 867000, tzinfo=tzutc()))
        comp4 = NexusComponent("bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng444",
                               "platform-public-front/platform-public-front",
                               "sha-444444",
                               "http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/sha-444444",
                               datetime.datetime(2021, 5, 5, 6, 18, 55, 867000, tzinfo=tzutc()))
        comp5 = NexusComponent("bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng555",
                               "platform-public-front/platform-public-front",
                               "sha-555555",
                               "http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/sha-555555",
                               datetime.datetime(2022, 3, 7, 8, 8, 55, 867000, tzinfo=tzutc()))
        result["platform-public-front/platform-public-front"].append(comp1)
        result["platform-public-front/platform-public-front"].append(comp2)
        result["platform-public-front/platform-public-front"].append(comp3)
        result["platform-public-front/platform-public-front"].append(comp4)
        result["platform-public-front/platform-public-front"].append(comp5)
        return result


if __name__ == '__main__':
    pass

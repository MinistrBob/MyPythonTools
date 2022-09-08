import requests
import swagger_client
import nexus_helper
from swagger_client.rest import ApiException
from typing import List, NoReturn


class NexusHelper(object):
    def __init__(self, settings, log):
        self.log = log
        self.configuration = swagger_client.Configuration()
        self.configuration.host = settings.nexus_host
        self.configuration.username = settings.nexus_username
        self.configuration.password = settings.nexus_password
        self.configuration.debug = settings.DEBUG
        self.nexus_repo = settings.nexus_repo
        self.work_dir = settings.work_dir
        self.tags_yaml = os.path.join(self.work_dir, r"tags.yaml")
        self.bat = self.configuration.get_basic_auth_token()
        self.api_client = swagger_client.ApiClient(configuration=configuration, header_name='Authorization',
                                                   header_value=bat)

    def __str__(self):
        return f"host={self.configuration.host}|username={self.configuration.username}|bat={self.bat}"

    def nexus_download_tags(self, download_url: str) -> NoReturn:
        """
        Скачать файл tags.yaml из Nexus.

        Args:
            download_url: URL для скачивания.
        """
        r = requests.get(download_url, auth=(self.configuration.username, self.configuration.password))
        self.log.debug(f"{r.status_code}")
        with open(self.tags_yaml, "wb") as code:
            code.write(r.content)

    def nexus_upload_tags(self,
                          local_file=self.tags_yaml,
                          nexus_raw_directory=r'/',
                          nexus_raw_filename=r'tags.yaml') -> NoReturn:
        """
        Закачать файл tags.yaml в Nexus. По умолчанию, закачивается локальный tags.yaml в корень репозитория '/'.

        Args:
            local_file: Полный путь к локальному файлу tags.yaml.
            nexus_raw_filename: Имя файла в Nexus репо.
            nexus_raw_directory: Имя папки в Nexus репо.
        """
        api_instance = swagger_client.ComponentsApi(self.api_client)
        api_instance.upload_component(repository=self.nexus_repo, raw_directory=nexus_raw_directory,
                                      raw_asset1=local_file, raw_asset1_filename=nexus_raw_filename)

    def nexus_get_components(self) -> List[PageComponentXO]:
        api_instance = swagger_client.ComponentsApi(self.api_client)
        result = []
        i = 0
        page = None
        continuation_token = ''
        while 1 == 1:
            try:
                if i == 0:
                    page = api_instance.get_components(repository=self.nexus_repo)
                else:
                    page = api_instance.get_components(repository=self.nexus_repo,
                                                       continuation_token=continuation_token)
                self.log.debug(page)
            except ApiException as e:
                self.log.error("Exception when calling ComponentsApi->get_components: %s\n" % e)
            result.append(page)
            i += 1
            self.log.debug(f"Страница {i}")
            if page.continuation_token is None:
                break
            else:
                continuation_token = page.continuation_token
        self.log.debug(result)
        return result


if __name__ == '__main__':
    pass

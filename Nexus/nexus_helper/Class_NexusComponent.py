class NexusComponent(object):
    """
    Class for working with components.

    Example one item:
    {'assets': [{'checksum': {'sha1': '49aca14980cea02e050d08a0f240eee6e98d87e1',
                          'sha256': '6388bef639193359f86551f35b66ff2cc62cfc5a3610700f5c229df837840a90'},
             'content_type': 'application/vnd.docker.distribution.manifest.v2+json',
             'download_url': 'http://172.22.22.22:8081/repository/pp-docker/v2/platform-public-front/platform-public-front/manifests/latest',
             'format': 'docker',
             'id': 'bWludXN0LXBwLWRvY2tlcjoyZmZmNTA5YTdjMmE5ZWJlNmQyOGNlZGZlMjc5YjRmOA',
             'last_modified': datetime.datetime(2022, 9, 9, 11, 8, 55, 867000, tzinfo=tzutc()),
             'path': 'v2/platform-public-front/platform-public-front/manifests/latest',
             'repository': 'pp-docker'}],
     'format': 'docker',
     'group': None,
     'id': 'bWludXN0LXBwLWRvY2tlcjozZjVjYWUwMTc2MDIzM2I2NjUwMWRhYWVmOGY3MDk4Ng',
     'name': 'platform-public-front/platform-public-front',
     'repository': 'pp-docker',
     'version': 'latest'}
    """

    __slots__ = ['id', 'name', 'version', 'download_url', 'last_modified']

    def __init__(self, id_, name, version, download_url, last_modified):
        self.id = id_
        self.name = name
        self.version = version
        self.download_url = download_url
        self.last_modified = last_modified

    def __str__(self):
        return f"{download_url}:{version}"


def main():
    pass


if __name__ == '__main__':
    main()

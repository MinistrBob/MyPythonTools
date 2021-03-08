import gitlab
import dateutil.parser
import custom_logger
import os
import gitlab_app_conf as conf

"""
<class 'gitlab.v4.objects.ProjectRegistryRepository'> => {'id': 1014301, 'name': 'bff', 'path': 'i-teco/rostourism-registry-backend/bff', 'project_id': 16881551, 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff', 'created_at': '2020-04-03T12:52:32.289Z', 'cleanup_policy_started_at': None}
<class 'gitlab.v4.objects.ProjectRegistryTag'> => {'name': 'latest', 'path': 'i-teco/rostourism-registry-backend/bff:latest', 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff:latest'}
<class 'gitlab.v4.objects.ProjectRegistryTag'> => {'name': 'latest', 'path': 'i-teco/rostourism-registry-backend/bff:latest', 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff:latest', 'revision': '210a384c17317d973ebe357524d8a1f864823152ec361e12d4f70e83e3a034d6', 'short_revision': '210a384c1', 'digest': 'sha256:994bd8969892e4094c9373d2af595b2993a706b57e22b431f74f9806d299140a', 'created_at': '2021-02-18T14:22:12.958+00:00', 'total_size': 156780434}
"""


class MyGitLab:

    def __init__(self, glo: object, log: object):
        self.glo = glo
        self.log = log

    # Print iterations progress
    def printProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

    def print_list(self, list_: list, indent=0):
        if indent == 0:
            for item in list_:
                print(item)
        else:
            indent = ' ' * indent
            for item in list_:
                print(f"{indent}{item}")

    def get_list_project_repositories(self, project_id: int) -> list:
        project = self.glo.projects.get(project_id)
        return project.repositories.list()

    def print_list_project_repositories(self, project_id: int, indent=0):
        self.print_list(self.get_list_project_repositories(project_id), indent)

    def get_list_repository_tags(self, repo: object, full=False) -> list:
        if full:
            list_tags = []
            for tag in repo.tags.list():
                list_tags.append(repo.tags.get(id=tag.name))
            return list_tags
        else:
            return repo.tags.list()

    def print_list_repository_tags(self, repo: object, full, indent=0):
        self.print_list(self.get_list_repository_tags(repo, full), indent)

    def get_max_tags_in_project(self, project_id: int) -> list:
        repositories = self.get_list_project_repositories(project_id)
        list_tags = []
        i = 1
        for repo in repositories:
            self.log.info(f"\n{repo}")
            tags = self.get_list_repository_tags(repo)
            print(f"REPO: {repo.name} | {i} of {len(repositories)} | {len(tags)} tags")
            max_datetime = dateutil.parser.isoparse("1900-01-01T00:00:00.000Z")
            j = 0
            for tag in tags:
                self.log.info(f"\n{tag}")
                self.printProgressBar(j, len(tags), prefix=f"{repo.name}|{tag.name}", suffix='Complete', length=50)
                current_tag = repo.tags.get(id=tag.name)
                current_datetime = dateutil.parser.isoparse(current_tag.created_at)
                if current_datetime > max_datetime:
                    last_tag = current_tag
                    max_datetime = current_datetime
                j += 1
                self.printProgressBar(j, len(tags), prefix=f"{repo.name}|{tag.name}", suffix='Complete', length=50)
            list_tags.append(last_tag)
            i += 1
        return list_tags

    def print_max_tags_in_project(self, project_id: int, indent=0):
        self.print_list(self.get_max_tags_in_project(project_id), indent)


# project_id = 16881551
# project = gl.projects.get(project_id)
# repositories = project.repositories.list()
# for repos in repositories:
#     print(repos)
#     tags = repos.tags.list()
#     max_datetime = dateutil.parser.isoparse(repos.created_at)
#     print(max_datetime)
#     for tag in tags:
#         print(f"    {tag}")
#         current_tag = repos.tags.get(id=tag.name)
#         print(f"        {current_tag}")
#         current_datetime = dateutil.parser.isoparse(current_tag.created_at)
#         if current_datetime > max_datetime:
#             last_tag = current_tag
#             max_datetime = current_datetime
#     print(max_datetime)
#     print(last_tag)
#     break

if __name__ == '__main__':
    program_file = os.path.realpath(__file__)
    the_custom_logger = custom_logger.get_logger(program_file=program_file)
    # private token or personal token authentication
    the_gitlab_obj = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    my_gitlab = MyGitLab(the_gitlab_obj, the_custom_logger)

    # Список репозитариев в проекте
    # my_gitlab.print_list_project_repositories(conf.project_dict["rostourism-images"])

    # Список тэгов в проекте
    repositories = my_gitlab.get_list_project_repositories(conf.project_dict["rostourism-registry-backend"])
    for repo in repositories:
        print(repo)
        my_gitlab.print_list_repository_tags(repo, full=True, indent=4)

    # Список самых последних тэгов в проекте
    # my_gitlab.print_max_tags_in_project(conf.project_dict["rostourism-registry-backend"])

    # Список проектов их репозиториев и самых последних тэгов
    # for name, repo_id in conf.project_dict.items():
    #     print(name, repo_id)
    #     my_gitlab.print_list_project_repositories(repo_id, indent=2)
    #     my_gitlab.print_max_tags_in_project(repo_id, indent=4)

    print("The end!")

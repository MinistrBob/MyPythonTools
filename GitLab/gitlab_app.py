import gitlab
# import dateutil.parser
import common.custom_logger as custom_logger
import os
import gitlab_app_conf as conf
import MyGitLab

"""
<class 'gitlab.v4.objects.ProjectRegistryRepository'> => {'id': 1014301, 'name': 'bff', 'path': 'i-teco/rostourism-registry-backend/bff', 'project_id': 16881551, 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff', 'created_at': '2020-04-03T12:52:32.289Z', 'cleanup_policy_started_at': None}
<class 'gitlab.v4.objects.ProjectRegistryTag'> => {'name': 'latest', 'path': 'i-teco/rostourism-registry-backend/bff:latest', 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff:latest'}
<class 'gitlab.v4.objects.ProjectRegistryTag'> => {'name': 'latest', 'path': 'i-teco/rostourism-registry-backend/bff:latest', 'location': 'registry.gitlab.com/i-teco/rostourism-registry-backend/bff:latest', 'revision': '210a384c17317d973ebe357524d8a1f864823152ec361e12d4f70e83e3a034d6', 'short_revision': '210a384c1', 'digest': 'sha256:994bd8969892e4094c9373d2af595b2993a706b57e22b431f74f9806d299140a', 'created_at': '2021-02-18T14:22:12.958+00:00', 'total_size': 156780434}
"""

if __name__ == '__main__':
    program_file = os.path.realpath(__file__)
    the_custom_logger = custom_logger.get_logger(program_file=program_file)
    # private token or personal token authentication
    the_gitlab_obj = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    my_gitlab = MyGitLab(the_gitlab_obj, the_custom_logger)

    # Список репозитариев в проекте
    # my_gitlab.print_list_project_repositories(conf.project_dict["rostourism-images"])

    # Список тэгов в проекте
    # repositories = my_gitlab.get_list_project_repositories(conf.project_dict["rostourism-registry-backend"])
    # for repo in repositories:
    #     print(repo)
    #     my_gitlab.print_list_repository_tags(repo, full=True, indent=4)

    # Список самых последних тэгов в проекте
    # my_gitlab.print_max_tags_in_project(conf.project_dict["rostourism-registry-backend"])

    # Список проектов их репозиториев и самых последних тэгов
    # for name, repo_id in conf.project_dict.items():
    #     print(name, repo_id)
    #     my_gitlab.print_list_project_repositories(repo_id, indent=2)
    #     my_gitlab.print_max_tags_in_project(repo_id, indent=4)

    print("The end!")

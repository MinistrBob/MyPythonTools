import gitlab
# import dateutil.parser
import common.custom_logger as custom_logger
import os
import gitlab_app_conf as conf
from GitLab import MyGitLab

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

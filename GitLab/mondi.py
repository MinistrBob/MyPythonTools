"""
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.
The script periodically monitors the appearance of a new version of the docker image.
If a new version is found, an action is taken, such as deploying the application.
"""
import os

import gitlab

import SETTINGS_mondi
import custom_logger
from mygitlab import MyGitLab

if __name__ == '__main__':
    settings = SETTINGS_mondi.get_settings()
    program_file = os.path.realpath(__file__)
    log = custom_logger.get_logger(settings)

    # personal token authentication (GitLab.com)
    gl = gitlab.Gitlab(private_token=settings.private_token, retry_transient_errors=True, timeout=60)

    # Get project
    project = gl.projects.get(id=settings.project_id)
    print(project)

    repositories = project.repositories.list(all=True)
    for repository in repositories:
        # print(repository)
        if repository.id in settings.repo_id:
            print(repository)
            tags = repository.tags.list(all=True)
            for tag in tags:
                print(tag)

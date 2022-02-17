"""
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.
The script periodically monitors the appearance of a new version of the docker image.
If a new version is found, an action is taken, such as deploying the application.
"""
import os
import requests
import gitlab

import SETTINGS_mondi
import custom_logger
from mygitlab import MyGitLab


# Because an image with two tags "latest" and "sha-ecd87758" is published to the repository at once,
# then you can use digest to identify the specific last tag.
def get_latest_tag(tags_dict):
    latest_digest = tags_dict['latest']
    for name, digest in tags_dict.items():
        if name != 'latest' and digest == latest_digest:
            # print(name)
            return name


if __name__ == '__main__':
    settings = SETTINGS_mondi.get_settings()
    program_file = os.path.realpath(__file__)
    log = custom_logger.get_logger(settings)
    log.info(print("\n" * 3))

    # personal token authentication (GitLab.com)
    gl = gitlab.Gitlab(private_token=settings.private_token, retry_transient_errors=True, timeout=60)

    # Get project
    project = gl.projects.get(id=settings.project_id)
    # print(project)

    # Get latest_tags dict {'image1': 'sha-7d1d28c7', 'image2': 'sha-ecd87758'}
    repositories = project.repositories.list(all=True)
    latest_tags = {}
    for repository in repositories:
        # print(repository)
        if repository.id in settings.repo_id:
            print("\n" * 3)
            # print(repository)
            tags = repository.tags.list(all=True)
            tags_dict = {}
            for tag in tags:
                # print(tag)
                url = f"https://gitlab.com/api/v4/projects/{settings.project_id}/registry/repositories/{repository.id}/tags/{tag.name}"
                # print(url)
                headers = {'PRIVATE-TOKEN': f'{settings.private_token}'}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                digest = response.json()['digest']
                # print(digest)
                tags_dict[tag.name] = digest
            print(tags_dict)
            latest_tag = get_latest_tag(tags_dict)
            print(latest_tag)
            latest_tags[repository.name] = latest_tag
    print(latest_tags)

    # Compare latest_tags dict with saved on disk.
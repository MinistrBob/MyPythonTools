"""
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.
The script periodically monitors the appearance of a new version of the docker image.
If a new version is found, an action is taken, such as deploying the application.
"""
import os
import requests
import gitlab
import datetime

import SETTINGS_mondi
import custom_logger
from mygitlab import MyGitLab
from kubernetes import client, config


# Because an image with two tags "latest" and "sha-ecd87758" is published to the repository at once,
# then you can use digest to identify the specific last tag.
def get_latest_tag(tags_dict):
    latest_digest = tags_dict['latest']
    for name, digest in tags_dict.items():
        if name != 'latest' and digest == latest_digest:
            return name


def execute_cmd(cmd, log, cwd_=None, message=None, message_prefix=None, output_prefix=None):
    """
    Execute cmd command (execute_cmd(cmd, cwd_="backend/deployment"))
    :param log: Logger.
    :param cmd: Executed command (r"rsync -vrt --exclude 'backup.cmd' --exclude 'config.yaml' /home/ci/script/backend/ci/ /home/ci/script/")
    :param cwd_: Working dir (cwd_="backend/deployment")
    :param message: Add message, before executed command.
    :param message_prefix: Prefix before every log message (f"... ")
    :param output_prefix: Add message, after executed command.
    :return: Output executed command
    """
    out = ""
    if not message_prefix:
        message_prefix = ""
    if not output_prefix:
        output_prefix = ""
    if message:
        log.info(f"{message_prefix}{message}")
    else:
        log.info(f"{message_prefix}{cmd}")

    try:
        # output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, )
        completed_process = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd_)
    except subprocess.CalledProcessError as exc:
        out = f"ERROR:\n{exc.returncode}\n{exc.output}"
        log.error(out)
        exit(777)
    else:
        # out = output.decode("utf-8")
        out = completed_process.stdout
        log.info(f'{output_prefix}{completed_process.stdout}')

    return out


if __name__ == '__main__':
    begin_time = datetime.datetime.now()
    # Get settings
    settings = SETTINGS_mondi.get_settings()

    # Get logging
    program_file = os.path.realpath(__file__)
    log = custom_logger.get_logger(settings)
    log.info("\n" * 3)

    # personal token authentication (GitLab.com)
    gl = gitlab.Gitlab(private_token=settings.private_token, retry_transient_errors=True, timeout=60)

    # Get project
    project = gl.projects.get(id=settings.project_id)
    log.debug(f'project={project}')

    # Get latest_tags dict
    repositories = project.repositories.list(all=True)
    latest_tags = {}
    for repository in repositories:
        log.debug(f"repository={repository}")
        if repository.id in settings.repo_id:
            log.debug("\n" * 3)
            tags = repository.tags.list(all=True)
            tags_dict = {}
            for tag in tags:
                log.debug(f"tag={tag}")
                url = f"https://gitlab.com/api/v4/projects/{settings.project_id}/registry/repositories/{repository.id}/tags/{tag.name}"
                log.debug(f"url={url}")
                headers = {'PRIVATE-TOKEN': f'{settings.private_token}'}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                digest = response.json()['digest']
                log.debug(f"digest={digest}")
                tags_dict[tag.name] = digest
            log.debug(f"tags_dict={tags_dict}")
            latest_tag = get_latest_tag(tags_dict)
            log.debug(f"latest_tag={latest_tag}")
            latest_tags[repository.name] = latest_tag
    log.info(f"Latest tags: {latest_tags}")  # {'image1': 'sha-7d1d28c7', 'image2': 'sha-ecd87758'}

    # Compare latest_tags dict with info from kubernetes and run ci application if needed
    config.load_kube_config(config_file=settings.kube_config_file)
    v1 = client.AppsV1Api()
    deploy_list = ""
    for deployment_name in settings.kube_deployments_name:
        ret = v1.read_namespaced_deployment(deployment_name, settings.kube_namespace)
        log.debug(f"ret={ret}")
        image = ret.spec.template.spec.containers[0].image
        log.debug(f"image={image}")
        image_list = image.split(':')
        log.debug(f"image_list={image_list}")
        image_name = image_list[0].split('/')[-1]
        tag = image_list[1]
        log.debug(f"image_name={image_name}; tag={tag}")
        if latest_tags[image_name] != tag:
            deploy_list = f"{deploy_list} {image_name}={tag}"

    # Execute CI
    cmd = f"/home/ci/script/ci.sh deploy {deploy_list}"
    log.info(f"Start CI process for {deploy_list}")
    execute_cmd(cmd, log)

    log.info(f"Program completed")
    log.info(f"Total time spent: {datetime.datetime.now() - begin_time} sec.")

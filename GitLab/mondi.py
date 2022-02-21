"""
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.
The script periodically monitors the appearance of a new version of the docker image.
If a new version is found, an action is taken, such as deploying the application.
"""
import datetime
import os
import subprocess
import traceback
import sys

import gitlab
import requests
from kubernetes import client, config

import custom_logger


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

    completed_process = None
    try:
        # output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True, )
        completed_process = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True, cwd=cwd_)
    except subprocess.CalledProcessError as exc:
        out = f"ERROR1:\n{exc.returncode}\n{exc.output}"
        raise Exception(out)
    else:
        # out = output.decode("utf-8")
        out = completed_process.stdout
        log.info(f'{output_prefix}{completed_process.stdout}')

    return out


def send_telegram_msg(text):
    url_req = f"https://api.telegram.org/bot{settings.token}/sendMessage?chat_id={settings.chat_id}&disable_web_page_preview=1&text={text}"
    results = requests.get(url_req)
    # print(results.json())
    return results.json()


def main(settings, log):
    log.info(" ")
    log.info(f"Get latest tags from Gitlab container registry")
    # personal token authentication (GitLab.com)
    gl = gitlab.Gitlab(private_token=settings.gitlab_private_token, retry_transient_errors=True, timeout=60)
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
                headers = {'PRIVATE-TOKEN': f'{settings.gitlab_private_token}'}
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                digest = response.json()['digest']
                log.debug(f"digest={digest}")
                tags_dict[tag.name] = digest
            log.debug(f"tags_dict={tags_dict}")
            latest_tag = get_latest_tag(tags_dict)
            log.debug(f"latest_tag={latest_tag} for {repository.name}")
            latest_tags[repository.name] = latest_tag
    log.info(f"Latest tags: {latest_tags}")  # {'russia-travel-ntp': 'sha-dd87264d', 'russia-travel': 'sha-ecd87758'}

    # Compare latest_tags dict with info from kubernetes
    log.info(" ")
    log.info(f"Compare latest_tags dict with info from kubernetes")
    config.load_kube_config(config_file=settings.kube_config_file)
    v1 = client.AppsV1Api()
    deploy_images_str = ""
    for deployment_name in settings.kube_deployments_name:
        ret = v1.read_namespaced_deployment(deployment_name, settings.kube_namespace)
        # log.debug(f"ret={ret}")
        image = ret.spec.template.spec.containers[0].image
        log.debug(f"image={image}")
        image_list = image.split(':')
        log.debug(f"image_list={image_list}")
        image_name = image_list[0].split('/')[-1]
        tag = image_list[1]
        log.debug(f"image_name={image_name}; tag={tag}")  # image_name=russia-travel-ntp; tag=sha-98266fe1
        if latest_tags[image_name] != tag:  # new tag compare old tag
            deploy_images_str = f"{deploy_images_str} {settings.config_yaml[image_name]}={latest_tags[image_name]}"
            log.debug(f"deploy_images_str={deploy_images_str}")

    # Execute CI application if needed
    log.info(" ")
    log.info(f"Execute CI application if needed")
    if deploy_images_str:
        # cmd = f"eval $(ssh-agent -s)"
        # execute_cmd(cmd, log)
        # cmd = f"cat {settings.ssh_key} | tr -d '\r' | ssh-add -"
        # execute_cmd(cmd, log)
        cmd = f"ssh -i {settings.ssh_key} -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no {settings.ssh_user}@{settings.ssh_host} /home/ci/script/ci.sh deploy{deploy_images_str}"
        execute_cmd(cmd, log)

        # cmd = f"/home/ci/script/ci.sh deploy{deploy_images_str}"  # space doesn't need it is in deploy_list
        # log.info(f"Start CI process for {deploy_images_str}")  # russia-travel=sha-b39fc2a6 russia-travel-ntp=sha-98266fe1
        # execute_cmd(cmd, log)
        send_telegram_msg(f"✅ ``` mondi.py ```%0A%0Aupdated {deploy_images_str}")
    else:
        log.info(f"Execute CI application NOT needed")


if __name__ == '__main__':
    begin_time = datetime.datetime.now()
    # Get settings
    sys.path.append(r"/mondi")
    import SETTINGS_mondi
    settings = SETTINGS_mondi.get_settings()

    # Get logging
    program_file = os.path.realpath(__file__)
    log = custom_logger.get_logger(settings)

    # The program start
    log.info("\n" * 3)
    log.info("=" * 80)
    log.info("****  PROGRAM MONDI.PY  ****".center(80, " "))
    log.info("=" * 80)
    # log.debug(f"settings=\n{settings}")

    # in case of any error notification in telegram
    try:
        main(settings, log)
    except Exception as err:
        log.error(f"ERROR:\n{err}")
        log.error(f"TRACE:\n{traceback.format_exc()}")
        send_telegram_msg(f"❌ ``` mondi.py ```%0A%0AERROR:\n{err}")
        exit(1)

    log.info(" ")
    log.info(f"Program completed")
    log.info(f"Total time spent: {datetime.datetime.now() - begin_time} sec.")
    log.info("****  THE END.  ****".center(80, " "))
    log.info("\n" * 3)

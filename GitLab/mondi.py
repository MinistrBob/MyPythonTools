"""
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.
The script periodically monitors the appearance of a new version of the docker image.
If a new version is found, an action is taken, such as deploying the application.
"""
import gitlab
import MyGitLab
import common.custom_logger as cl


if __name__ == '__main__':
    program_file = os.path.realpath(__file__)
    the_custom_logger = custom_logger.get_logger(program_file=program_file)
    # private token or personal token authentication
    the_gitlab_obj = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    my_gitlab = MyGitLab(the_gitlab_obj, the_custom_logger)

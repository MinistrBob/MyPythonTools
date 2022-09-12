import logging
import os
import re
import sys
import traceback

import yaml

from nexus_helper.nexus_helper import NexusHelper

# Program settings
settings = {}
# Program logger
logger = logging.getLogger()


def main():
    # Get app settings
    try:
        get_settings()
    except Exception:
        print(f"ERROR: app cannot get settings\n{traceback.format_exc()}")
        exit(1)
    # Create app logger
    set_logger()
    logger.debug(settings)
    # Читаем списки правил для каждого репо из rules.yaml
    with open("rules.yaml", "r") as stream:
        try:
            rules_yaml = yaml.safe_load(stream)
        except yaml.YAMLError as err:
            logger.error(f"ERROR: {err}\n{traceback.format_exc()}")
    logger.debug(rules_yaml)
    repos = rules_yaml['repos']
    # Обрабатываем каждый репозиторий
    for repo in repos:
        logger.info(f"Work with {repo} repo")
        settings.nexus_repo = repo
        nexus = NexusHelper(settings, logger)
        if settings.DEBUG:
            result = nexus.fake_get_list_component_items()
        else:
            result = nexus.get_list_component_items()
        logger.debug(result)
        logger.debug(f"Всего {len(result)} items")
        # Из списка result удалить все образы которые соответствуют правилам exclude_rules.
        logger.info(f"Apply exclude_rules")
        exclude_rules = repos[repo]['exclude_rules']
        logger.debug(exclude_rules)
        for rule in exclude_rules:
            rule = rule['rule']
            logger.debug(f"{type(rule)} | {rule}")
            for name in list(result.keys()):
                if re.search(rule, name):
                    logger.debug(f"{rule} | {name}")
                    del result[name]
        logger.debug(f"После exclude_rules всего {len(result)} items")
        logger.debug(result)
        # Оставшиеся образы обрабатываем правилами include_rules.
        logger.info(f"Apply include_rules")
        include_rules = repos[repo]['include_rules']
        logger.debug(include_rules)
        for rule in include_rules:
            rule_rule = rule['rule']
            logger.debug(f"{type(rule_rule)} | {rule_rule}")
            for name in list(result.keys()):
                if re.search(rule_rule, name):
                    logger.debug(f"{rule_rule} | {name}")
                    # TODO оставить Save last XXX images.
                    # Сортируем list of components (NexusComponent) по reverse last_modified и берём всё что далее last.
                    result[name].sort(reverse=True, key=lambda comp: comp.last_modified)
                    for i in result[name]:
                        print(f"{i.name} | {i.last_modified}")
                    # TODO остальные проверить на > days и удалить.
                    list_for_check_days = result[name][rule['last']:]
                    print("Check date")
                    for comp in list_for_check_days:
                        print(f"{comp.name} | {comp.last_modified}")


class Settings(object):
    """
    Program settings like class
    """

    def __init__(self, iterable=(), **kwargs):
        self.__dict__.update(iterable, **kwargs)

    def __str__(self):
        return str(self.__dict__)


def get_settings():
    global settings
    # Enable DEBUG mode?
    settings['DEBUG'] = os.getenv("NX_DEBUG", 'False').lower() in 'true'
    settings['nexus_host'] = os.getenv('NX_HOST', "Unknown")
    settings['nexus_username'] = os.getenv('NX_USERNAME', "Unknown")
    settings['nexus_password'] = os.getenv('NX_PASSWORD', "Unknown")
    settings['nexus_repo'] = os.getenv('NX_REPO', "Unknown")
    settings = Settings(settings)


def set_logger():
    # Log to stdout
    global logger
    if settings.DEBUG:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    stdout_log_formatter = logging.Formatter('%(asctime)s|%(levelname)-5s|%(funcName)s| %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_log_formatter)
    logger.addHandler(stdout_handler)


if __name__ == '__main__':
    main()

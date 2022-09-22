import logging
import os
import re
import sys
import traceback

import yaml
from datetime import datetime, timedelta, timezone
from nexus_helper.nexus_helper import NexusHelper
from zmpe import raise_error

# Program settings
settings = {}
# Program logger
logger = logging.getLogger()


def main():
    mine_time = datetime.now()

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
            raise_error(settings, logger, program=settings.PROGRAM, hostname=settings.HOSTNAME,
                        message=f"{err}\n{traceback.format_exc()}", do_error_exit=True)
    logger.debug(rules_yaml)
    repos = rules_yaml['repos']

    try:
        count = 0
        # Обрабатываем каждый репозиторий
        for repo in repos:
            logger.info(f"Work with {repo} repo")
            settings.nexus_repo = repo
            nexus = NexusHelper(settings, logger)
            if settings.DEV:
                result = nexus.fake_get_list_component_items()
            else:
                result = nexus.get_list_component_items()
            logger.debug(result)
            logger.debug(f"Всего {len(result)} items")

            # Из списка result удалить все образы которые соответствуют правилам exclude_rules.
            logger.info(f" ")
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
            logger.info(f" ")
            logger.debug(f"После exclude_rules осталось {len(result)} items")
            logger.debug(result)

            # Оставшиеся образы обрабатываем правилами include_rules.
            logger.info(f" ")
            logger.info(f"Apply include_rules")
            include_rules = repos[repo]['include_rules']
            logger.debug(include_rules)
            for rule in include_rules:  # Цикл по каждому правилу
                rule_rule = rule['rule']
                logger.debug(f" ")
                logger.debug(f"    {type(rule_rule)} | {rule_rule}")
                for name in list(result.keys()):  # Выбираем из списка всех образов те которые соответствуют правилу
                    if re.search(rule_rule, name):
                        logger.debug(f"    {rule_rule} | {name}")

                        logger.info(f"Save last {rule['last']} images")
                        # Сортируем list of components (NexusComponent) по reverse last_modified и берём всё что далее last.
                        # Т.е. сохраняем [rule['last'] образов.
                        result[name].sort(reverse=True, key=lambda comp: comp.last_modified)
                        for i in result[name][0:rule['last']]:
                            logger.debug(f"    {i.name}:{i.version} | {i.last_modified}")
                        list_for_check_days = result[name][rule['last']:]

                        logger.info(f"Delete images older than {rule['days']} days")
                        for comp in list_for_check_days:
                            # logger.debug(f"    {comp.name}:{comp.version} | {comp.last_modified}")
                            if (datetime.now(timezone.utc) - comp.last_modified).days > rule['days']:
                                logger.info(f"Delete component {comp.name}:{comp.version} | {comp.last_modified}")
                                nexus.delete(id=comp.id)
                                count += 1
    except Exception as err:
        result = {'cleaner-result': 1, 'cleaner-time': 0, 'cleaner-count': 0}
        zabbix_sender(settings, logger, result)
        raise_error(settings, logger, program=settings.PROGRAM, hostname=settings.HOSTNAME,
                    message=f"{err}\n{traceback.format_exc()}", do_error_exit=True)

    time_execution = round((datetime.now() - mine_time).total_seconds())
    logger.info(f"Process executed in {time_execution} sec.")
    # Send Zabbix info
    if settings.ZM_ZABBIX_SEND:
        try:
            result = {'cleaner-result': 0, 'cleaner-time': time_execution, 'cleaner-count': count}
            zabbix_sender(settings, logger, result)
        except Exception as err:
            raise_error(settings, logger, program=settings.PROGRAM, hostname=settings.HOSTNAME,
                        message=f"Cannot send data to Zabbix\n{err}\n{traceback.format_exc()}", do_error_exit=True)


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
    # Get program name (without extension so that telegram does not convert the program name into a link)
    settings['PROGRAM'] = os.path.splitext(os.path.basename(__file__))[0]
    # Telegram settings
    settings['ZM_TELEGRAM_NOTIF'] = os.getenv("ZM_TELEGRAM_NOTIF", 'True').lower() in 'true'
    settings['ZM_TELEGRAM_CHAT'] = os.getenv('ZM_TELEGRAM_CHAT', "Unknown")
    settings['ZM_TELEGRAM_BOT_TOKEN'] = os.getenv('ZM_TELEGRAM_BOT_TOKEN', "Unknown")
    # Zabbix settings
    # Should app send data to Zabbix?
    settings['ZM_ZABBIX_SEND'] = os.getenv("ZM_ZABBIX_SEND", 'True').lower() in 'true'
    # Zabbix server ip address.
    settings['ZM_ZABBIX_IP'] = os.getenv('ZM_ZABBIX_IP', None)
    # Zabbix "Host name". How is the host named in Zabbix.
    settings['ZM_ZABBIX_HOST_NAME'] = os.getenv('ZM_ZABBIX_HOST_NAME', None)
    # Add settings
    settings['DEV'] = os.getenv("NX_DEV", 'False').lower() in 'true'
    settings['HOSTNAME'] = settings['ZM_ZABBIX_HOST_NAME']

    # Check required setting
    if settings.ZM_TELEGRAM_NOTIF and \
            (not settings.ZM_TELEGRAM_BOT_TOKEN or not settings.ZM_TELEGRAM_CHAT):
        print(f"ERROR: Telegram notifications are enabled but the parameters ZM_TELEGRAM_BOT_TOKEN, ZM_TELEGRAM_CHAT "
              f"are not defined")
        exit(1)
    if settings.ZM_ZABBIX_SEND and \
            (not settings.ZM_ZABBIX_IP or not settings.ZM_ZABBIX_HOST_NAME or not settings.ZM_ZABBIX_ITEM_NAME):
        print(f"ERROR: Send data to Zabbix are enabled but the parameters ZM_ZABBIX_IP, ZM_ZABBIX_HOST_NAME, "
              f"ZM_ZABBIX_ITEM_NAME are not defined")
        exit(1)
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

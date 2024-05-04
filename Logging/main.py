import custom_logger
from SETTINGS import app_settings as appset
from module2 import func2

log = custom_logger.get_logger(appset)


def main():
    log.debug('This is debug message')
    log.info('This is info message')
    log.warning('This is warning message')
    log.error('This is error message')
    log.critical('This is critical message')


if __name__ == '__main__':
    main()
    func2()

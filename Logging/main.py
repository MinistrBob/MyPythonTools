import custom_logger
from SETTINGS import app_settings as appset
from module2 import func2

log = custom_logger.get_logger(appset)


def main():
    log.info('Hello, World!')


if __name__ == '__main__':
    main()
    func2()

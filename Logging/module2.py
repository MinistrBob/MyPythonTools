import logging

log = logging.getLogger("teleservice-logger")


def func2():
    log.info('module2 str')


if __name__ == '__main__':
    func2()

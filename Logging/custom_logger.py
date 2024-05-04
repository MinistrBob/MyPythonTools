import logging
import os
import shutil
import sys
import traceback
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """Logging colored formatter, adapted from https://stackoverflow.com/a/56944256/3638629
    The color coding \x1b[38;21m you're seeing is an ANSI escape code for setting text color in terminal output. In this case, it sets the text color to grey.
    Here's a breakdown of the code:
    \x1b: Escape character indicating the start of an escape sequence.
    [38;21m: ANSI escape sequence for setting the foreground (text) color.
    In more detail:
    38: Select the foreground color.
    21: Set the color to grey.

    """
    # Здесь белый текст на "черном" фоне, но реально здесь 0m это просто фон (default), он в консоли обычно не чёрный,
    # а сероватый. ChatGPT выдал мне для белого текста на чёрном фоне такой код: white_on_black = '\x1b[97;40m'
    white_on_black = '\x1b[97;0m'
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    red = '\x1b[38;5;196m'
    bold_red = '\x1b[31;1m'
    reset = '\x1b[0m'

    def __init__(self, fmt):
        super().__init__()
        self.fmt = fmt
        self.FORMATS = {
            logging.DEBUG: self.grey + self.fmt + self.reset,
            logging.INFO: self.white_on_black + self.fmt + self.reset,
            logging.WARNING: self.yellow + self.fmt + self.reset,
            logging.ERROR: self.red + self.fmt + self.reset,
            logging.CRITICAL: self.bold_red + self.fmt + self.reset
        }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger(settings):
    """
    The procedure creates a logger based on either program_file or log_file.
    Logging is done by default to the folder where the script/log is located
    :param settings: Application settings
    :return: logger
    """
    # Define the logging level
    if settings.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Formation of custom_logger. Log everything to stdout, and if necessary, to a file.
    # log_formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(process)d:%(thread)d - %(message)s')
    custom_logger = logging.getLogger(settings.logger_name)
    custom_logger.setLevel(log_level)
    stdout_handler = logging.StreamHandler(sys.stdout)
    # Здесь LOGLEVEL выравнивается до 7 символов так нормально центруются все уровни кроме CRITICAL,
    # но т.к. он редко используется им можно пренебречь
    fmt = r'%(asctime)s|%(levelname)-7s|%(funcName)s| %(message)s'
    # stdout_handler.setFormatter(logging.Formatter(fmt))
    stdout_handler.setFormatter(CustomFormatter(fmt))
    custom_logger.addHandler(stdout_handler)
    if settings.log_to_file:
        # Log file example /home/<user>/script/log/app.log
        log_dir = os.path.join(settings.work_dir, 'log')
        log_name = "app.log"
        log_file_ = os.path.join(log_dir, log_name)

        if os.path.exists(log_file_):
            # Rotate the log file if necessary. Because it can be difficult to determine the date a file was created in Linux,
            # read the first line of the log file and parse the date from there.
            # 2021-06-07 13:49:54,870|    INFO|
            with open(log_file_, encoding="utf-8") as f:
                first_line = f.readline()[0:10]
            try:
                create_date = datetime.strptime(first_line, '%Y-%m-%d')
                if (datetime.now() - create_date).days > settings.log_file_period_days:
                    # Ротировать лог файл
                    shutil.move(log_file_, os.path.join(log_dir, f"app-{first_line}.log"))
            except Exception as err:
                print("\nWARNING!!!: File rotation failed\n" + traceback.format_exc())
        else:
            # If the directory for logging does not exist, create it
            if not os.path.exists(log_dir):
                try:
                    os.mkdir(log_dir)
                except OSError:
                    print(f"Creation of the directory {log_dir} failed")
                    exit(1)

        # Create a file_handler and add it to the main logger
        file_log_formatter = logging.Formatter('%(asctime)s|%(levelname)8s| %(message)s')
        file_handler = logging.FileHandler(log_file_, mode='a', encoding='utf-8')
        file_handler.setFormatter(file_log_formatter)
        custom_logger.addHandler(file_handler)
    # print(custom_logger.handlers[0].baseFilename)

    return custom_logger

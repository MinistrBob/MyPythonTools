import logging
import os
import shutil
import sys
import traceback
from datetime import datetime


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
    custom_logger = logging.getLogger("teleservice-logger")
    custom_logger.setLevel(log_level)
    stdout_log_formatter = logging.Formatter('%(asctime)s|%(levelname)-5s|%(funcName)s| %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_log_formatter)
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

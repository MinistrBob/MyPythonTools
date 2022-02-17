import logging
import os
import shutil
import sys
import traceback
from datetime import datetime


def get_logger(settings):
    """
    Процедура создаёт logger на основе либо program_file либо log_file.
    Логирование по умолчанию производится в папку где лежит скрипт/log
    :param settings: Настройки приложения
    :return: logger
    """
    # Определение уровня логирования
    if settings.DEBUG:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    # Формирование custom_logger. Логируем всё в stdout, а если нужно, то еще и в файл.
    # log_formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(name)s|%(process)d:%(thread)d - %(message)s')
    custom_logger = logging.getLogger()
    custom_logger.setLevel(log_level)
    stdout_log_formatter = logging.Formatter('%(asctime)s|%(levelname)8s| %(message)s')
    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(stdout_log_formatter)
    custom_logger.addHandler(stdout_handler)
    if settings.log_to_file:
        # Лог файл /home/ci/script/log/ci.log
        log_dir = os.path.join(settings.work_dir, 'log')
        log_name = "ci.log"
        log_file_ = os.path.join(log_dir, log_name)

        if os.path.exists(log_file_):
            # Ротация лог файла если нужно. Из-за того что определить дату создания файла в Linux может быть сложным,
            # зачитываем первую строку лог файла и парсим оттуда дату.
            # 2021-06-07 13:49:54,870|    INFO|
            with open(log_file_) as f:
                first_line = f.readline()[0:10]
            try:
                create_date = datetime.strptime(first_line, '%Y-%m-%d')
                if (datetime.now() - create_date).days > settings.log_file_period_days:
                    # Ротировать лог файл
                    shutil.move(log_file_, os.path.join(log_dir, f"ci-{first_line}.log"))
            except Exception as err:
                print("\nWARNING!!!: Ротация файла не удалась\n" + traceback.format_exc())
        else:
            # Если директории для логирования не существует создаём её
            if not os.path.exists(log_dir):
                try:
                    os.mkdir(log_dir)
                except OSError:
                    print(f"Creation of the directory {log_dir} failed")
                    exit(1)

        # Формируем file_handler и добавляем его в основной logger
        file_log_formatter = logging.Formatter('%(asctime)s|%(levelname)8s| %(message)s')
        file_handler = logging.FileHandler(log_file_, mode='a', encoding='utf-8')
        file_handler.setFormatter(file_log_formatter)
        custom_logger.addHandler(file_handler)
    # print(custom_logger.handlers[0].baseFilename)
 
    return custom_logger

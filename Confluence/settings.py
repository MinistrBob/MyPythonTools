from profiles import default_settings, profile_settings
import custom_logger

# Объединение общих настроек и настроек конкретного профайла
settings = {**default_settings, **profile_settings}

class Settings(object):
    """
    Класс настроек приложения.
    Singleton-класс, который позволяет иметь только один экземпляр.
    """
    _instance = None  # Статическая переменная для хранения единственного экземпляра

    def __new__(cls, iterable=(), **kwargs):
        if cls._instance is None:  # Проверка на наличие существующего экземпляра
            cls._instance = super(Settings, cls).__new__(cls)  # Создание экземпляра, если его нет
            cls._instance.__dict__.update(iterable, **kwargs)  # Инициализация экземпляра

            # Инициализация логгера через custom_logger
            cls._instance.log = custom_logger.get_logger(cls._instance)
        return cls._instance  # Возврат единственного экземпляра

    def __str__(self):
        return str(self.__dict__)


def get_settings():
    """
    Процедура возвращает настройки приложения в виде класса.
    :return:
    """
    return Settings(settings)


app_settings = get_settings()
if hasattr(app_settings, 'DEBUG') and app_settings.DEBUG:
    print(f"app_settings: {app_settings}")

if __name__ == '__main__':
    import pprint

    pp = pprint.PrettyPrinter(indent=2)
    print("\n" + "=" * 80 + "\nDefault settings\n" + "=" * 80)
    pp.pprint(default_settings)
    print("\n" + "=" * 80 + f"\nProfile settings\n" + "=" * 80)
    pp.pprint(profile_settings)

    s = Settings(settings)
    print("\n" + "=" * 80 + "\nClass Settings\n" + "=" * 80)
    pp.pprint(s.__dict__)

    appset = get_settings()
    print("\n" + "=" * 80 + "\nApp Settings\n" + "=" * 80)
    pp.pprint(appset)

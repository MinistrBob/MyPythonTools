# Gitlab tools

Набор скриптов на Python для работы с GitLab API: мониторинг версий docker-образов в Container Registry, обход дерева групп/проектов, получение списка участников группы и вспомогательные утилиты (логирование, настройки).

## Программы

| Программа | Назначение |
|---|---|
| **mondi.py** | Мониторинг появления новой версии docker-образа в GitLab Container Registry с автоматическим запуском CI-деплоя при необходимости. |
| **mygitlab.py** | Класс-обёртка `MyGitLab` над GitLab API для работы с проектами, их репозиториями и тегами Container Registry. |
| **gitlab_app.py** | Основной скрипт для взаимодействия с GitLab API через `MyGitLab`: вывод репозиториев и последних тегов проектов. |
| **gitlab_tree.py** | Рекурсивный обход дерева групп и подгрупп GitLab с экспортом списка групп/проектов в CSV. |
| **compare_members.py** | Сведения о членстве пользователя в подгруппах и сравнение членства двух пользователей (поиск недостающих прав). |
| **get_members.py** | Получение списка участников группы GitLab (включая унаследованных) и сохранение в CSV. |
| **SETTINGS_mondi.py** | Конфигурация (профили настроек) для `mondi.py`. Содержит секреты — не должен храниться в git. |
| **custom_logger.py** | Утилита создания логгера с поддержкой логирования в stdout и файл с ротацией. |
| **test.py** | Временный скрипт для отладки/экспериментов. |

---

## mondi.py

Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.  
The script periodically monitors the appearance of a new version of the docker image.  
If a new version is found, an action is taken, such as deploying the application.

Принцип работы: скрипт получает последние теги образов из Container Registry проекта, сравнивает их с образами, запущенными в кластере Kubernetes, и при расхождении запускает CI-деплой по SSH на сервере. Об успехе/ошибке уведомляет через Telegram-бота.

Приложение внутри контейнера с python:3.10 в папке /app. Контейнер запускается с помощью /home/<user>/mondi/mondi_start.sh каждые 30 мин. через cron.

crontab:

```commandline
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ci/.local/bin:/home/ci/bin
MAILTO=""

*/30 * * * * /home/ci/mondi/mondi_start.sh >> /home/ci/mondi/mondi.log 2>&1
50 23 * * * echo cleared > /home/ci/mondi/mondi.log 2>&1

```

В контейнер монтируются папки (для приватных данных):
/home/<user>/mondi:/mondi - SETTINGS_mondi.py
/home/<user>/.ssh:/ssh - отсюда берётся ключ для работы с SSH
/home/<user>/.kube:/kube - отсюда берётся config для работы с kubernetes

Зависимости: python-gitlab, requests, kubernetes, custom_logger, SETTINGS_mondi.

## mygitlab.py

Класс-обёртка `MyGitLab` для работы с GitLab API. Предоставляет методы для работы с проектами GitLab и их Container Registry:

- Получение списка репозиториев проекта.
- Получение списка тегов репозитория (сокращённый и полный с детальной информацией).
- Поиск самого последнего (по дате создания) тега в каждом репозитории проекта.
- Вывод данных в консоль с настраиваемым отступом.
- Отображение прогресс-бара в терминале при длительных операциях.

Конструктор принимает:
- `glo` — объект `gitlab.Gitlab` (авторизованный клиент API).
- `log` — объект логгера для записи отладочной информации.

Зависимости: python-gitlab, dateutil (для `get_max_tags_in_project`).

## gitlab_app.py

Основной скрипт для работы с GitLab API. Подключается к GitLab API (python-gitlab), авторизуется с помощью токена из конфигурации, создаёт экземпляр обёртки `MyGitLab` и выполняет операции над проектами и их репозиториями (Container Registry).

Доступные (закомментированные) операции:
- Получение списка репозиториев (Container Registry) в проекте.
- Получение списка тегов в конкретном репозитории.
- Вывод самых последних (максимальных) тегов в проекте.
- Массовый обход проектов из конфигурации с выводом репозиториев и последних тегов.

Проекты и их ID задаются в конфигурационном модуле `gitlab_app_conf` (`project_dict`).

Использование:
```shell
python gitlab_app.py
```

Зависимости: python-gitlab, common.custom_logger, модуль GitLab (MyGitLab), gitlab_app_conf.

## gitlab_tree.py

Рекурсивный обход дерева групп и проектов GitLab с экспортом результата в CSV.

На вход подаётся URL группы GitLab (например: `https://lab.hub.nspd.rosreestr.gov.ru/nspd`). Скрипт обходит подгруппы и проекты, собирает информацию о каждом узле и сохраняет результат в CSV-файл.

Столбцы CSV:
- `name` — короткое имя (последняя часть URL после `/`).
- `type` — «group» или «project».
- `id` — ID проекта (для групп — ID группы).
- `url` — полный URL до группы или проекта.

Универсальная функция `walk_tree()` может использоваться в других программах — она принимает callback, который вызывается для каждого узла дерева (группы или проекта).

Использование:
```shell
python gitlab_tree.py [url] [output.csv]
# Вообще всё, но там много лишнего
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd gitlab_tree.csv
# Поэтому конкретные группы
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/backend
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/devops
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/docs
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/frontend
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/geoalert
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/smev-client
python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd/studio-tg
```

Зависимости: python-gitlab, gitlab_app_conf.

## compare_members.py

Сведения о членстве пользователя в подгруппах GitLab и сравнение членства двух пользователей. Скрипт обходит дерево подгрупп внутри родительской группы `acl/iteco` (константа `PARENT_GROUP`) и для каждой подгруппы определяет уровень доступа пользователя.

Два режима работы:

- **Один параметр** — выводит все подгруппы, где состоит указанный пользователь, с уровнем доступа в каждой. Удобно, чтобы просто посмотреть текущие права пользователя.
- **Два параметра** — сравнивает целевого пользователя (1-й параметр) с эталонным (2-й параметр) и показывает:
    - где права **совпадают**;
    - где целевой пользователь **состоит, но с другим уровнем**;
    - в каких подгруппах целевому пользователю прав **не хватает** (с указанием нужного уровня доступа) — именно это подсказывает, куда и с какими правами добавить пользователя.

Уровни доступа:
- 10 — Guest, 20 — Reporter, 30 — Developer, 40 — Maintainer, 50 — Owner

Использование:
```shell
# только сведения о пользователе
python compare_members.py luninas
# сравнение: какие права есть у suluyanovev, но нет у luninas
python compare_members.py luninas suluyanovev

```

Зависимости: python-gitlab, gitlab_app_conf, gitlab_tree.walk_tree.

## get_members.py

Получение списка участников группы GitLab. Подключается к GitLab API (python-gitlab), авторизуется с помощью токена из конфигурации, получает полный список участников группы `nspd/iteco` (включая унаследованных через `.members_all`) и выводит их в консоль в табличном виде (ID, Username, Name, Access Level, State).

Результат также сохраняется в CSV-файл `members.csv` с разделителем `;` для совместимости с Excel.

Уровни доступа:
- 10 — Guest, 20 — Reporter, 30 — Developer, 40 — Maintainer, 50 — Owner

Использование:
```shell
python get_members.py
```

Зависимости: python-gitlab, конфигурационный модуль gitlab_app_conf.

## SETTINGS_mondi.py

Модуль настроек (профилей) для `mondi.py`. Позволяет задавать несколько профилей (например, `RT77` — продакшен, `DEV` — разработка) с общими и специфичными настройками.

Профиль и режим отладки задаются через переменные окружения `MONDI_PROFILE` и `MONDI_DEBUG`.

Внимание!!! Файл содержит секретные данные (токены, ключи) и **никогда не должен храниться в репозитории git** — его необходимо сразу добавить в `.gitignore`. Файл копируется между компьютерами вручную. Резервные копии хранятся в защищённом хранилище (например, в архиве с паролем).

Использование:
```python
import SETTINGS_mondi
settings = SETTINGS_mondi.get_settings()
```

## custom_logger.py

Утилита создания логгера (`get_logger`) для приложений. Логирование по умолчанию производится в stdout, при включённой опции — дополнительно в файл в папке `log` рядом со скриптом.

Возможности:
- Выбор уровня логирования (`DEBUG`/`INFO`) из настроек.
- Логирование в stdout и/или файл.
- Ротация лог-файла по дате из первой строки файла.

Использование:
```python
import custom_logger
log = custom_logger.get_logger(settings)
```

## test.py

Временный скрипт для отладки и экспериментов с настройками, логированием, отправкой сообщений в Telegram и выполнением команд. Продукционной ценности не имеет.

---

## FOR DEVELOPER

### Get requirements (on Windows)

```shell
cd C:\MyGit\MyPythonTools\GitLab
py -3.14 -m venv venv
c:\MyGit\MyPythonTools\GitLab\venv\Scripts\activate.bat

pip freeze | Out-File -Encoding UTF8 requirements.txt

```

### Docker build and run

```shell
cd C:\MyGit\MyPythonTools\GitLab
docker build . -t ministrbob/my-python-tools-gitlab:latest
docker login --username XXX --password XXX
docker push ministrbob/my-python-tools-gitlab:latest

docker pull ministrbob/my-python-tools-gitlab:latest
docker run -it --rm ministrbob/my-python-tools-gitlab:latest bash

```

### Links

[python-gitlab v3.1.1](https://python-gitlab.readthedocs.io/en/stable/)
[requests](https://docs.python-requests.org/en/latest/user/quickstart/)
[A Beginner’s Guide to Kubernetes Python Client](https://www.velotio.com/engineering-blog/kubernetes-python-client)
[Kubernetes Python Client](https://github.com/kubernetes-client/python)
[Kubernetes Python Client.README.md](https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md)
[Telegram Bot API](https://core.telegram.org/bots/api)

### Useful

- python-gitlab only supports GitLab API v4.  
- If you use `http_username\http_password` in python-gitlab than I get error: `gitlab.exceptions.GitlabHttpError: 404: 404 Project Not Found`. With token no problem.
- On free version Gitlab only available personal token (not project and group). The token must have all the necessary rights.  

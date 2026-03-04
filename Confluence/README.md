# Подготовка инфраструктуры

Ниже приведены команды, необходимые для подготовки окружения в папке `Confluence`.

```bat
cd /d c:\MyGit\MyPythonTools\Confluence
"c:\Program Files\Python312\python.exe" -m venv .venv
.venv\Scripts\activate

```

# Запуск

## Установка зависимостей

```bat
cd /d c:\MyGit\MyPythonTools\Confluence
.venv\Scripts\activate
python.exe -m pip install --upgrade pip
pip install requests

```

## Запуск скрипта

```shell
cd /d c:\MyGit\MyPythonTools\Confluence
.venv\Scripts\activate

# Запуск с переменными окружения
set APP_PROFILE=dev

python confluence.py
python parser_db.py

```

## Результат

- HTML страницы сохраняется в `out/page_127672967.html`
- Метаданные страницы сохраняются в `out/page_127672967_meta.json`
- Вложения сохраняются в `out/attachments/` без конвертации

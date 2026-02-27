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
set CONFLUENCE_USER=USERNAME
set CONFLUENCE_PASS=PASSWORD
python confluence.py --page-id 127672967 --out out

# Запуск с параметрами логина/пароля
python confluence.py --page-id 127672967 --out out --username USERNAME --password PASSWORD

# Отключение проверки сертификата (если требуется)
python confluence.py --page-id 127672967 --out out --insecure

# Указать CA bundle (PEM/CRT) для корректной проверки TLS
python confluence.py --page-id 127672967 --out out --ca-bundle dmz-DMZ-AD1-CA.crt

# Увеличить таймаут и количество повторов при сетевых сбоях
python confluence.py --page-id 127672967 --out out --timeout 60 --retries 5 --retry-backoff 1.0

```

## Результат

- HTML страницы сохраняется в `out/page_127672967.html`
- Метаданные страницы сохраняются в `out/page_127672967_meta.json`
- Вложения сохраняются в `out/attachments/` без конвертации

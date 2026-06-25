


## Установка python для разработки

### Установка Linux

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
cd /home/bobrovsky/mygit/_ministrbob/birthday-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-optional.txt

$ python3 --version
Python 3.13.5

```

## Использование CLI

```bash
# Список проектов
python weeek.py list-project

# Список задач проекта (ID 12 — пример)
python weeek.py list-tasks 12

# Отчёт: план на сегодня + выполнено вчера (проект ТЕКУЩЕЕ, доска СЕГОДНЯ)
python weeek.py report

# Справка
python weeek.py --help
python weeek.py help
```

### Установка Windows

```bash
cd c:\MyGit\Weeek
"c:\Program Files\Python312\python.exe" -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-optional.txt

```


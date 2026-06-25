import argparse
import io
import sys
from datetime import date, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import requests

WEEKDAYS_RU = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

# Портфолио, задачи которого выводятся сразу после заголовка без названия группы
SCHOOL_PORTFOLIO = "Я ШКОЛА"

# Порядок сортировки по приоритету: Высокий → Средний → Низкий → Hold → None
PRIORITY_WEIGHT = {2: 0, 1: 1, 0: 2, 3: 3}


def _priority_key(priority):
    return PRIORITY_WEIGHT.get(priority, 9)

API_BASE = "https://api.weeek.net/public/v1"
TOKEN = "0af3534c-6212-4044-b76f-e722b61e0234"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json",
}


def list_projects():
    url = f"{API_BASE}/tm/projects"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        msg = f"API вернул ошибку: {data}"
        raise SystemExit(msg)

    projects = data.get("projects", [])
    if not projects:
        print("Проекты не найдены.")
        return

    print(f"Всего проектов: {len(projects)}\n")
    for p in projects:
        # print(f"{p}")
        # pid = p.get("id", "?")
        # name = p.get("name", "(без имени)")
        # status = p.get("status", "?")
        # is_private = p.get("isPrivate", False)
        # color = p.get("color", "")
        print(f"{p['name']} ({p['id']})")
        # print(f"  Название: {name}")
        # print(f"  Статус: {status}")
        # print(f"  Приватный: {'да' if is_private else 'нет'}")
        # if color:
        #     print(f"  Цвет: {color}")
        # team = p.get("team")
        # if team:
        #     print(f"  Участники: {', '.join(team)}")
        print()


def list_tasks(project_id):
    url = f"{API_BASE}/tm/tasks"
    params = {"projectId": project_id}
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        msg = f"API вернул ошибку: {data}"
        raise SystemExit(msg)

    tasks = data.get("tasks", [])
    if not tasks:
        print(f"Задачи для проекта {project_id} не найдены.")
        return

    print(f"Всего задач: {len(tasks)}\n")
    for t in tasks:
        print(t)


def _api_get(path, params=None):
    url = f"{API_BASE}{path}"
    resp = requests.get(url, headers=HEADERS, params=params)
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise SystemExit(f"API вернул ошибку: {data}")
    return data


def _find_project_id(name):
    for p in _get_projects():
        if p.get("name") == name or p.get("title") == name:
            return p["id"]
    raise SystemExit(f"Проект '{name}' не найден")


def _get_projects():
    data = _api_get("/tm/projects")
    return data.get("projects", [])


def _get_portfolios():
    data = _api_get("/tm/portfolios")
    return {p["id"]: p["name"] for p in data.get("data", [])}


def _get_tags():
    data = _api_get("/ws/tags")
    return {t["id"]: (t.get("title") or t.get("name")) for t in data.get("tags", [])}


def _find_board_id(project_id, name):
    data = _api_get("/tm/boards", {"projectId": project_id})
    for b in data.get("boards", []):
        if b.get("name") == name:
            return b["id"]
    raise SystemExit(f"Доска '{name}' не найдена в проекте {project_id}")


def _find_column_ids(board_id, names):
    data = _api_get("/tm/board-columns", {"boardId": board_id})
    result = {}
    for col in data.get("boardColumns", []):
        if col.get("name") in names:
            result[col["name"]] = col["id"]
    return result


def report():
    project_id = _find_project_id("ТЕКУЩЕЕ")
    board_id = _find_board_id(project_id, "СЕГОДНЯ")
    columns = _find_column_ids(board_id, ["В работе", "Готово", "Ожидание"])
    col_in_progress = columns["В работе"]
    col_waiting = columns["Ожидание"]
    col_done = columns["Готово"]

    portfolios = _get_portfolios()
    project_portfolio = {p["id"]: p.get("portfolioId") for p in _get_projects()}
    tags = _get_tags()
    ne_plan_ids = {tid for tid, name in tags.items() if name == "НЕ ПЛАН"}
    important_ids = {tid for tid, name in tags.items() if name == "ВАЖНО"}

    data = _api_get("/tm/tasks", {"projectId": project_id, "perPage": 100})
    tasks = data.get("tasks", [])

    plan = {}
    done = {}
    for t in tasks:
        locations = t.get("locations", [])

        # колонка задачи на доске СЕГОДНЯ проекта ТЕКУЩЕЕ
        col_id = None
        for loc in locations:
            if loc.get("projectId") == project_id and loc.get("boardId") == board_id:
                col_id = loc.get("boardColumnId")
                break
        if col_id not in (col_in_progress, col_waiting, col_done):
            continue

        # проект-источник для портфолио: первый проект из locations, НЕ ТЕКУЩЕЕ
        source_pid = None
        for loc in locations:
            pid = loc.get("projectId")
            if pid is not None and pid != project_id:
                source_pid = pid
                break
        if source_pid is None and t.get("projectId") != project_id:
            source_pid = t.get("projectId")

        portfolio_id = project_portfolio.get(source_pid)
        if portfolio_id:
            pname = portfolios.get(portfolio_id, "Без портфолио")
        else:
            pname = "Без портфолио"

        title = t["title"]
        if col_id == col_waiting:
            title = "⏸" + title
        if important_ids & set(t.get("tags", [])):
            title = "❗️" + title
        if ne_plan_ids & set(t.get("tags", [])):
            title = f"[НЕ ПЛАН] {title}"
        record = (t.get("priority"), title)

        if col_id == col_done:
            done.setdefault(pname, []).append(record)
        else:
            plan.setdefault(pname, []).append(record)

    today = date.today()
    yesterday = today - timedelta(days=1)
    today_str = today.strftime("%d.%m.%Y") + " " + WEEKDAYS_RU[today.weekday()]
    yesterday_str = yesterday.strftime("%d.%m.%Y") + " " + WEEKDAYS_RU[yesterday.weekday()]

    def _print_groups(groups):
        school_records = groups.pop(SCHOOL_PORTFOLIO, [])
        if not school_records and not groups:
            print("—")
            return
        for _prio, title in sorted(school_records, key=lambda r: _priority_key(r[0])):
            print(f"• {title}")
        for pname, records in groups.items():
            print(f"\n📁 {pname}")
            for _prio, title in sorted(records, key=lambda r: _priority_key(r[0])):
                print(f"• {title}")

    print(f"📋 ПЛАН на {today_str}\n")
    _print_groups(plan)

    print()
    print("───────────────")
    print()

    print(f"✅ ВЫПОЛНЕНО {yesterday_str}\n")
    _print_groups(done)


def main():
    parser = argparse.ArgumentParser(description="CLI для Weeek API")
    parser.add_argument(
        "command",
        choices=["list-project", "list-tasks", "report", "help"],
        help="Команда для выполнения",
    )
    parser.add_argument(
        "project_id",
        nargs="?",
        type=int,
        help="ID проекта (для list-tasks)",
    )
    args = parser.parse_args()

    if args.command == "list-project":
        list_projects()
    elif args.command == "list-tasks":
        if args.project_id is None:
            raise SystemExit("Укажите ID проекта: python weeek.py list-tasks <id>")
        list_tasks(args.project_id)
    elif args.command == "report":
        report()
    elif args.command == "help":
        parser.print_help()


if __name__ == "__main__":
    main()
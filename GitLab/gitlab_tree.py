"""
gitlab_tree.py — Обход дерева групп и проектов GitLab с экспортом в CSV.

На вход подаётся URL группы GitLab (например: https://lab.hub.nspd.rosreestr.gov.ru/nspd).
Скрипт рекурсивно обходит дерево подгрупп и проектов, собирает информацию о каждом узле
и сохраняет результат в CSV-файл.

Столбцы CSV:
    name  — короткое имя (последняя часть URL после /).
    type  — «group» или «project».
    id    — ID проекта (для групп — ID группы).
    url   — полный URL до группы или проекта.

Универсальная функция walk_tree() может использоваться в других программах —
она принимает callback, который вызывается для каждого узла дерева (группы или проекта).

Использование:
    python gitlab_tree.py [url] [output.csv]
    python gitlab_tree.py https://lab.hub.nspd.rosreestr.gov.ru/nspd gitlab_tree.csv

Зависимости: python-gitlab, gitlab_app_conf.
"""

import gitlab
import csv
import sys
import logging
import gitlab_app_conf as conf


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)8s| %(message)s'
)
log = logging.getLogger(__name__)


def walk_tree(gl: gitlab.Gitlab, root_path: str, callback):
    """
    Рекурсивно обходит дерево групп и проектов GitLab, начиная с root_path.

    Для каждого узла (группы или проекта) вызывается callback(node_info),
    где node_info — словарь с ключами:
        name      — короткое имя,
        type      — 'group' или 'project',
        id        — ID группы или проекта,
        url       — полный web_url,
        path      — путь внутри GitLab (например 'nspd/iteco').

    Параметры:
        gl         — авторизованный объект gitlab.Gitlab.
        root_path  — путь к корневой группе (например 'nspd' или 'nspd/iteco').
        callback   — функция, вызываемая для каждого узла дерева.
    """
    def _walk_group(group, callback):
        # Обрабатываем саму группу
        callback({
            'name': group.name,
            'type': 'group',
            'id': group.id,
            'url': group.web_url,
            'path': group.full_path,
        })

        # Рекурсивно обходим подгруппы
        try:
            subgroups = group.subgroups.list(all=True)
        except Exception as e:
            log.warning(f"Не удалось получить подгруппы для {group.full_path}: {e}")
            subgroups = []

        for sg in subgroups:
            try:
                full_sg = gl.groups.get(sg.id)
                _walk_group(full_sg, callback)
            except Exception as e:
                log.error(f"Ошибка при обработке подгруппы {sg.full_path}: {e}")

        # Обходим проекты внутри группы
        try:
            projects = group.projects.list(all=True)
        except Exception as e:
            log.warning(f"Не удалось получить проекты для {group.full_path}: {e}")
            projects = []

        for proj in projects:
            callback({
                'name': proj.name,
                'type': 'project',
                'id': proj.id,
                'url': proj.web_url,
                'path': proj.path_with_namespace,
            })

    # Получаем корневую группу по пути
    try:
        root_group = gl.groups.get(root_path)
    except gitlab.exceptions.GitlabGetError as e:
        log.error(f"Группа '{root_path}' не найдена: {e}")
        return

    _walk_group(root_group, callback)


if __name__ == '__main__':
    # URL группы по умолчанию
    default_url = f"{conf.gitlab_url}/nspd"
    default_output = "gitlab_tree.csv"

    input_url = sys.argv[1] if len(sys.argv) > 1 else default_url
    output_file = sys.argv[2] if len(sys.argv) > 2 else default_output

    # Извлекаем путь группы из URL
    # Пример: https://lab.hub.nspd.rosreestr.gov.ru/nspd/iteco -> nspd/iteco
    base_url = conf.gitlab_url.rstrip('/')
    if not input_url.startswith(base_url):
        log.error(f"URL '{input_url}' не соответствует базе '{base_url}'")
        sys.exit(1)

    group_path = input_url[len(base_url):].strip('/')

    log.info(f"Подключение к GitLab: {conf.gitlab_url}")
    gl = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    gl.auth()

    # Открываем CSV сразу и пишем по мере обхода
    csv_file = open(output_file, "w", newline="", encoding="utf-8")
    csv_writer = csv.DictWriter(
        csv_file, fieldnames=["id", "name", "type", "url"], delimiter=";", extrasaction="ignore"
    )
    csv_writer.writeheader()
    csv_file.flush()

    row_count = 0

    def collect(node_info):
        nonlocal row_count
        row_count += 1
        csv_writer.writerow(node_info)
        csv_file.flush()
        log.info(f"  {node_info['type']:7s} | {node_info['id']:<12} | {node_info['path']}")

    log.info(f"Обход дерева групп, начиная с: {group_path}")
    walk_tree(gl, group_path, collect)

    csv_file.close()

    print(f"\nВсего записей: {row_count}")
    print(f"Сохранено в {output_file}")

    log.info("The end!")

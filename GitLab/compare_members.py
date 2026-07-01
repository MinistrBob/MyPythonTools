"""
compare_members.py — Сравнение членства двух пользователей в группах GitLab.

Скрипт обходит дерево подгрупп внутри указанной родительской группы (по умолчанию
«acl/iteco») и для каждой подгруппы показывает уровень доступа обоих пользователей.

Цель: увидеть, в каких подгруппах состоит suluyanovev, в каких из них уже состоит
luninas и с какими правами, и какие подгруппы нужно добавить luninas, чтобы её
права совпали с правами suluyanovev.

Уровни доступа:
    10 — Guest, 20 — Reporter, 30 — Developer, 40 — Maintainer, 50 — Owner

Использование:
    python compare_members.py [suluyanovev] [luninas] [parent_group_path]
    # по умолчанию
    python compare_members.py
    # явно
    python compare_members.py suluyanovev luninas acl/iteco

Зависимости: python-gitlab, gitlab_app_conf, gitlab_tree.walk_tree.
"""

import sys
import logging

import gitlab
import gitlab_app_conf as conf
from gitlab_tree import walk_tree

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)8s| %(message)s'
)
log = logging.getLogger(__name__)

ACCESS_LEVELS = {
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer",
    50: "Owner",
}

DEFAULT_REFERENCE = "suluyanovev"
DEFAULT_TARGET = "luninas"
DEFAULT_PARENT = "acl/iteco"


def get_member_level(gl: gitlab.Gitlab, group_id, username: str):
    """
    Возвращает уровень доступа (int) пользователя username в группе group_id
    (прямое членство), либо None, если пользователь не является прямым участником.
    """
    group = gl.groups.get(group_id)
    members = group.members.list(all=True)
    for member in members:
        if member.username == username:
            return member.access_level
    return None


def level_name(level):
    if level is None:
        return "—"
    return f"{level} ({ACCESS_LEVELS.get(level, '?')})"


if __name__ == '__main__':
    reference_user = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REFERENCE
    target_user = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_TARGET
    parent_path = sys.argv[3] if len(sys.argv) > 3 else DEFAULT_PARENT

    log.info(f"Подключение к GitLab: {conf.gitlab_url}")
    gl = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    gl.auth()

    # Собираем все подгруппы внутри родительской группы
    groups = []

    def collect(node_info):
        if node_info['type'] == 'group':
            groups.append(node_info)

    log.info(f"Обход дерева групп, начиная с: {parent_path}")
    walk_tree(gl, parent_path, collect)
    log.info(f"Найдено групп: {len(groups)}")

    ref_memberships = []   # группы, где есть reference_user
    matching = []          # права совпадают
    differs = []           # luninas есть, но права другие
    missing = []           # luninas отсутствует

    for node in groups:
        ref_level = get_member_level(gl, node['id'], reference_user)
        tgt_level = get_member_level(gl, node['id'], target_user)

        if ref_level is None:
            continue  # reference_user не состоит в этой подгруппе — пропускаем

        ref_memberships.append((node, ref_level, tgt_level))

        if tgt_level is None:
            missing.append((node, ref_level))
        elif tgt_level == ref_level:
            matching.append((node, ref_level))
        else:
            differs.append((node, ref_level, tgt_level))

    # --- Отчёт ---
    print()
    print("=" * 100)
    print(f"Эталонный пользователь : {reference_user}")
    print(f"Целевой пользователь   : {target_user}")
    print(f"Родительская группа    : {parent_path}")
    print("=" * 100)

    print(f"\nВсего подгрупп с {reference_user}: {len(ref_memberships)}\n")

    print("Подгруппы, где права СОВПАДАЮТ:")
    if matching:
        for node, level in matching:
            print(f"  [{level_name(level)}]  {node['path']}")
    else:
        print("  —")

    print("\nПодгруппы, где luninas ЕСТЬ, но права ОТЛИЧАЮТСЯ:")
    if differs:
        for node, ref_level, tgt_level in differs:
            print(f"  {reference_user}={level_name(ref_level)}  {target_user}={level_name(tgt_level)}  ->  {node['path']}")
    else:
        print("  —")

    print(f"\nПодгруппы, где luninas ОТСУТСТВУЕТ (нужно добавить):")
    if missing:
        for node, ref_level in missing:
            print(f"  добавить с уровнем {level_name(ref_level)}  ->  {node['path']}")
    else:
        print("  —")

    print()
    print(f"Итого: совпадают {len(matching)}, отличаются {len(differs)}, отсутствуют {len(missing)}")
    log.info("The end!")

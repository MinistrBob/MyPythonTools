"""
compare_members.py — Сведения и сравнение членства пользователей в группах GitLab.

Скрипт обходит дерево подгрупп внутри родительской группы PARENT_GROUP и для
каждой подгруппы показывает уровень доступа пользователя(ей).

Режимы работы:
    - Один параметр:  выводит все подгруппы, где состоит указанный пользователь,
      с уровнем доступа в каждой.
    - Два параметра:   сравнивает членство целевого пользователя (1-й параметр)
      с эталонным (2-й параметр). Показывает, где права совпадают, где отличаются
      и в каких подгруппах целевому пользователю их не хватает.

Уровни доступа:
    10 — Guest, 20 — Reporter, 30 — Developer, 40 — Maintainer, 50 — Owner

Использование:
    python compare_members.py luninas
    python compare_members.py luninas suluyanovev

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

PARENT_GROUP = "acl/iteco"

ACCESS_LEVELS = {
    10: "Guest",
    20: "Reporter",
    30: "Developer",
    40: "Maintainer",
    50: "Owner",
}


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


def collect_groups(gl: gitlab.Gitlab):
    """Собирает все подгруппы внутри PARENT_GROUP."""
    groups = []

    def collect(node_info):
        if node_info['type'] == 'group':
            groups.append(node_info)

    log.info(f"Обход дерева групп, начиная с: {PARENT_GROUP}")
    walk_tree(gl, PARENT_GROUP, collect)
    log.info(f"Найдено групп: {len(groups)}")
    return groups


def report_single(gl: gitlab.Gitlab, groups, target_user):
    """Вывод всех подгрупп, где состоит target_user, с уровнем доступа."""
    print()
    print("=" * 100)
    print(f"Пользователь: {target_user}")
    print(f"Родительская группа: {PARENT_GROUP}")
    print("=" * 100)

    memberships = []
    for node in groups:
        level = get_member_level(gl, node['id'], target_user)
        if level is not None:
            memberships.append((node, level))

    if memberships:
        print(f"\nПодгруппы, где состоит {target_user}:")
        for node, level in memberships:
            print(f"  [{level_name(level)}]  {node['path']}")
    else:
        print(f"\n{target_user} не состоит ни в одной подгруппе (прямое членство).")

    print(f"\nИтого подгрупп: {len(memberships)}")


def report_compare(gl: gitlab.Gitlab, groups, target_user, reference_user):
    """Сравнение членства target_user с reference_user."""
    matching = []   # права совпадают
    differs = []    # target есть, но права другие
    missing = []    # target отсутствует

    for node in groups:
        ref_level = get_member_level(gl, node['id'], reference_user)
        tgt_level = get_member_level(gl, node['id'], target_user)

        if ref_level is None:
            continue  # reference_user не состоит в этой подгруппе — пропускаем

        if tgt_level is None:
            missing.append((node, ref_level))
        elif tgt_level == ref_level:
            matching.append((node, ref_level))
        else:
            differs.append((node, ref_level, tgt_level))

    # --- Отчёт ---
    print()
    print("=" * 100)
    print(f"Целевой пользователь   : {target_user}")
    print(f"Эталонный пользователь : {reference_user}")
    print(f"Родительская группа    : {PARENT_GROUP}")
    print("=" * 100)

    print(f"\nПодгруппы, где права СОВПАДАЮТ:")
    if matching:
        for node, level in matching:
            print(f"  [{level_name(level)}]  {node['path']}")
    else:
        print("  —")

    print(f"\nПодгруппы, где {target_user} ЕСТЬ, но права ОТЛИЧАЮТСЯ:")
    if differs:
        for node, ref_level, tgt_level in differs:
            print(f"  {reference_user}={level_name(ref_level)}  {target_user}={level_name(tgt_level)}  ->  {node['path']}")
    else:
        print("  —")

    print(f"\nПодгруппы, где {target_user} ОТСУТСТВУЕТ (нужно добавить):")
    if missing:
        for node, ref_level in missing:
            print(f"  добавить с уровнем {level_name(ref_level)}  ->  {node['path']}")
    else:
        print("  —")

    print()
    print(f"Итого: совпадают {len(matching)}, отличаются {len(differs)}, отсутствуют {len(missing)}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python compare_members.py <пользователь> [<эталонный_пользователь>]")
        print("Пример:")
        print("  python compare_members.py luninas")
        print("  python compare_members.py luninas suluyanovev")
        sys.exit(1)

    target_user = sys.argv[1]
    reference_user = sys.argv[2] if len(sys.argv) > 2 else None

    log.info(f"Подключение к GitLab: {conf.gitlab_url}")
    gl = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    gl.auth()

    groups = collect_groups(gl)

    if reference_user:
        report_compare(gl, groups, target_user, reference_user)
    else:
        report_single(gl, groups, target_user)

    log.info("The end!")

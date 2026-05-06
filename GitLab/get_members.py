"""
get_members.py — Получение списка участников группы GitLab.

Подключается к GitLab API (python-gitlab), авторизуется с помощью токена из конфигурации,
получает полный список участников группы «nspd/iteco» (включая унаследованных через .members_all),
и выводит их в консоль в табличном виде (ID, Username, Name, Access Level, State).
Результат также сохраняется в CSV-файл «members.csv» с разделителем «;» для совместимости с Excel.

Уровни доступа:
    10 — Guest, 20 — Reporter, 30 — Developer, 40 — Maintainer, 50 — Owner

Зависимости: python-gitlab, конфигурационный модуль gitlab_app_conf.
"""

import gitlab
import logging
import os
import csv
import gitlab_app_conf as conf

# Простой логгер без custom_logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s|%(levelname)8s| %(message)s'
)
log = logging.getLogger(__name__)

if __name__ == '__main__':
    the_gitlab_obj = gitlab.Gitlab(conf.gitlab_url, private_token=conf.private_token, timeout=30)
    the_gitlab_obj.auth()

    group = the_gitlab_obj.groups.get("nspd/iteco")

    members = group.members_all.list(all=True)

    access_levels = {
        10: "Guest",
        20: "Reporter",
        30: "Developer",
        40: "Maintainer",
        50: "Owner",
    }

    print(f"{'ID':<10}\t{'Username':<30}\t{'Name':<40}\t{'Access Level':<20}\t{'State':<10}")
    # print("-" * 110)

    for member in members:
        level_name = access_levels.get(member.access_level, str(member.access_level))
        print(f"{member.id:<10}\t{member.username:<30}\t{member.name:<40}\t{level_name:<20}\t{member.state:<10}")

    print(f"\nВсего участников: {len(members)}")

    output_file = "members.csv"
    with open(output_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, delimiter=";")  # точка с запятой для совместимости
        writer.writerow(["ID", "Username", "Name", "Access Level", "State"])
        for member in members:
            level_name = access_levels.get(member.access_level, str(member.access_level))
            writer.writerow([member.id, member.username, member.name, level_name, member.state])

    print(f"Сохранено в {output_file}")

    log.info("The end!")

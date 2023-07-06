"""
Получение списка контактов группы VK
"""
import vk
import SETTINGS


def main(app_set):
    api = vk.API(v='5.131',
                 access_token=app_set.vk_access_token)
    # api.users.get(user_ids=1)
    # print(api.users.get(user_ids=1))
    list1 = api.groups.getMembers(group_id='meditation_lessons_sochi', v='5.131')  # Получить список участников группы
    # print(list1)
    for i in list1['items']:
        user = api.users.get(user_ids=i, v='5.131', fields='last_name,first_name,country,city,domain')
        # print(user[0])
        if 'country' in user[0]:
            country = user[0]['country']['title']
        else:
            country = 'нет'
        if 'city' in user[0]:
            city = user[0]['city']['title']
        else:
            city = 'нет'
        first_name = user[0].get('first_name', 'нет')
        if first_name not in ("DELETED", "Заблокированный пользователь"):
            print(f"{user[0].get('last_name', 'нет')}\t{first_name}\t{country}\t{city}\t{user[0].get('domain', 'нет')}")


if __name__ == '__main__':
    # Настройки программы
    settings = SETTINGS.get_settings()
    if settings.DEBUG:
        print(f"settings={settings}")
    main(settings)

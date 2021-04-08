def stub():
    pass


def mongo1(base_path):
    """
    Генерация команд для импорта множества коллекций в mongo
    :return:
    """
    txt_file = open('text2.txt', 'r')
    lines = txt_file.readlines()
    for line in lines:
        # print(line, end='')
        if line.endswith(".json\n"):
            print(
                f"mongoimport --authenticationDatabase admin --username root --password P@ssw0rds --drop --db objects --collection obj_{line.split('.')[0]}_history {base_path}/{line}",
                end='')


if __name__ == '__main__':
    stub()
    mongo1('/bitnami/mongodb/data/export-folder')

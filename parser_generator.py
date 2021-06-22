def stub():
    pass


def mongo1(base_path, drop=True):
    """
    Генерация команд для импорта множества коллекций в mongo
    :return:
    """
    txt_file = open('text2.txt', 'r')
    lines = txt_file.readlines()
    if drop:
        drop_sub = " --drop "
    else:
        drop_sub = " "
    for line in lines:
        # print(line, end='')
        if line.endswith(".json\n"):
            print(f"mongoimport --authenticationDatabase admin --username root --password P@ssw0rds{drop_sub}--db "
                  f"objects --collection obj_{line.split('.')[0]}_history {base_path}/{line}", end='')


def copy_picture():
    """
    Генерация команд для копирования картинок
    :return:
    """
    txt_file = open('text3.txt', 'r')
    # lines = txt_file.readlines()
    lines = txt_file.read().splitlines()
    for line in lines:
        # print(line, end='')
        line = line.split('/')
        print(f"xcopy h:\\RT\\uf\\{line[2]}\\{line[3]} \\\\172.26.12.60\\upload\\uf\\{line[2]}\\{line[3]}\n", end='')


if __name__ == '__main__':
    stub()
    # mongo1('/bitnami/mongodb/data/import-folder')
    # copy_picture()

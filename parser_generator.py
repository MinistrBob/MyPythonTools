def stub():
    pass


def mongo1(base_path, drop=True, mode=False):
    """
    Генерация команд для импорта множества коллекций в mongo
    --mode=<insert|upsert|merge|delete>
    :return:
    """
    txt_file = open('text2.txt', 'r')
    lines = txt_file.readlines()

    if drop:
        drop_sub = " --drop "
    else:
        drop_sub = " "

    if mode:
        if mode == "insert":
            mode_sub = " --mode=insert "
        elif mode == "upsert":
            mode_sub = " --mode=upsert "
        elif mode == "merge":
            mode_sub = " --mode=merge "
        elif mode == "delete":
            mode_sub = " --mode=delete "
        else:
            raise Exception('Не правильно определён --mode')
    else:
        mode_sub = " "

    for line in lines:
        # print(line, end='')
        if line.endswith(".json\n"):
            line = line.rstrip()
            print(f"echo -e \"\\nImport {line}\" && "
                  f"mongoimport --authenticationDatabase admin --username root --password P@ssw0rds{drop_sub}{mode_sub}"
                  f" --db objects --collection obj_{line.split('.')[0]}_history {base_path}/{line} "
                  f"2>&1 | tee {base_path}/{line}.import.log\n", end='')


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


def get_images_for_prod():
    """
    Генерация команд для закачки docker images для prod
    k get deploy -l app.kubernetes.io/component=services | awk '{print $1}' | sort | xargs kubectl describe deploy | grep Image:
    :return:
    """
    txt_file = open('text4.txt', 'r')
    # lines = txt_file.readlines()
    lines = txt_file.read().splitlines()
    print("#!/bin/env bash")
    for line in lines:
        image_name = line.split('/')[-1]
        print(f"docker pull {line}\n", end='')
        print(f"docker tag {line} localhost:5000/{image_name}\n", end='')
        print(f"docker push localhost:5000/{image_name}\n", end='')
        print("\n", end='')


if __name__ == '__main__':
    stub()
    # --mode = < False | insert | upsert | merge | delete > #
    mongo1('/bitnami/mongodb/data/import-folder', drop=False, mode='merge')
    # copy_picture()
    # get_images_for_prod()

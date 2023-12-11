import os
import time
import ast  # Used to safely parse the tags string
import re
import shutil
from urllib.parse import unquote
from typing import List, Optional


def replace_strings_in_file(file_path):
    """
    Находит в файле все внешние ссылки r"![" и заменяет в таких строках "_resources" на "attachments",
    а ".resources" удаляет.
    :param file_path: Путь к файлу.
    """
    # Read the file, replace strings, and write the modified content back
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = [line.replace("_resources", "attachments").replace(".resources", "")
                 if r"![" in line else line for line in file]

    with open(file_path, 'w', encoding='utf-8') as file:
        file.writelines(lines)


def replace_content_in_parentheses(input_string, replacement):
    """
    (вспомогательное) Заменяет содержимое внешних ссылок в строке на replacement.
    :param input_string:
    :param replacement:
    :return:
    """
    # Define a regular expression pattern to match content within parentheses
    pattern = r'\((.*?)\)'

    # Use re.sub to replace the content within parentheses
    result_string = re.sub(pattern, f'({replacement})', input_string)

    return result_string


def check_link(input_string: str) -> bool:
    """
    Внешняя ссылка на attachment должна начинаться с ./_resources
    :param input_string: Проверяемая строка.
    :return: boolean
    """
    if input_string.startswith(r"./_resources"):
        return True
    else:
        return False


def get_path_from_link(input_string: str, pattern=r'!\[.*?\]\((.*?)\)') -> str:
    """
    С помощью регулярного выражения возвращаю путь к файлу attachment.
    :param input_string:
    :param pattern:
    :return:
    """
    # Use re.search to find the first match
    match = re.search(pattern, input_string)
    # If a match is found, return the content within parentheses, else return None
    return match.group(1) if match else None


def calculate_execution_time(func):
    """
    (вспомогательное) Decorator to calculate the execution time of a function.
    :param func: The function to be decorated.
    :return: The decorated function.
    """

    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = round(end_time - start_time, 3)
        # print(f"Execution time: {execution_time} seconds")
        return execution_time, result

    return wrapper


@calculate_execution_time
def count_md_files(folder_path) -> int:
    """
    (вспомогательное) Обход файлового дерева начиная с folder_path и подсчет количества *.md файлов.
    :param folder_path: The path to the folder to start traversing from.
    :return: The count of *.md files.
    """
    md_file_count = 0
    # Walk through the directory tree
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            # Check if the file has a .md extension
            if filename.endswith(".md"):
                md_file_count += 1
    return md_file_count


def find_long_filepath(folder_path):
    """
    (вспомогательное) Поиск путей файлов которые длиннее 256 символов.
    """
    # Walk through the directory tree
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            file_path = os.path.join(foldername, filename)
            if len(file_path) > 256:
                print(file_path)


def process_md_files(folder_path, func):
    """
    (вспомогательное) Обход файлового дерева начиная с folder_path и обработка каждого *.md файла.
    В данном случае печать списка тегов для файла.
    file_path: d:\YandexDisk\ObsidianVault\MainVault\@ ХРАНИЛИЩЕ\! Включение серверов по iLO SSH.md
    relative_path: ! Включение серверов по iLO SSH.md
    :param func:
    :param folder_path: The path to the folder to start traversing from.
    """
    # Walk through the directory tree
    for foldername, subfolders, filenames in os.walk(folder_path):
        for filename in filenames:
            # Check if the file has a .md extension
            if filename.endswith(".md"):
                file_path = os.path.join(foldername, filename)
                relative_path = os.path.relpath(file_path, folder_path)
                # print(f"file_path: {file_path}")
                # print(f"relative_path: {relative_path}")
                func(file_path, relative_path)


def work_with_links_in_md_files(file_path, relative_path):
    """
    Вывести список ссылок "![" из md файла.
    :param file_path:
    :param relative_path:
    :return:
    """
    links = []
    with open(file_path, 'r', encoding='utf-8') as md_file:
        for line in md_file:
            if r"![" in line:
                links.append(line)
    if links:
        # print(f"File: {relative_path}")
        report = []
        for link in links:
            # print(f"  {link}")
            link_parts = link.split("/")
            try:
                index_of_resources = link_parts.index("_resources")
            except ValueError:
                report.append(f"NO RESOURCES: link={link}")
                continue
            attach_dir = link_parts[index_of_resources + 1]
            attach_file = link_parts[index_of_resources + 2]
            if ")]" in attach_file:
                continue
            if "(" in attach_dir or ")" in attach_dir or "(" in attach_file or ")" in attach_file:
                report.append(f"link={link}")
        if report:
            print(f"File: {relative_path}")
            for i in report:
                print(f"  {i}")


def get_tags_from_md(file_path, relative_path):
    """
    (вспомогательное) Находит в файле md теги и печатает их. Или выводит сообщение об отсутствии тегов.
    :param file_path:
    :param relative_path:
    :return:
    """
    tags_list = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if line.startswith("tags:"):
                # Extract the tags using ast.literal_eval to safely parse the string
                tags_str = line.replace("tags:", "").strip()
                try:
                    tags_list = ast.literal_eval(tags_str)
                except (SyntaxError, ValueError):
                    print(f"    Error parsing tags in file: {relative_path}")
                break
        if not tags_list:
            # Print relative path
            print(f"File: {relative_path}")
            print(f"    No tags found in file: {relative_path}")
        else:
            # Print relative path
            # print(f"File: {relative_path}")
            # Print the list of tags
            # print(f"    Tags: {tags_list}")
            pass


def create_tag_folders(tags, destination_path):
    """
    Создать папки, соответствующие тегам, если они не существуют в пути назначения.

    :param tags: List of tags.
    :param destination_path: Path to the destination folder.
    """
    # Ensure the destination path exists
    if not os.path.exists(destination_path):
        raise ValueError(f"Destination path '{destination_path}' does not exist.")
        exit(1)

    for tag in tags:
        # Remove the '#' symbol if present at the beginning
        if tag.startswith('#'):
            folder_name = tag.lstrip('#')
        else:
            folder_name = tag

        # Create the full path for the folder
        folder_path = os.path.join(destination_path, folder_name)

        # Check if the folder already exists
        if not os.path.exists(folder_path):
            # If not, create the folder
            os.makedirs(folder_path)
            print(f"Folder created: {folder_path}")
        # else:
        #     print(f"Folder already exists: {folder_path}")


def delete_attach_folder(source_dir, dest_dir):
    # Check if source_dir exists
    if os.path.exists(source_dir) and os.path.isdir(source_dir):
        # Check if source_dir has any files
        files_in_source_dir = os.listdir(source_dir)

        if files_in_source_dir:
            # source_dir has files, so copy them to folder2
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
            for file in files_in_source_dir:
                file_path = os.path.join(source_dir, file)
                shutil.move(file_path, dest_dir)

            # Delete source_dir
            os.rmdir(source_dir)
            print(f"Files from {source_dir} moved to {dest_dir}, and {source_dir} deleted.")
        else:
            # source_dir is empty, so just delete it
            os.rmdir(source_dir)
            print(f"{source_dir} is empty and has been deleted.")
    else:
        print(f"{source_dir} does not exist or is not a directory.")


def remove_parentheses(data_path, dry=True):
    for foldername, subfolders, filenames in os.walk(data_path):
        for filename in filenames:
            if filename.endswith('.md') and ('(' in filename or ')' in filename):
                print(f"Filename: {filename}")
                # Task 1: Имя файла, где все проблемы заменяются на _
                md_name_without_spaces = filename.replace(' ', '_')
                template_name = md_name_without_spaces.rstrip('.md')
                print(f"  md_name_without_spaces ={md_name_without_spaces}")
                print(f"  template_name={template_name}")

                # Task 2: Find and rename the corresponding folder
                resources_folder_path = os.path.join(data_path, '_resources', f"{template_name}.resources")
                print(f"  Find dir: {resources_folder_path}")
                new_resources_folder_path = resources_folder_path.replace('(', '').replace(')', '')
                print(f"  new_resources_folder_path={new_resources_folder_path}")
                if os.path.exists(resources_folder_path):

                    print(f"  Rename dir: {resources_folder_path} to {new_resources_folder_path}")
                    if not dry:
                        os.rename(resources_folder_path, new_resources_folder_path)

                # Task 3: Open and modify the contents of the md file
                md_file = os.path.join(foldername, filename)
                print(f"  Replace content: {md_file}")
                if not dry:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        md_content = f.read()
                        modified_content = md_content.replace(template_name,
                                                              template_name.replace('(', '').replace(')', ''))

                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(modified_content)

                # Task 4: Rename the md file itself
                new_md_file = os.path.join(foldername, filename.replace('(', '').replace(')', ''))
                print(f"  Rename md: {md_file} to {new_md_file}")
                if not dry:
                    os.rename(md_file, new_md_file)


def move_md_files(data_path: str, tags: List[str], destination_path: str, dry: bool = True, special_folder: str = None):
    """
    Перенос *.md файлов с заданными тегами. В папке destination_path создаются подпапки с тегами.

    :param special_folder: Если указано, то заметки переносятся в подпапку special_folder.
    :type special_folder: List[str]
    :param dry: Dry run, если True то реальные действия с файлами не производятся.
    :param destination_path: Папка где будет создаваться подпапка тега в которую будут перенесены *.md файлы.
    :param tags: Список тегов, *.md файлы которых будут перенесены.
    :param data_path: Путь к исходной папке где сейчас лежать *.md файлы.
    """
    count = 0
    # Создать папки соответствующие тегам в destination_path если их нет.
    if not dry:
        if special_folder:
            create_tag_folders([special_folder], destination_path)
        else:
            create_tag_folders(tags, destination_path)
    # Walk through the directory tree
    for foldername, subfolders, filenames in os.walk(data_path):
        for filename in filenames:
            # Check if the file has a .md extension
            if filename.endswith(".md"):
                file_path = os.path.join(foldername, filename)
                # print(file_path)
                relative_path = os.path.relpath(file_path, data_path)

                # Ищем в файле теги
                tags_list = []
                with open(file_path, 'r', encoding='utf-8') as file:
                    for line in file:
                        if line.startswith("tags:"):
                            # Extract the tags using ast.literal_eval to safely parse the string
                            tags_str = line.replace("tags:", "").strip()
                            try:
                                tags_list = ast.literal_eval(tags_str)
                            except (SyntaxError, ValueError):
                                print(f"    Error parsing tags in file: {relative_path}")
                            break
                # Работаем только с файлами с тегами, остальные потом обработаю.
                if tags_list:
                    # Есть ли какой-нибудь из тегов входящего списка (tags) в списке тегов документа (tags_list).
                    # Берём первый попавшийся.
                    first_matching_tag = next((item for item in tags if item in tags_list), None)
                    if first_matching_tag is not None:
                        # Файл соответствует списку тегов tags
                        print(f"Tag: {first_matching_tag} in file: {file_path}")
                        # Собираем все ссылки из документа
                        links = []
                        with open(file_path, 'r', encoding='utf-8') as md_file:
                            for line in md_file:
                                if r"![" in line:
                                    print(f"link line: {line}")
                                    # Получаем ссылку и проверяем ее на корректность, если она корректна то добавляем в список,
                                    # если нет, пробуем другие варианты pattern.
                                    # Вариант ссылки в круглых скобках:
                                    # [![](./_resources/Глобальные_платформы_для_Фрилансеров_-The_Most_Popular_Platforms.1.resources/unknown_filename.png)](https://blog.payoneer.com/ru/author/richardcl/)
                                    res = get_path_from_link(line, pattern=r'!\[.*?\]\((.*?)\)')
                                    print(f"    res1: {res}")
                                    if res and check_link(res):
                                        links.append(res)
                                    else:
                                        # Вариант ссылки в квадратных скобках:
                                        # [![[./_resources/Совместная_работа_с_документами_SharePoint_2016,_Office_Online_и_все-все-все._Часть_1._Что_это__Хабр.resources/embedded.83.svg]]](https://habr.com/ru/post/310396/#comment_9817182)
                                        res = get_path_from_link(line, pattern=r'!\[\[\s*(.*?)\s*\]\]')
                                        print(f"    res2: {res}")
                                        if res and check_link(res):
                                            links.append(res)
                                        else:
                                            raise ValueError(f"Ни один из паттернов не подошёл, нужно искать другие")
                                    print("-" * 60)
                            print(f"    Links: {links}")
                            for link in links:
                                print(link)
                            print("-" * 60)
                        # Если у документа нет ссылок тогда мы его просто переносим в папку destination_path/tag
                        # иначе переносим ещё и связанные с документом вложения.
                        # Удалить символ # из имени тега и символы - заменить на пробелы.
                        if first_matching_tag.startswith('#'):
                            first_matching_tag = first_matching_tag.lstrip('#').replace('-', ' ')
                        # Целевая папка тега.
                        if special_folder:
                            dest_tag_dir = os.path.join(destination_path, special_folder)
                        else:
                            dest_tag_dir = os.path.join(destination_path, first_matching_tag)
                        if not links:
                            # Перемещение заметки
                            print(f"    Moving file: {file_path} to {dest_tag_dir}")
                            if not dry:
                                shutil.move(file_path, dest_tag_dir)
                        else:
                            print("Create attachments folder: " + dest_tag_dir)
                            if not dry:
                                create_tag_folders(["attachments"], dest_tag_dir)
                            # Перемещение вложений
                            for link in links:
                                # Выделить из ссылки имя папки и имя файла
                                link = link.split("/")
                                print(f"Link parts: {link}")
                                # Так будет называться папка вложений на новом месте
                                dest_attach_dir_name = link[-2].replace(".resources", "")
                                # Имя файла вложения. В некоторых ссылках имена файлов идут как URL-encoded string,
                                # поэтом производиться декодирование имени файла.
                                dest_attach_file_name = unquote(link[-1], encoding='utf-8')
                                print(f"dest_attach_dir_name={dest_attach_dir_name}")
                                print(f"dest_attach_file_name={dest_attach_file_name}")
                                # Создать папку для вложений конкретной заметки в папке destination_path/tag/attachments
                                if not dry:
                                    print("Create note attache folder: " + dest_tag_dir)
                                    create_tag_folders([dest_attach_dir_name],
                                                       os.path.join(dest_tag_dir, "attachments"))
                                # Перенести вложение в папку destination_path/tag/attachments/folder_name
                                ## Исходный путь к файлу вложения (dest_attach_file_name сюда подходит,
                                # потому что исходное и целевое имя файла одно и тоже).
                                source_attach_file = os.path.join(data_path, "_resources", link[-2],
                                                                  dest_attach_file_name)
                                ## Целевой путь к целевой папке вложений и файлу вложения.
                                dest_attach_dir = os.path.join(dest_tag_dir, "attachments", dest_attach_dir_name)
                                dest_attach_file = os.path.join(dest_attach_dir, dest_attach_file_name)
                                print(f"source_attach_file={source_attach_file}")
                                print(f"dest_attach_dir={dest_attach_dir}")
                                print(f"dest_attach_file={dest_attach_file}")
                                print(f"    Moving attach: {source_attach_file} to {dest_attach_file}")
                                if not dry:
                                    try:
                                        shutil.move(source_attach_file, dest_attach_file)
                                    except FileNotFoundError:
                                        print(f"File not found: {source_attach_file}")
                                # Копировать оставшиеся вложения в папку destination_path/tag/attachments/folder_name
                                # и удалять папку.
                                if not dry:
                                    source_attach_dir = os.path.join(data_path, "_resources", link[-2])
                                    print(f"source_attach_dir={source_attach_dir}")
                                    delete_attach_folder(source_attach_dir, dest_attach_dir)
                            # Перемещение заметки
                            if not dry:
                                replace_strings_in_file(file_path)
                            print(f"    Moving file: {file_path} to {dest_tag_dir}")
                            if not dry:
                                shutil.move(file_path, dest_tag_dir)
                        count+=1
                        print(f"\n{'=' * 60}\n")
    print(f"\nВсего обработано: {count} заметок.")


if __name__ == '__main__':
    DATA_PATH = r"d:\YandexDisk\ObsidianVault\MainVault\@ ХРАНИЛИЩЕ"

    # execution_time, result= count_md_files(DATA_PATH)
    # print(f"({execution_time} sec.) Number of *.md files: {result}")  # Number of *.md files: 7572

    # (в текущем примере) выводит файлы md не имеющих тегов.
    # process_md_files(DATA_PATH, get_tags_from_md)

    # (в текущем примере) выводит список ссылок "![" из md файла.
    # process_md_files(DATA_PATH, work_with_links_in_md_files)

    # find_long_filepath(DATA_PATH)

    # path1 = get_path_from_link("![wqerewr](https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png)")
    # print(path1)

    # encoded_string = "Инструкция%20по%20работе%20в%20среде%20MacOS.pdf"
    # decoded_string = unquote(encoded_string, encoding='utf-8')
    # print(decoded_string)

    # test_path = os.path.join(DATA_PATH,
    #                          r"./_resources/О_готовности_программного_токена.resources/Инструкция%20по%20работе%20в%20среде%20MacOS.pdf".lstrip(
    #                              r'./'))
    # print(test_path)

    # Убрать все скобки из названий файлов и из ссылок в md файлах.
    # remove_parentheses(DATA_PATH, dry=True)
    # remove_parentheses(DATA_PATH, dry=False)

    destination_path = r"d:\YandexDisk\ObsidianVault\MainVault\ДЕНЕЖНЫЙ ПОТОК"
    # move_md_files(DATA_PATH, ["#@@@-ИЗУЧЕНИЕ"], destination_path)
    move_md_files(DATA_PATH, ["#Криптовалюта"], destination_path, dry=False)

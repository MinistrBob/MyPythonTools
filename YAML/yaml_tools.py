import os
import yaml

keys_to_remove = ['metadata.resourceVersion', 'metadata.uid', 'metadata.annotations',
                  'metadata.creationTimestamp', 'metadata.selfLink']


def sort_nodes_in_one_yaml_file(file_path):
    print(f"Process file {file_path}")
    with open(file_path, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except Exception:
            print(f"ERROR: can't READ the file")
            return
    try:
        sorted_data = yaml.dump(data, sort_keys=True)
    except Exception:
        print(f"ERROR: can't sort yaml data")
        return

    with open(file_path, 'w') as f:
        f.write(sorted_data)
    print(f"File processing was successful")


def sort_nodes_for_yaml_files_in_directory(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                file_path = os.path.join(root, file)
                sort_nodes_in_one_yaml_file(file_path)


def split_yaml_documents(file_path):
    """
    Берёт один yaml файл в котором содержатся множество других yaml документов разделённых ---
    и разделяет их на отдельные документы, помещая в список.
    :param file_path: Путь к исходному yaml файлу.
    :return: Список yaml документов.
    """
    with open(file_path, 'r') as file:
        yaml_documents = file.read().split('---')

    parsed_documents = []
    for document in yaml_documents:
        # Skip empty lines
        if document.strip() == '':
            continue

        # Parse each YAML document
        parsed_document = yaml.safe_load(document)
        parsed_documents.append(parsed_document)

    directory_path, file_name = split_path_without_extension(file_path)

    create_folder(directory_path)

    for doc in parsed_documents:
        # Extract metadata.name from the document
        file_name = doc.get('metadata', {}).get('name')
        if not file_name:
            print("Error: 'metadata.name' not found in the document.")
            continue

        # Write the document to a YAML file
        file_path = f"{os.path.join(directory_path, file_name)}.yaml"
        with open(file_path, 'w') as file:
            yaml.dump(doc, file)


def split_path_without_extension(full_path):
    """
    Принимает полный путь к файлу. Возвращает полный путь до папки и имя файла без расширения.
    :param full_path:
    :return:
    """
    directory_path, file_name_with_extension = os.path.split(full_path)
    file_name, _ = os.path.splitext(file_name_with_extension)
    return directory_path, file_name


def create_folder(folder_path):
    try:
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created successfully.")
    except FileExistsError:
        pass
        # print(f"Folder '{folder_path}' already exists.")


def remove_keys_from_yaml(yaml_data, keys_to_remove):
    for key in keys_to_remove:
        if key in yaml_data:
            del yaml_data[key]


if __name__ == '__main__':
    # Сортировка узлов для всех yaml файлов в папке c:\!SAVE\DITMoscow\compare\work-compare\
    work_directory = r'c:\!SAVE\DITMoscow\compare\work-compare'
    sort_nodes_for_yaml_files_in_directory(work_directory)

    # Сортировка узлов конкретного yaml файла
    # file_path = r'c:\!SAVE\DITMoscow\compare\helm-charts-backup\asuno-backend\templates\deployment.yaml'
    # sort_nodes_in_yaml_file(file_path)

    # Example usage
    # file_path = r'c:\!SAVE\DITMoscow\compare\asuno-backend.yaml'
    # split_yaml_documents(file_path)

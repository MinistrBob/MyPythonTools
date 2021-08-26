#!/usr/bin/env python3
import json


def stub():
    pass


def count_documents(path):
    with open(path, encoding='utf-8') as json_file:
        data = json.load(json_file)
        print(data)


if __name__ == '__main__':
    stub()
    # count_documents(r'<file_path>')

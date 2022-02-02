"""
Parsing Dockerfile-s and Nodejs files for to get dependencies.
"""
import sys
import os
import argparse

parser = argparse.ArgumentParser(description='Parsing Dockerfile-s and Nodejs files for to get dependencies.')
parser.add_argument('directory', type=str, help='Path to src')
args = parser.parse_args()


def scantree(path):
    """Recursively yield DirEntry objects for given directory."""
    for entry in os.scandir(path):
        if entry.is_dir(follow_symlinks=False):
            yield from scantree(entry.path)  # see below for Python 2.x
        else:
            yield entry


# Выбираем только уникальные значения
docker_images = set()
run_commands = set()

for entry in scantree(args.directory):
    if entry.name.startswith('Dockerfile'):
        # print(f"{'-' * 80}\nDockerfile {entry.path}\n{'-' * 80}")
        with open(entry.path, encoding='utf8') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('FROM'):
                    if line.startswith(('FROM build', 'FROM base'), ):
                        continue
                    # print(line)
                    # print(line.rstrip('\n').split(' '))
                    docker_images.add(line.rstrip('\n').split(' ')[1])
                if line.startswith('RUN'):
                    if line.startswith('RUN dotnet'):
                        continue
                    # print(line.rstrip('\n'))
                    run_commands.add(line.rstrip('\n'))

print(f"{'-' * 80}\nLIST DOCKER IMAGES\n{'-' * 80}")
for di in docker_images:
    print(di)

print(f"{'-' * 80}\nRUN COMMANDS\n{'-' * 80}")
for rc in run_commands:
    print(rc)

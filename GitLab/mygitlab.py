class MyGitLab:

    def __init__(self, glo: object, log: object):
        self.glo = glo
        self.log = log

    # Print iterations progress
    def printProgressBar(self, iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
        """
        Call in a loop to create terminal progress bar
        @params:
            iteration   - Required  : current iteration (Int)
            total       - Required  : total iterations (Int)
            prefix      - Optional  : prefix string (Str)
            suffix      - Optional  : suffix string (Str)
            decimals    - Optional  : positive number of decimals in percent complete (Int)
            length      - Optional  : character length of bar (Int)
            fill        - Optional  : bar fill character (Str)
            printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
        """
        percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
        # Print New Line on Complete
        if iteration == total:
            print()

    def print_list(self, list_: list, indent=0):
        if indent == 0:
            for item in list_:
                print(item)
        else:
            indent = ' ' * indent
            for item in list_:
                print(f"{indent}{item}")

    def get_list_project_repositories(self, project_id: int) -> list:
        project = self.glo.projects.get(project_id)
        return project.repositories.list()

    def print_list_project_repositories(self, project_id: int, indent=0):
        self.print_list(self.get_list_project_repositories(project_id), indent)

    def get_list_repository_tags(self, repo: object, full=False) -> list:
        if full:
            list_tags = []
            for tag in repo.tags.list():
                list_tags.append(repo.tags.get(id=tag.name))
            return list_tags
        else:
            return repo.tags.list()

    def print_list_repository_tags(self, repo: object, full, indent=0):
        self.print_list(self.get_list_repository_tags(repo, full), indent)

    def get_max_tags_in_project(self, project_id: int) -> list:
        repositories = self.get_list_project_repositories(project_id)
        list_tags = []
        i = 1
        for repo in repositories:
            self.log.info(f"\n{repo}")
            tags = self.get_list_repository_tags(repo)
            print(f"REPO: {repo.name} | {i} of {len(repositories)} | {len(tags)} tags")
            max_datetime = dateutil.parser.isoparse("1900-01-01T00:00:00.000Z")
            j = 0
            for tag in tags:
                self.log.info(f"\n{tag}")
                self.printProgressBar(j, len(tags), prefix=f"{repo.name}|{tag.name}", suffix='Complete', length=50)
                current_tag = repo.tags.get(id=tag.name)
                current_datetime = dateutil.parser.isoparse(current_tag.created_at)
                if current_datetime > max_datetime:
                    last_tag = current_tag
                    max_datetime = current_datetime
                j += 1
                self.printProgressBar(j, len(tags), prefix=f"{repo.name}|{tag.name}", suffix='Complete', length=50)
            list_tags.append(last_tag)
            i += 1
        return list_tags

    def print_max_tags_in_project(self, project_id: int, indent=0):
        self.print_list(self.get_max_tags_in_project(project_id), indent)


# project_id = 16881551
# project = gl.projects.get(project_id)
# repositories = project.repositories.list()
# for repos in repositories:
#     print(repos)
#     tags = repos.tags.list()
#     max_datetime = dateutil.parser.isoparse(repos.created_at)
#     print(max_datetime)
#     for tag in tags:
#         print(f"    {tag}")
#         current_tag = repos.tags.get(id=tag.name)
#         print(f"        {current_tag}")
#         current_datetime = dateutil.parser.isoparse(current_tag.created_at)
#         if current_datetime > max_datetime:
#             last_tag = current_tag
#             max_datetime = current_datetime
#     print(max_datetime)
#     print(last_tag)
#     break
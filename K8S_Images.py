import json
# ENV_SUFFIX = "-staging"
ENV_SUFFIX = "-dev"
with open(r'c:\!SAVE\all_pods_in_json.json') as json_file:
    data = json.load(json_file)
    unique_kind_name = set()
    for item in data['items']:
        for container in item["spec"]["containers"]:
            image = container["image"]
            if image.startswith("registry.gitlab.com"):
                kind = "deployment"
                container_name = container["name"]
                if container_name.startswith("russia-travel"):
                    kind_name = container_name
                else:
                    kind_name = item["metadata"]["name"].split('-dev-')[0] + ENV_SUFFIX
                    if kind_name.startswith("instagram-loader-"):
                        kind = "CronJob"
                        if kind_name in unique_kind_name:
                            continue
                        else:
                            unique_kind_name.add(kind_name)
                if "initContainers" in item["spec"]:
                    list_init_containers = []
                    command_str = f"kubectl -n rostourism set image {kind}/{kind_name} {container_name}={image}"
                    for init_container in item["spec"]["initContainers"]:
                        init_container_name = init_container["name"]
                        init_container_image = init_container["image"]
                        # print(f"{init_container_name}; {init_container_image}")
                        list_init_containers.append(f"{init_container_name}={init_container_image}")
                    for prefix in list_init_containers:
                        command_str = command_str + " " + prefix
                    command_str = command_str + " --record"
                else:
                    command_str = f"kubectl -n rostourism set image {kind}/{kind_name} {container_name}={image} --record"
                print(command_str)
                # print(image)

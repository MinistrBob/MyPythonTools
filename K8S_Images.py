import json
ENV_SUFFIX = "-staging"
# ENV_SUFFIX = "-dev"
with open(r'c:\!SAVE\all_pods_in_json.json') as json_file:
    data = json.load(json_file)
    unique_kind_name = set()
    for i in data['items']:
        image = i["spec"]["containers"][0]["image"]
        if image.startswith("registry.gitlab.com"):
            kind = "deployment"
            container_name = i["spec"]["containers"][0]["name"]
            if container_name.startswith("russia-travel"):
                kind_name = container_name
            else:
                kind_name = i["metadata"]["name"].split('-dev-')[0] + ENV_SUFFIX
                if kind_name.startswith("instagram-loader-"):
                    kind = "CronJob"
                    if kind_name in unique_kind_name:
                        continue
                    else:
                        unique_kind_name.add(kind_name)
            print(f"kubectl -n rostourism set image {kind}/{kind_name} {container_name}={image} --record")
            # print(image)

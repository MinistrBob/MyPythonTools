import json
with open(r'c:\!SAVE\all_pods_in_json.json') as json_file:
    data = json.load(json_file)
    for i in data['items']:
        # print(i["metadata"]["name"])
        # print(i["spec"]["containers"][0]["name"])
        # print(i["spec"]["containers"][0]["image"])
        image = i["spec"]["containers"][0]["image"]
        if image.startswith("registry.gitlab.com"):
            kind = "deployment"
            container_name = i["spec"]["containers"][0]["name"]
            kind_name = i["metadata"]["name"].split('-dev-')[0] + '-dev'
            if kind_name.startswith("instagram-loader-"):
                kind = "CronJob"
            # print(i["metadata"]["name"])
            # print(i["spec"]["containers"][0]["name"])
            # print(i["spec"]["containers"][0]["image"])
            # print(deploy_name)
            print(f"kubectl -n rostourism set image {kind}/{kind_name} {container_name}={image} --record")

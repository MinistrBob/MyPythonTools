#!/bin/env bash

set -euov pipefail
# echo "PREFIX=$1"
# echo "BASE_PATH=$2"
kubectl get pods -n rostourism -o=json > $2/all_pods_in_json.json
#python3 k8s_get_set_images.py $1 $2 | tee $2/update.sh
k8s_get_set_images.py $1 $2 | tee $2/update.sh

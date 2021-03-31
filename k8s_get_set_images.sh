#!/bin/env bash
set -euo pipefail

kubectl get pods -n rostourism -o=json > $HOME/all_pods_in_json.json
python3 k8s_get_set_images.py &1 &2 2>&1 | tee $HOME/update_&1.sh

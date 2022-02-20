#!/bin/bash
docker run --rm --name=mondi -v /home/ci/mondi:/app -v /home/ci/.ssh:/ssh -v /home/ci/.kube:/kube --user=$(id -u ci) --env MONDI_DEBUG=False --env MONDI_PROFILE=RT77 --env CI_CI_PROFILE=$CI_CI_PROFILE --env CI_CI_DEBUG=False registry.gitlab.com/i-teco/rostourism-images/mondi:latest

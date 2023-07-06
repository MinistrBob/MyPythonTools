import os


gitlab_ci_text = """image: docker:23

services:
  - docker:23-dind

variables:
  DOCKER_TLS_CERTDIR: ""
  DOCKER_DRIVER: overlay2
  DOCKER_BUILDKIT: 1
#  CI_DEBUG_TRACE: "true"
#  CI_DEBUG_SERVICES: "true"

stages:
  - build
  - test
  - push_develop
  - push

cache:
  paths:
    - .gradle/wrapper
    - .gradle/caches

test:
  image: gradle:6.3.0-jdk13
  stage: test
  only:
    - merge_requests
  script:
    - gradle -PnexusUser=${NEXUS_MAVEN_USER} -PnexusPassword=${NEXUS_MAVEN_PASSWORD} clean check

build:
  image: gradle:6.3.0-jdk13
  stage: build
  only: 
    - develop
    - master
  script:
    - gradle -Dorg.gradle.daemon=false -PnexusUser=${NEXUS_MAVEN_USER} -PnexusPassword=${NEXUS_MAVEN_PASSWORD} --build-cache assemble
  artifacts:
    paths:
      - build/libs/*.jar


push:
  image: docker:23
  stage: push
  only: 
    - master
  script:
    - docker login ${RON_DOCKER_REGISTRY} --username ${NEXUS_DOCKER_USER} --password ${NEXUS_DOCKER_PASSWORD}
    - 'docker build --build-arg BUILDKIT_INLINE_CACHE=1 --cache-from ${RON_DOCKER_REGISTRY}/<PROJECT>:master -t ${RON_DOCKER_REGISTRY}/<PROJECT>:master -t ${RON_DOCKER_REGISTRY}/<PROJECT>:$CI_JOB_ID .'
    - docker push ${RON_DOCKER_REGISTRY}/<PROJECT>:master ${RON_DOCKER_REGISTRY}/<PROJECT>:$CI_JOB_ID

push_develop:
  image: docker:23
  stage: push_develop
  only: 
    - develop
  script:
    - docker login ${RON_DOCKER_REGISTRY} --username ${NEXUS_DOCKER_USER} --password ${NEXUS_DOCKER_PASSWORD}
    - 'docker build --build-arg BUILDKIT_INLINE_CACHE=1 --cache-from ${RON_DOCKER_REGISTRY}/<PROJECT>:develop -t ${RON_DOCKER_REGISTRY}/<PROJECT>:develop -t ${RON_DOCKER_REGISTRY}/<PROJECT>:$CI_JOB_ID .'
    - docker push ${RON_DOCKER_REGISTRY}/<PROJECT>:develop
"""


# projects_text = """Algorithm Execution Service
# Auth Service
# Catalogs Service
# Clickhouse Data Service
# Criteria Service
# Data Representation Service
# Directory Service
# Ehpd Service
# Fpsr Service
# Metadata Service
# Objects Service
# Query Service
# Rfp Service
# Scheduler Service
# Smev Data Import Service"""
# projects_list = projects_text.splitlines()
# print(projects_list)

def main():
    projects_list = ['Algorithm Execution Service', 'Auth Service', 'Catalogs Service', 'Clickhouse Data Service',
                     'Criteria Service', 'Data Representation Service', 'Directory Service', 'Ehpd Service',
                     'Fpsr Service', 'Metadata Service', 'Objects Service', 'Query Service', 'Rfp Service',
                     'Scheduler Service', 'Smev Data Import Service']
    base_path = r"c:\MyGit\rosstat-ron"
    for project in projects_list:
        project_name = project.lower().replace(' ', '-')
        print(project_name)
        # print('=' * len(project.lower().replace(' ', '_')))
        # print(gitlab_ci_text.replace('<PROJECT>', project.lower().replace(' ', '_')))
        # print('=' * len(project.lower().replace(' ', '_')))
        # write gitlab_ci_text to file
        with open(os.path.join(base_path, project_name, '.gitlab-ci-iteco.yml'), 'w') as f:
            f.write(gitlab_ci_text.replace('<PROJECT>', project_name))


if __name__ == '__main__':
    main()

# mondi.py
Monitoring for docker image (mondi). Script watches for new version docker image in Gitlab Container Registry.  
The script periodically monitors the appearance of a new version of the docker image.  
If a new version is found, an action is taken, such as deploying the application.  

Приложение внутри контейнера с python:3.10 в папке /app. Контейнер запускается с помощью /home/<user>/mondi/mondi_start.sh каждые 30 мин. через cron. 
crontab:
```commandline
SHELL=/bin/bash
PATH=/usr/local/bin:/usr/bin:/usr/local/sbin:/usr/sbin:/home/ci/.local/bin:/home/ci/bin
MAILTO=""

*/30 * * * * /home/ci/mondi/mondi_start.sh >> /home/ci/mondi/mondi.log 2>&1
50 23 * * * echo cleared > /home/ci/mondi/mondi.log 2>&1
```
В контейнер монтируются папки (для приватных данных):
/home/<user>/mondi:/mondi - SETTINGS_mondi.py
/home/<user>/.ssh:/ssh - отсюда берётся ключ для работы с SSH
/home/<user>/.kube:/kube - отсюда берётся config для работы с kubernetes


## FOR DEVELOPER
### Get requirements (on Windows)
```
cd C:\MyGit\MyPythonTools\GitLab
c:\MyGit\MyPythonTools\GitLab\venv\Scripts\activate.bat

pip freeze | Out-File -Encoding UTF8 requirements.txt
```
### Docker build and run
```commandline
cd C:\MyGit\MyPythonTools\GitLab
docker build . -t ministrbob/my-python-tools-gitlab:latest
docker login --username XXX --password XXX
docker push ministrbob/my-python-tools-gitlab:latest

docker pull ministrbob/my-python-tools-gitlab:latest
docker run -it --rm ministrbob/my-python-tools-gitlab:latest bash
```

### Links
[python-gitlab v3.1.1](https://python-gitlab.readthedocs.io/en/stable/)
[requests](https://docs.python-requests.org/en/latest/user/quickstart/)
[A Beginner’s Guide to Kubernetes Python Client](https://www.velotio.com/engineering-blog/kubernetes-python-client)
[Kubernetes Python Client](https://github.com/kubernetes-client/python)
[Kubernetes Python Client.README.md](https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md)
[Telegram Bot API](https://core.telegram.org/bots/api)

### Useful
- python-gitlab only supports GitLab API v4.  
- If you use `http_username\http_password` in python-gitlab than I get error: `gitlab.exceptions.GitlabHttpError: 404: 404 Project Not Found`. With token no problem.
- On free version Gitlab only available personal token (not project and group). The token must have all the necessary rights.  

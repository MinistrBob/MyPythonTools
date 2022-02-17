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
docker run -it --rm ministrbob/my-python-tools-gitlab:latest
```

### Links
[python-gitlab v3.1.1](https://python-gitlab.readthedocs.io/en/stable/)
[requests](https://docs.python-requests.org/en/latest/user/quickstart/)
[A Beginner’s Guide to Kubernetes Python Client](https://www.velotio.com/engineering-blog/kubernetes-python-client)
[Kubernetes Python Client](https://github.com/kubernetes-client/python)
[Kubernetes Python Client.README.md](https://github.com/kubernetes-client/python/blob/master/kubernetes/README.md)

### Useful
- python-gitlab only supports GitLab API v4.  
- If you use `http_username\http_password` than I get error: `gitlab.exceptions.GitlabHttpError: 404: 404 Project Not Found`. With token no problem.
- On free version Gitlab only available personal token (not project and group). The token must have all the necessary rights.  

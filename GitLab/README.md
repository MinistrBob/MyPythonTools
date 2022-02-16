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
https://python-gitlab.readthedocs.io/en/stable/

### Useful
python-gitlab only supports GitLab API v4.  

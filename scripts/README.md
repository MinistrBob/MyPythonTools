### Docker build and run
```commandline
cd C:\MyGit\MyPythonTools\scripts
docker build . -t ministrbob/my-python-scripts:latest
docker login --username XXX --password XXX
docker push ministrbob/my-python-scripts:latest

docker pull ministrbob/my-python-scripts:latest
docker run -it --rm ministrbob/my-python-scripts:latest
```

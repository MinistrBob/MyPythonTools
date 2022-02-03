https://docs.oracle.com/cd/E91275_01/html/E96223/gsyqi.html
https://github.com/boto/boto

https://boto3.amazonaws.com/v1/documentation/api/latest/index.html
http://docs.pythonboto.org/en/latest/boto_config_tut.html
https://cloud.yandex.ru/docs/storage/tools/boto


## FOR DEVELOPER
### Get requirements (on Windows)
```
cd C:\MyGit\MyPythonTools\S3
c:\MyGit\MyPythonTools\S3\venv\Scripts\activate.bat
pip freeze | Out-File -Encoding UTF8 requirements.txt
```
### Docker build and run
```commandline
cd C:\MyGit\MyPythonTools\S3
docker build . -t ministrbob/my-python-tools-s3:latest
docker login --username XXX --password XXX
docker push ministrbob/my-python-tools-s3:latest

docker pull ministrbob/my-python-tools-s3:latest
docker run -it --rm ministrbob/my-python-tools-s3:latest
```
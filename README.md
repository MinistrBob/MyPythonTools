# MyPythonTools
Различные программки для личного пользования и автоматизации деятельности.

## Prerequisites
Python form 3.6 and up.  (f-string formatting is used)

## Install
Install Python.
Clone repository or copy *.py
Copy PASSWORDS_example.py to PASSWORDS.py and edit parameters.
```
cd C:\MyPythonTools
pip install -r C:\MyPythonTools\requirements.txt
python ControlVeeamBackup.py
```

### ControlVeeamBackup.py
Программа контролирует сделанные резервные копии VMWare ESXi VMs c помощью VeeamBackup. Сообщает администратору о наличие виртуальных машин у которых нет ни одной резервной копии или резервная копия слишком старая.  
Для работы с VMWare используется пакет pyvmomi - https://github.com/vmware/pyvmomi.  
Примеры использования - http://vmware.github.io/pyvmomi-community-samples. Но здесь могут быть устаревшие примеры.
Рабочий пример getallvms.py взял из - https://github.com/vmware/pyvmomi/tree/master/sample.  

### k8s_get_set_images.*
**RUS**: Парсинг описания подов кластера kubernetes в формате json (`kubectl get pods -o json > all_pods_in_json.json`) и получение набора команд `kubectl set images`.  
**ENG**: Parsing the description of pods of the kubernetes cluster in json format (`kubectl get pods -o json> all_pods_in_json.json`) and getting the `kubectl set images` command set.  

### gitlab_app.py
Работа с GitLab в частности получение списка самых последних образов (тэгов).  

## FOR DEVELOPER
### Get requirements
```
cd c:\MyGit\MyPythonTools
c:\Users\MinistrBob\.virtualenvs\MyPythonTools\Scripts\activate
pip freeze > c:\MyGit\MyPythonTools\requirements.txt
```

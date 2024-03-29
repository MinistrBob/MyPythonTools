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

### WMWare
Программы для VMWare.  
pyvmomi: [vmware / pyvmomi](https://github.com/vmware/pyvmomi)
Примеры от VMWare: [vmware / pyvmomi-community-samples](https://github.com/vmware/pyvmomi-community-samples)
Документация по API: [vSphere WS SDK API Docs](https://code.vmware.com/apis/968/vsphere)
VMware vSphere Automation SDK for Python: [vmware / vsphere-automation-sdk-python]

```cmd
cd C:\MyGit\MyPythonTools\VMWare
c:\MyGit\MyPythonTools\VMWare\venv\Scripts\activate.bat
pip install --upgrade pyvmomi
pip freeze | Out-File -Encoding UTF8 c:\MyGit\MyPythonTools\VMWare\requirements.txt
```
Run program (in CMD use " in PyCharm console use '):
```cmd
C:\MyGit\MyPythonTools\VMWare\venv\Scripts\python.exe C:/MyGit/MyPythonTools/VMWare/getallvms.py -s 192.168.22.1 -u 'Administrator@xxx.local' -p 'strongPassword'
```


### ControlVeeamBackup.py
Программа контролирует сделанные резервные копии VMWare ESXi VMs c помощью VeeamBackup. Сообщает администратору о наличие виртуальных машин у которых нет ни одной резервной копии или резервная копия слишком старая.  
Для работы с VMWare используется пакет pyvmomi - https://github.com/vmware/pyvmomi.  
Примеры использования - http://vmware.github.io/pyvmomi-community-samples. Но здесь могут быть устаревшие примеры.
Рабочий пример getallvms.py взял из - https://github.com/vmware/pyvmomi/tree/master/sample.  

### k8s_get_set_images.*
**RUS**: Парсинг описания подов кластера kubernetes в формате json (`kubectl get pods -o json > all_pods_in_json.json`) и получение набора команд `kubectl set images`.  
**ENG**: Parsing the description of pods of the kubernetes cluster in json format (`kubectl get pods -o json> all_pods_in_json.json`) and getting the `kubectl set images` command set.  
```
# Install
cd /.../<git path>
sudo cp -v k8s_get_set_images.sh k8s_get_set_images.py /usr/local/bin
sudo chmod +x /usr/local/bin/k8s_get_set_images.sh
sudo chmod +x /usr/local/bin/k8s_get_set_images.py

# Execute
k8s_get_set_images.sh staging $HOME
```

### gitlab_app.py
Работа с GitLab в частности получение списка самых последних образов (тэгов).  

## FOR DEVELOPER
### Get requirements (on Windows)
```
cd c:\MyGit\MyPythonTools
c:\Users\MinistrBob\.virtualenvs\MyPythonTools\Scripts\activate
pip freeze | Out-File -Encoding UTF8 requirements.txt
```

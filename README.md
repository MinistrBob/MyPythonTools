# MyPythonTools
Различные программки для личного пользования и автоматизации деятельности.

## Get packages
cd c:\MyGit\MyPythonTools
c:\Users\MinistrBob\.virtualenvs\MyPythonTools\Scripts\activate
pip freeze > c:\MyGit\MyPythonTools\requirements.txt

## Install
Install Python.
Clone repository or copy *.py
Copy PASSWORDS_example.py to PASSWORDS.py and edit parameters.
cd C:\MyPythonTools
pip install -r C:\MyPythonTools\requirements.txt
python ControlVeeamBackup.py

## ControlVeeamBackup.py
Программа контролирует сделаные резервные копии VMWare ESXi VMs c помощью VeeamBackup. Сообщает администратору о наличие виртуальных машин у которых нет ни одной резервной копии или резервная копия слишком старая.  
Для работы с VMWare используется пакет pyvmomi - https://github.com/vmware/pyvmomi.  
Примеры использования - http://vmware.github.io/pyvmomi-community-samples. Но здесь могут быть устаревшие примеры.
Рабочий пример getallvms.py взял из - https://github.com/vmware/pyvmomi/tree/master/sample.  

  

  

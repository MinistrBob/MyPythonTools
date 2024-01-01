@echo off
pushd %~dp0
powershell -Command "& {Start-Process 'python' -ArgumentList 'socket_server.py' -Verb RunAs}"

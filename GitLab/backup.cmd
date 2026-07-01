rem Hostname
rem set compname=%COMPUTERNAME%
FOR /F %%H IN ('hostname') DO SET compname=%%H
if "%compname%"=="" set compname=UNKNOWN

rem Date and time for file name, hours are counted <10 (one character instead of two => 07).
FOR /F "tokens=1-4 delims=., " %%i IN ('DATE /t') DO SET pdate=%%k%%j%%i
FOR /F "tokens=1-4 delims=:"  %%b IN ('TIME /T') DO SET ptime=%%b%%c
set token=%pdate%-%ptime%-%compname%
rem echo %token%

rem Project
SET PNAME=Gitlab
SET PPATH=_MinistrBob\MyPythonTools
SET PDIR=%MYGIT_PATH%\%PPATH%\%PNAME%
rem Backup
SET BP=%BACKUP_GIT_PATH%\%PPATH%\%PNAME%
rem Path to WinRAR
rem SET WINRAR=C:\Program Files\WinRAR\WinRAR.exe
rem Path to 7-Zip
SET SZIP=c:\Program Files\7-Zip\7z.exe

mkdir "%BP%"
rem "%WINRAR%" a -r -s -m5 -md1024 -ag_YYYYMMDD-NN "%BP%\%PNAME%.rar" "c:\MyGit\%PNAME%\*"
"%SZIP%" a -t7z -r -mx9 -mtc=on -mta=on -mtr=on -xr@exclude.txt -xr!__pycache__ "%BP%\%token%-%PNAME%.7z" "%PDIR%\*"
"%SZIP%" a -t7z -r -mx9 -mtc=on -mta=on -mtr=on -mhe=on -p%mypass% -ir@exclude.txt "%BP%\%token%-%PNAME%-PASS.7z" "%PDIR%\exclude.txt"
rem Skips the last 14 files. Since each backup is 2 files, there are 7 LAST backups.
cd /d "%BP%"
for /f "skip=14 eol=: delims=" %%F in ('dir /b /o-d *.7z') do @del "%%F"

pause

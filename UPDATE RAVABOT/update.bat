@echo off
for /f "delims=" %%a in (save.txt) do set lasttimetaken=%%a
chcp 28591 > nul
echo Appuyez sur n'importe quel touche pour lancer le push (dernière exécution en %lasttimetaken%sec.)
echo.

set starttime=%TIME%
set startcsec=%STARTTIME:~9,2%
set startsecs=%STARTTIME:~6,2%
set startmins=%STARTTIME:~3,2%
set starthour=%STARTTIME:~0,2%
set /a starttime=(%starthour%*60*60*100)+(%startmins%*60*100)+(%startsecs%*100)+(%startcsec%)

cd C:\Program Files\PuTTY
plink.exe -ssh USER@NOM_PRESET -P PORT -pw USER -m "C:\....chemin....\commandupdate.txt"

set endtime=%time%
set endcsec=%endTIME:~9,2%
set endsecs=%endTIME:~6,2%
set endmins=%endTIME:~3,2%
set endhour=%endTIME:~0,2%
if %endhour% LSS %starthour% set /a endhour+=24
set /a endtime=(%endhour%*60*60*100)+(%endmins%*60*100)+(%endsecs%*100)+(%endcsec%)

set /a timetaken= ( %endtime% - %starttime% )
set /a timetakens= %timetaken% / 100
set timetaken=%timetakens%.%timetaken:~-2%

cd "C:\....chemin....\UPDATE RAVABOT"
echo %timetaken% > save.txt
echo.

set /a timetaken=%timetaken% + 5

for %%d in (%timetaken%) do call :duration %%d

pause

exit/b 0

:duration
set output=
set /a "wk=%1/604800,rem=%1%%604800"
if %wk% neq 0 set "output= %wk% sem,"

set /a "d=%rem%/86400,rem=%rem%%%86400"
if %d% neq 0 set "output=%output% %d% j"

set /a "hr=%rem%/3600,rem=%rem%%%3600"
if %hr% neq 0 set "output=%output% %hr% h"

set /a "min=%rem%/60,rem=%rem%%%60"
if %min% neq 0 set "output=%output% %min% min"

if %rem% neq 0 set "output=%output% %rem% sec"

if %1 gtr 0 echo Exécution en %output%.
goto :EOF


set KodiLaunchCmd="%PROGRAMFILES%\Kodi\Kodi.exe"

echo Stopping Kodi...
echo.
taskkill /f /IM Kodi.exe>nul 2>nul

echo Starting %*...
echo.
%*


REM SOMETIMES xbmc starts too fast, and on some hardware if there is still a millisecond of sound being used, XBMC starts witout sound and some emulators say there is a problem with the sound hardware. If so, remove the REM of the next line:
REM timeout 1

REM Restart XBMC
echo Restarting Kodi...

REM Done? Restart Kodi
%KodiLaunchCmd%



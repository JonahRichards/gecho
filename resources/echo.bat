@echo off

setlocal

set SUBDIR=%1
set EXEPATH=%2
set POSTPATH=%3
set ANIMPATH=%4
set POST=%5
set ANIM=%6

echo Created directory %SUBDIR%
echo %ANIM_PATH%
echo %POST_PATH%

echo %%%%%%%%%%%%%%%%%%%%%%%%%%%% STARTING %%%%%%%%%%%%%%%%%%%%%%%%%%

copy %EXEPATH% %SUBDIR%
copy %POSTPATH% %SUBDIR%
copy %ANIMPATH% %SUBDIR%

cd %SUBDIR%

echo %%%%%%%%%%%%%%%%%%%%%%%%%%%% EXECUTING ECHO %%%%%%%%%%%%%%%%%%%%%%%%%%%%

%~n2.exe
del %~n2.exe

if "%POST%"=="1" (
echo %%%%%%%%%%%%%%%%%%%%%%%%%%%% EXECUTING POST PROCESSING %%%%%%%%%%%%%%%%%%%%%%%%%%%%
python processing.py
del processing.py
)

if "%ANIM%"=="1" (
echo %%%%%%%%%%%%%%%%%%%%%%%%%%%% GENERATING MONITOR ANIMATIONS %%%%%%%%%%%%%%%%%%%%%%%%%%%%
python gif.py
del gif.py
)

echo %%%%%%%%%%%%%%%%%%%%%%%%%%%% FINISHED %%%%%%%%%%%%%%%%%%%%%%%%%%%%

endlocal
exit /b
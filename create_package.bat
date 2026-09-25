@echo off
echo Creating ZSDumper Windows package...

REM Create package directory
if not exist "ZSDumper_Windows" mkdir "ZSDumper_Windows"

REM Copy executable and dependencies
xcopy /E /I /Y "dist\ZSDumper" "ZSDumper_Windows"

REM Create launcher
echo @echo off > "ZSDumper_Windows\ZSDumper.bat"
echo title ZSDumper >> "ZSDumper_Windows\ZSDumper.bat"
echo color 0A >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo echo ======================================== >> "ZSDumper_Windows\ZSDumper.bat"
echo echo           ZSDumper >> "ZSDumper_Windows\ZSDumper.bat"
echo echo ======================================== >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo set /p LINK=Enter cfx.re link:  >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo echo [*] Launching ZSDumper with link: %%LINK%% >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo ZSDumper.exe %%LINK%% >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo echo ======================================== >> "ZSDumper_Windows\ZSDumper.bat"
echo echo        ZSDumper / Dump Finished! >> "ZSDumper_Windows\ZSDumper.bat"
echo echo   Decrypted resources are in /Output >> "ZSDumper_Windows\ZSDumper.bat"
echo echo ======================================== >> "ZSDumper_Windows\ZSDumper.bat"
echo. >> "ZSDumper_Windows\ZSDumper.bat"
echo pause >> "ZSDumper_Windows\ZSDumper.bat"

REM Copy README
copy README.md "ZSDumper_Windows\README.txt" /Y

echo Package created in ZSDumper_Windows folder!
pause

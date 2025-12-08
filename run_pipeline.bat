@echo off
cd /d "%~dp0"
echo ----- Lancement du pipeline Fraude Bancaire -----
"%USERPROFILE%\anaconda3\python.exe" ".\src\pipeline\pipeline.py"
echo.
echo Pipeline termine. Appuyez sur une touche pour fermer.
pause >nul

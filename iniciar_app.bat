@echo off
cd /d "%~dp0"
echo Abrindo o app de holerites no navegador...
echo.
echo Pra fechar o app, clique nessa janela e aperte Ctrl+C.
echo.
"%~dp0venv\Scripts\streamlit.exe" run app.py
pause

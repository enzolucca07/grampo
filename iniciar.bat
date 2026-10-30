@echo off
rem Abre o Grampo numa janela propria (sem navegador e sem janela preta). No navegador: app.py --navegador
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Ambiente virtual nao encontrado. Veja a secao "Instalar para desenvolver" do README.md.
  pause
  exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" app.py

@echo off
chcp 65001 >nul
REM 공장 차임벨 실행 (검은 창 없이 백그라운드)
REM Chay Chuong nha may (chay nen, khong hien cua so den)

cd /d "%~dp0"

REM pythonw.exe (창 없는 파이썬) 우선 사용
where pythonw >nul 2>&1
if errorlevel 1 (
    start "" python "%~dp0chime.py" --show
) else (
    start "" pythonw "%~dp0chime.py"
)
exit /b 0

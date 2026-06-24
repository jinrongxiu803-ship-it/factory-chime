@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
title 공장 차임벨 설치 / Cai dat Chuong nha may

REM ============================================================
REM   공장 차임벨 - 올인원 설치 (더블클릭 한 번이면 끝)
REM   Cai dat tat-ca-trong-mot (chi nhap dup MOT lan)
REM ============================================================

cd /d "%~dp0"

echo.
echo ============================================================
echo            공장 차임벨 설치를 시작합니다
echo            Bat dau cai dat Chuong nha may
echo ============================================================
echo.
echo   이 창은 자동으로 진행됩니다. 잠시 기다려 주세요.
echo   Cua so se tu dong chay. Vui long doi.
echo.

REM ---------- 1. Python 확인 / 없으면 자동 설치 ----------
echo [1/4] Python 확인 중... / Kiem tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo       Python 이 없습니다. 자동 설치를 시도합니다...
    echo       Khong co Python. Dang thu tu cai...
    REM Windows 10/11 내장 winget 으로 자동 설치 시도
    winget install -e --id Python.Python.3.12 --silent --accept-package-agreements --accept-source-agreements >nul 2>&1
    REM PATH 갱신을 위해 재확인
    python --version >nul 2>&1
    if errorlevel 1 (
        echo.
        echo   [안내] Python 자동 설치에 실패했습니다.
        echo   아래 사이트에서 Python 을 직접 설치한 뒤,
        echo   이 파일을 다시 더블클릭하세요.
        echo   설치 화면에서 "Add Python to PATH" 를 꼭 체크하세요!
        echo.
        echo   https://www.python.org/downloads/
        echo.
        start https://www.python.org/downloads/
        pause
        exit /b 1
    )
)
echo       OK
echo.

REM ---------- 2. 필요한 패키지 설치 ----------
echo [2/4] 필요한 구성요소 설치 중... / Dang cai cac thanh phan...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install edge-tts pygame pystray Pillow >nul 2>&1
echo       OK
echo.

REM ---------- 3. 고음질 베트남어 음성 생성 ----------
echo [3/4] 고음질 베트남어 음성 생성 중... / Dang tao giong noi...
echo       (인터넷 연결 필요 / Can Internet)
python generate_voice.py
if errorlevel 1 (
    echo       [참고] 음성 생성 실패해도 프로그램은 작동합니다
    echo              (기본 음성으로 대체). 나중에 다시 시도 가능.
)
echo.

REM ---------- 4. 부팅 시 자동 시작 등록 ----------
echo [4/4] 자동 시작 등록 중... / Dang ky tu chay...

REM pythonw.exe 경로 찾기 (검은 창 없이 백그라운드 실행)
for /f "delims=" %%P in ('where pythonw 2^>nul') do set "PYW=%%P"
if not defined PYW (
    for /f "delims=" %%P in ('where python 2^>nul') do set "PYW=%%P"
)

set "SCRIPT=%~dp0chime.py"
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"

powershell -NoProfile -Command ^
  "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('%STARTUP%\FactoryChime.lnk');" ^
  "$s.TargetPath='!PYW!';" ^
  "$s.Arguments='\"%SCRIPT%\"';" ^
  "$s.WorkingDirectory='%~dp0';" ^
  "$s.WindowStyle=7;" ^
  "$s.Description='Factory Chime';" ^
  "$s.Save()" >nul 2>&1

if exist "%STARTUP%\FactoryChime.lnk" (
    echo       OK
) else (
    echo       [참고] 자동 시작 등록에 실패했습니다.
    echo              "시작.bat" 을 직접 실행해서 쓰셔도 됩니다.
)
echo.

REM ---------- 지금 바로 실행 ----------
echo ============================================================
echo            설치 완료! / Cai dat hoan tat!
echo ============================================================
echo   - 지금부터 PC 를 켜면 차임벨이 자동으로 백그라운드 실행됩니다
echo   - 우측 하단 트레이의 "종 아이콘" 으로 설정/종료 가능
echo   - Tu bay gio chuong tu chay nen khi mo may
echo.
echo   지금 바로 한 번 실행해 봅니다...
echo   Dang chay thu ngay bay gio...
echo ============================================================

start "" "!PYW!" "%SCRIPT%"

timeout /t 5 >nul
exit /b 0

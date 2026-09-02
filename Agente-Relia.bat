@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title RELIA 2.0 Agentico - Plataforma de Mediacao Leitora
color 0A

REM Garantir que o directorio de trabalho e o directorio do script
cd /d "%~dp0"

echo.
echo ================================================================
echo    RELIA 2.0 - Roteiro de Leitura Empatica e Interativa
echo    com Agentes (PhD CEHUM/UMinho)
echo ----------------------------------------------------------------
echo    Backend:  FastAPI + SQLAlchemy    http://localhost:8000
echo    Frontend: HTML/CSS/JS            http://localhost:3030
echo    Swagger:  Documentacao da API    http://localhost:8000/docs
echo ================================================================
echo.

REM --------------------------------------------------------
REM 1. Verificar se Python esta instalado
REM --------------------------------------------------------
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado no PATH do sistema.
    echo        Instale Python 3.10+ de https://python.org e adicione ao PATH.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo [INFO] %PYVER% detectado.
echo.

REM --------------------------------------------------------
REM 2. Criar/Activar virtualenv
REM --------------------------------------------------------
set VENV_DIR=relia-env

if not exist "%VENV_DIR%\Scripts\activate.bat" (
    echo [INFO] A criar ambiente virtual '%VENV_DIR%'...
    python -m venv %VENV_DIR%
    if !errorlevel! neq 0 (
        echo [ERRO] Falha ao criar virtualenv.
        pause
        exit /b 1
    )
)

echo [INFO] A activar ambiente virtual...
call "%VENV_DIR%\Scripts\activate.bat"

REM --------------------------------------------------------
REM 3. Instalar dependencias
REM --------------------------------------------------------
echo.
echo [INFO] A verificar dependencias do backend...
python -m pip install -q -r backend\requirements.txt
if %errorlevel% neq 0 (
    echo [AVISO] Algumas dependencias podem nao ter sido instaladas.
    echo         Verifique o ficheiro backend\requirements.txt
)

REM --------------------------------------------------------
REM 4. Executar testes rapidos (opcional)
REM --------------------------------------------------------
echo.
set /p RUNTESTS="Deseja executar os testes antes de iniciar? (S/N): "
if /i "%RUNTESTS%"=="S" (
    echo.
    echo [INFO] A executar testes unitarios e de integracao...
    python -m pytest backend\tests\ -v --tb=short
    if !errorlevel! neq 0 (
        echo.
        echo [AVISO] Alguns testes falharam.
        set /p CONTINUAR="Deseja continuar mesmo assim? (S/N): "
        if /i not "!CONTINUAR!"=="S" (
            echo A encerrar.
            pause
            exit /b 1
        )
    ) else (
        echo [OK] Todos os testes passaram com sucesso!
    )
    echo.
)

REM --------------------------------------------------------
REM 5. Iniciar FastAPI Backend (porta 8000)
REM --------------------------------------------------------
echo [INFO] A iniciar FastAPI backend na porta 8000...
start "RELIA-Backend" /MIN cmd /c "cd /d "%~dp0" && call "%VENV_DIR%\Scripts\activate.bat" && python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload"

REM Aguardar backend arrancar com polling
echo [INFO] A aguardar inicializacao do backend...
set BACKEND_OK=0
for /l %%i in (1,1,8) do (
    if !BACKEND_OK! equ 0 (
        timeout /t 1 /nobreak >nul
        python -c "import urllib.request; res = urllib.request.urlopen('http://127.0.0.1:8000/'); exit(0 if res.getcode() == 200 else 1)" 2>nul
        if !errorlevel! equ 0 (
            set BACKEND_OK=1
        )
    )
)

if "!BACKEND_OK!"=="1" (
    echo [OK] Backend online e a responder!
) else (
    echo [AVISO] O backend esta a demorar a responder. Continuando o arranque...
)

REM --------------------------------------------------------
REM 6. Iniciar Frontend (porta 3030)
REM --------------------------------------------------------
echo [INFO] A iniciar frontend na porta 3030...
start "RELIA-Frontend" /MIN cmd /c "cd /d "%~dp0frontend" && python -m http.server 3030"

REM Aguardar frontend arrancar
timeout /t 2 /nobreak >nul

REM --------------------------------------------------------
REM 7. Abrir browser automaticamente
REM --------------------------------------------------------
echo.
echo ================================================================
echo   RELIA 2.0 esta a correr com sucesso!
echo.
echo   Frontend:  http://localhost:3030
echo   API Docs:  http://localhost:8000/docs
echo   Health:    http://localhost:8000/
echo.
echo   Para parar: prima qualquer tecla nesta janela
echo ================================================================
echo.

start "" http://localhost:3030

REM --------------------------------------------------------
REM 8. Manter vivo - espera por tecla para encerrar
REM --------------------------------------------------------
echo Prima qualquer tecla para parar todos os servicos...
pause >nul

REM Cleanup
echo.
echo [INFO] A encerrar servicos...
taskkill /FI "WINDOWTITLE eq RELIA-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq RELIA-Frontend*" /F >nul 2>&1
echo [INFO] Todos os servicos foram encerrados.
echo.
timeout /t 2 /nobreak >nul

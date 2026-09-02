@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title RELIA 2.0 Agentico - Docker Compose
color 0B

cd /d "%~dp0"

echo.
echo ================================================================
echo    RELIA 2.0 - Arranque via Docker Compose
echo ----------------------------------------------------------------
echo    Backend:  FastAPI + SQLAlchemy    http://localhost:8000
echo    Frontend: Nginx (HTML/CSS/JS)     http://localhost:3030
echo    Swagger:  Documentacao da API    http://localhost:8000/docs
echo ================================================================
echo.

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao foi encontrado no PATH do sistema.
    echo        Instale ou inicie o Docker Desktop.
    pause
    exit /b 1
)

echo [INFO] A iniciar containers Docker...
docker compose up -d --build

if %errorlevel% neq 0 (
    echo [ERRO] Falha ao construir/iniciar containers Docker.
    pause
    exit /b 1
)

echo [INFO] Containers em execucao! A abrir http://localhost:3030 ...
timeout /t 3 /nobreak >nul
start "" http://localhost:3030

echo.
echo ================================================================
echo   RELIA 2.0 esta a correr em Docker!
echo   Para parar os containers: prima qualquer tecla nesta janela
echo ================================================================
echo.
pause >nul

echo [INFO] A parar containers...
docker compose down
echo [INFO] Containers encerrados.
timeout /t 2 /nobreak >nul

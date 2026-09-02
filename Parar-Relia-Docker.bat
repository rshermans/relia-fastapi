@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title RELIA 2.0 Agentico - Encerrar Docker Containers
color 0C

cd /d "%~dp0"

echo.
echo ================================================================
echo    A encerrar os containers Docker do RELIA 2.0...
echo ================================================================
echo.

where docker >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Docker nao foi encontrado no PATH.
    pause
    exit /b 1
)

docker compose down

if %errorlevel% equ 0 (
    echo.
    echo [OK] Todos os containers Docker foram encerrados com sucesso.
) else (
    echo.
    echo [AVISO] Ocorreu uma advertencia ao encerrar os containers Docker.
)

echo.
timeout /t 3 /nobreak >nul

@echo off
setlocal EnableDelayedExpansion
chcp 65001 >nul
title RELIA 2.0 Agentico - Encerrar Servicos Locais
color 0C

cd /d "%~dp0"

echo.
echo ================================================================
echo    A encerrar todos os servicos locais do RELIA 2.0...
echo ================================================================
echo.

REM 1. Encerrar processos por titulo de janela
taskkill /FI "WINDOWTITLE eq RELIA-Backend*" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq RELIA-Frontend*" /F >nul 2>&1

REM 2. Libertar porta 8000 (Backend FastAPI / Uvicorn) se ainda estiver presa
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":8000.*LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

REM 3. Libertar porta 3030 (Frontend Python HTTP Server) se ainda estiver presa
for /f "tokens=5" %%a in ('netstat -aon 2^>nul ^| findstr /r ":3030.*LISTENING"') do (
    taskkill /f /pid %%a >nul 2>&1
)

echo [OK] Todos os servicos locais (Backend:8000 e Frontend:3030) foram encerrados.
echo.
timeout /t 3 /nobreak >nul

@echo off
title Servidor Scriptura TCC
echo Ativando o ambiente virtual (venv)...
call venv\Scripts\activate.bat

echo =================================================================
echo  Iniciando a API em http://127.0.0.1:8000
echo  ESTA JANELA PRECISA FICAR ABERTA DURANTE O USO.
echo =================================================================

uvicorn main:app

echo Servidor encerrado.
pause
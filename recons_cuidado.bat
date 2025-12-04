@echo off
title Scriptura - RESET TOTAL
color 4f
echo =================================================================
echo  ATENCAO: ISSO VAI APAGAR O BANCO DE DADOS E RECRIAR DO ZERO
echo  Todos os dados serao resetados para o padrao do script.
echo =================================================================
pause

echo.
echo 1. Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo 2. Resetando Banco de Dados (Apagando e Criando Tabelas)...
python scripts_db.py

echo.
echo 3. Convertendo PDFs base...
python auto_converter.py

echo.
echo 4. Processando IA (Trechos)...
python processar_textos.py

echo.
echo 5. Processando IA (Temas)...
python processar_temas.py

echo.
echo =================================================================
echo  RESET COMPLETO. O SISTEMA ESTA LIMPO.
echo =================================================================
pause
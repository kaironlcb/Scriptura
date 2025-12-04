@echo off
title Scriptura - Atualizar Inteligencia
echo =================================================================
echo  ATUALIZANDO INDICES DA IA (SEM APAGAR O BANCO)
echo =================================================================

echo 1. Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo.
echo 2. Convertendo novos PDFs para TXT...
python auto_converter.py

echo.
echo 3. Recriando indices de TRECHOS (Busca exata)...
python processar_textos.py

echo.
echo 4. Recriando indices de TEMAS (Busca semantica)...
python processar_temas.py

echo.
echo =================================================================
echo  PROCESSO CONCLUIDO COM SUCESSO!
echo  Pode fechar esta janela e rodar o 'iniciar.bat'.
echo =================================================================
pause
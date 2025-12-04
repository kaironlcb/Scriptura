@echo off
title Scriptura - Instalacao
echo =================================================================
echo  INSTALANDO DEPENDENCIAS DO PROJETO
echo =================================================================

echo 1. Criando ambiente virtual (se nao existir)...
python -m venv venv

echo.
echo 2. Ativando venv...
call venv\Scripts\activate.bat

echo.
echo 3. Atualizando o PIP...
python.exe -m pip install --upgrade pip

echo.
echo 4. Instalando bibliotecas (requirements.txt)...
pip install fastapi uvicorn sqlite3 spacy sentence-transformers scikit-learn numpy rank_bm25 pdfplumber python-multipart

echo.
echo 5. Baixando modelo de linguagem do SpaCy (pt_core_news_lg)...
python -m spacy download pt_core_news_lg

echo.
echo =================================================================
echo  INSTALACAO CONCLUIDA! AGORA RODE O 'iniciar.bat'
echo =================================================================
pause
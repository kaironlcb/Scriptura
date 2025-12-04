# main.py

import os
import sqlite3
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity

# --- Modelos Pydantic ---

# Modelo para a ENTRADA de dados
class TextoParaAnalisar(BaseModel):
    texto: str

# NOVO: Modelo para a SAÍDA de dados
class InfoObraResponse(BaseModel):
    titulo: str
    autor: str
    ano_lancamento: int 
    genero: str
    movimento_literario: str 


# --- Carregamento dos Modelos e do Banco ---

# Carrega os objetos do índice de busca salvos pelo script processar_textos.py
try:
    vectorizer = joblib.load('vectorizer.pkl')
    tfidf_matrix = joblib.load('tfidf_matrix.pkl')
    ids_documentos = joblib.load('ids_documentos.pkl')
    print("Índice de busca carregado com sucesso.")
except FileNotFoundError:
    print("Arquivos de índice não encontrados. Execute o script 'processar_textos.py' primeiro.")
    vectorizer = tfidf_matrix = ids_documentos = None

# Caminho para o banco de dados
DB_PATH = 'literatura.db'

# --- Inicia a aplicação FastAPI ---

app = FastAPI(
    title="Scriptura API",
    description="Uma API para Análise e Recomendação Literária.",
    version="0.1.0",
)


@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API do Scriptura!"}


# --- Endpoint de Identificação de Obra (Versão Atualizada) ---

@app.post("/identificar-obra", response_model=InfoObraResponse)
async def identificar_obra(item: TextoParaAnalisar):
    """
    Recebe um trecho de texto e tenta identificar a obra, autor e gênero
    usando o banco de dados e índice local.
    """
    if not all([vectorizer, tfidf_matrix, ids_documentos]):
        raise HTTPException(status_code=500, detail="Índice de busca não está carregado.")

    # 1. Vetorizar o texto de entrada do usuário
    texto_vetorizado = vectorizer.transform([item.texto])

    # 2. Calcular a similaridade com todos os parágrafos do nosso acervo
    similaridades = cosine_similarity(texto_vetorizado, tfidf_matrix)

    # 3. Encontrar o parágrafo com a maior similaridade
    indice_do_melhor_paragrafo = similaridades.argmax()
    id_livro_encontrado = ids_documentos[indice_do_melhor_paragrafo]

    # 4. Buscar os dados do livro correspondente no banco de dados SQLite
    try:
        conn = sqlite3.connect(DB_PATH)
        # Garante que o resultado seja um dicionário (mais fácil de trabalhar)
        conn.row_factory = sqlite3.Row 
        cursor = conn.cursor()

        # Selecionamos APENAS as colunas que queremos
        cursor.execute(
            "SELECT titulo, autor, ano_lancamento, genero, movimento_literario FROM livros WHERE id = ?",
            (id_livro_encontrado,)
        )
        resultado = cursor.fetchone()
        conn.close()

        if resultado is None:
            raise HTTPException(status_code=404, detail="Obra correspondente não encontrada no banco de dados.")
        
        # O FastAPI vai garantir que o dicionário "resultado" seja retornado
        # no formato definido pelo "InfoObraResponse".
        return resultado

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
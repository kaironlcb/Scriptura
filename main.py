import os
import sqlite3
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from typing import List
from sklearn.metrics.pairwise import cosine_similarity

# --- Modelos Pydantic (Estrutura de Dados) ---

class ObraBase(BaseModel):
    titulo: str
    autor: str
    ano_lancamento: int | None
    genero: str | None
    movimento_literario: str | None
    url_download: str | None

class ResultadoComRecomendacoes(BaseModel):
    obra_identificada: ObraBase
    recomendacoes_por_autor: List[ObraBase]
    recomendacoes_por_genero: List[ObraBase]

class TextoParaAnalisar(BaseModel):
    texto: str = Field(min_length=15)

# --- Carregamento dos Modelos e Definições Globais ---

DB_PATH = 'literatura.db'

print("Carregando o índice de busca...")
try:
    vectorizer = joblib.load('vectorizer.pkl')
    tfidf_matrix = joblib.load('tfidf_matrix.pkl')
    ids_documentos = joblib.load('ids_documentos.pkl')
    print("Índice de busca carregado com sucesso.")
except FileNotFoundError:
    print("AVISO: Arquivos de índice (vectorizer.pkl, etc.) não encontrados.")
    print("Execute o script 'processar_textos.py' para criá-los.")
    vectorizer = tfidf_matrix = ids_documentos = None

# --- Inicia a aplicação FastAPI ---

app = FastAPI(
    title="Scriptura API",
    description="Uma API para Análise e Recomendação Literária.",
    version="0.3.0",
)

# Monta o diretório 'static' para servir os PDFs
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoints da API ---

@app.get("/")
def read_root():
    """Endpoint raiz da aplicação."""
    return {"message": "Bem-vindo à API do Scriptura!"}

@app.post("/identificar-obra", response_model=ResultadoComRecomendacoes)
async def identificar_obra_com_recomendacoes(item: TextoParaAnalisar):
    """
    Recebe um trecho de texto, identifica a obra e retorna
    recomendações baseadas no autor e no gênero.
    """
   # --- CORREÇÃO APLICADA AQUI ---
    if vectorizer is None or tfidf_matrix is None or ids_documentos is None:
        raise HTTPException(status_code=500, detail="Índice de busca não está carregado. Execute 'processar_textos.py'.")

    # Lógica de busca com TF-IDF
    texto_vetorizado = vectorizer.transform([item.texto])
    similaridades = cosine_similarity(texto_vetorizado, tfidf_matrix)
    indice_do_melhor_paragrafo = similaridades.argmax()
    id_livro_encontrado = ids_documentos[indice_do_melhor_paragrafo]

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Busca a obra principal
        cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro_encontrado,))
        livro_principal_row = cursor.fetchone()

        if livro_principal_row is None:
            conn.close()
            raise HTTPException(status_code=404, detail="Obra não encontrada no banco de dados para o ID correspondente.")

        # Busca as recomendações
        autor_principal = livro_principal_row["autor"]
        genero_principal = livro_principal_row["genero"]

        cursor.execute("SELECT * FROM livros WHERE autor = ? AND id != ? LIMIT 2", (autor_principal, id_livro_encontrado))
        recomendacoes_autor_rows = cursor.fetchall()

        cursor.execute("SELECT * FROM livros WHERE genero = ? AND id != ? LIMIT 2", (genero_principal, id_livro_encontrado))
        recomendacoes_genero_rows = cursor.fetchall()
        
        conn.close()

        # Função auxiliar para formatar a resposta
        def formatar_livro(row):
            if not row:
                return None
            livro = dict(row)
            if livro.get("caminho_pdf"):
                livro["url_download"] = f"/{livro['caminho_pdf']}"
            else:
                livro["url_download"] = None
            return livro

        # Formata a resposta final
        livro_principal_formatado = formatar_livro(livro_principal_row)
        recomendacoes_autor_formatado = [formatar_livro(row) for row in recomendacoes_autor_rows]
        recomendacoes_genero_formatado = [formatar_livro(row) for row in recomendacoes_genero_rows]

        return {
            "obra_identificada": livro_principal_formatado,
            "recomendacoes_por_autor": recomendacoes_autor_formatado,
            "recomendacoes_por_genero": recomendacoes_genero_formatado
        }
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")

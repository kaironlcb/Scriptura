# main.py (v3.3 - Completo com Modo Auditoria)

import sqlite3
import joblib
import numpy as np
import spacy
import re
import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

# --- Modelos Pydantic (Estrutura de Dados) ---

class ObraBase(BaseModel):
    titulo: str
    autor: str
    ano_lancamento: int | None
    genero: str | None
    movimento_literario: str | None
    url_download: str | None

class ResultadoComPontuacao(BaseModel):
    pontuacao: float
    obra: ObraBase

class TextoParaAnalisar(BaseModel):
    texto: str = Field(min_length=15)

# --- Carregamento dos Modelos e Definições Globais ---

DB_PATH = 'literatura.db'
print("Carregando o 'cérebro' semântico (Embeddings)...")
try:
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings_matrix = joblib.load('embeddings.pkl')
    ids_documentos = joblib.load('ids_documentos.pkl')
    print("Modelo e índice de busca carregados com sucesso.")
except FileNotFoundError:
    print("AVISO: Arquivos de índice (embeddings.pkl, etc.) não encontrados.")
    print("Execute o script 'processar_textos.py' para criá-los.")
    model = embeddings_matrix = ids_documentos = None

# --- Inicia a aplicação FastAPI ---

app = FastAPI(
    title="Scriptura API (v3.3 - Modo Auditoria)",
    description="Uma API para Análise Semântica.",
    version="3.3.0",
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoints da API ---

@app.get("/")
def read_root():
    """Endpoint raiz da aplicação."""
    return {"message": "Bem-vindo à API Semântica do Scriptura!"}


# --- NOVO ENDPOINT DE AUDITORIA (JÁ INCLUÍDO NO LUGAR CERTO) ---
@app.get("/auditar-livro/{livro_id}")
def auditar_chunks_do_livro(livro_id: int):
    """
    Endpoint de depuração. Pega um ID de livro, processa o .txt
    associado usando a MESMA lógica do processar_textos.py,
    e retorna os 5 primeiros chunks de texto puro.
    """
    print(f"[AUDITORIA] Buscando chunks para o livro ID: {livro_id}")
    
    # Regras de Chunking (iguais ao processar_textos.py v3.3)
    CHUNK_SIZE = 3
    CHUNK_OVERLAP = 2
    STEP_SIZE = CHUNK_SIZE - CHUNK_OVERLAP
    
    try:
        # Carrega o spaCy (só para este endpoint)
        nlp_audit = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
        nlp_audit.max_length = 5000000
        nlp_audit.add_pipe('sentencizer')
        
        # Busca o caminho do .txt no banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_arquivo, titulo FROM livros WHERE id = ?", (livro_id,))
        resultado = cursor.fetchone()
        conn.close()
        
        if not resultado:
            raise HTTPException(status_code=404, detail="Livro não encontrado.")
            
        caminho_arquivo, titulo = resultado
        print(f"[AUDITORIA] Encontrado: {titulo}. Lendo arquivo: {caminho_arquivo}")

        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            texto_original = f.read()

        # Lógica de limpeza (IDÊNTICA ao processar_textos.py v3.3)
        whitespace_chars = string.whitespace + '\x0c'
        texto_limpo = texto_original.lstrip(whitespace_chars)
        texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo)
        
        # Lógica de fatiamento (IDÊNTICA)
        doc_spacy = nlp_audit(texto_limpo)
        frases = [s.text.strip() for s in doc_spacy.sents if s.text.strip()]
        
        chunks_de_texto = []
        for i in range(0, len(frases) - CHUNK_SIZE + 1, STEP_SIZE):
            chunk_frases = frases[i : i + CHUNK_SIZE]
            chunk_texto = " ".join(chunk_frases)
            chunks_de_texto.append(chunk_texto)
            
        # Retorna os 5 primeiros chunks
        return {
            "livro_id": livro_id,
            "titulo": titulo,
            "total_chunks_gerados": len(chunks_de_texto),
            "primeiros_5_chunks": chunks_de_texto[:5]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a auditoria: {e}")
# --- FIM DO NOVO ENDPOINT ---


@app.post("/identificar-obra", response_model=List[ResultadoComPontuacao])
async def identificar_obra_top3(item: TextoParaAnalisar):
    """
    Endpoint principal de busca (Modo Detetive Top-3)
    """
    if model is None or embeddings_matrix is None or ids_documentos is None:
        raise HTTPException(status_code=500, detail="Índice de busca semântico não está carregado. Execute 'processar_textos.py'.")

    texto_vetorizado = model.encode([item.texto])
    similaridades = cosine_similarity(texto_vetorizado, embeddings_matrix)
    indices_top_3 = np.argsort(similaridades[0])[:-4:-1]
    pontuacoes_top_3 = similaridades[0][indices_top_3]
    ids_livros_top_3 = [ids_documentos[i] for i in indices_top_3]

    resultados_finais = []
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        def formatar_livro(row):
            if not row: return None
            livro = dict(row)
            if livro.get("caminho_pdf"):
                livro["url_download"] = f"/{livro['caminho_pdf']}"
            else:
                livro["url_download"] = None
            return livro

        for i, id_livro in enumerate(ids_livros_top_3):
            cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
            livro_row = cursor.fetchone()
            
            if livro_row:
                resultado = {
                    "pontuacao": round(float(pontuacoes_top_3[i]), 4),
                    "obra": formatar_livro(livro_row)
                }
                resultados_finais.append(resultado)
        
        conn.close()
        
        return resultados_finais
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
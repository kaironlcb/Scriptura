# -*- coding: utf-8 -*-

import sqlite3
import joblib
import numpy as np
import spacy
import re
import string
import os
import shutil
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel, Field
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

# --- Modelos Pydantic (Estrutura de Dados) ---
class ObraBase(BaseModel):
    titulo: str
    autor: str
    ano_lancamento: int | None
    genero: str | None
    movimento_literario: str | None
    url_download: str | None

class ResultadoTrecho(BaseModel):
    pontuacao: float
    texto_encontrado: str 
    obra: ObraBase

class ObraTema(BaseModel):
    id: int
    titulo: str
    autor: str

class ResultadoTema(BaseModel):
    score_fusao_multiplicativa: float
    score_vetor_normalizado: float
    score_bm25_normalizado: float
    obra: ObraTema
    texto_chunk_encontrado: str

class TextoParaAnalisar(BaseModel):
    texto: str = Field(min_length=5) 

DB_PATH = 'literatura.db'
RE_CONTROLE_INVISIVEL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

print("Carregando modelo SentenceTransformer (MiniLM)...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Carregando modelo spaCy (pt_core_news_lg)...")
nlp_main = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
nlp_main.add_pipe('sentencizer')

print("Carregando 'Cérebro de Trecho' (index_TRECHO.pkl)...")
try:
    embeddings_matrix_TRECHO = joblib.load('embeddings_TRECHO.pkl')
    index_TRECHO = joblib.load('index_TRECHO.pkl')
    print(f"Cérebro de Trecho carregado. ({len(index_TRECHO)} frases)")
except FileNotFoundError:
    print("ERRO FATAL: Cérebro de Trecho (index_TRECHO.pkl) não encontrado.")
    print("           Execute 'processar_textos.py' primeiro.")
    embeddings_matrix_TRECHO = index_TRECHO = None
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR 'index_TRECHO.pkl': {e}")
    embeddings_matrix_TRECHO = index_TRECHO = None

print("Carregando 'Cérebro de Tema' (index_TEMA.pkl)...")
try:
    embeddings_matrix_TEMA = joblib.load('embeddings_TEMA.pkl')
    index_TEMA = joblib.load('index_TEMA.pkl')
    print(f"Cérebro de Tema carregado. ({len(index_TEMA)} chunks)")
except FileNotFoundError:
    print("ERRO FATAL: Cérebro de Tema (index_TEMA.pkl) não encontrado.")
    print("           Execute 'processar_temas.py' primeiro.")
    embeddings_matrix_TEMA = index_TEMA = None
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR 'index_TEMA.pkl': {e}")
    embeddings_matrix_TEMA = index_TEMA = None

bm25_TEMA = None
if index_TEMA:
    print("Construindo índice BM25 (Keywords) para Temas...")
    corpus_textos_tema = [item['texto'] for item in index_TEMA]
    tokenized_corpus_tema = [doc.lower().split(" ") for doc in corpus_textos_tema]
    bm25_TEMA = BM25Okapi(tokenized_corpus_tema)
    print("Índice BM25 construído com sucesso.")


app = FastAPI(
    title="Scriptura",
    version="1.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

def formatar_livro_saida(row):
    if not row: return None
    livro = dict(row)
    if livro.get("caminho_pdf"):
        livro["url_download"] = f"/{livro['caminho_pdf']}"
    else:
        livro["url_download"] = None
    return livro

def limpar_texto_busca(texto_sujo: str):
    texto_limpo = RE_CONTROLE_INVISIVEL.sub('', texto_sujo)
    texto_limpo = texto_limpo.lstrip(string.whitespace)
    texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo)
    doc_spacy = nlp_main(texto_limpo)
    frases_busca = [s.text.strip() for s in doc_spacy.sents if s.text.strip()]
    if not frases_busca:
        raise HTTPException(status_code=422, detail="Nenhuma frase válida encontrada na busca.")
    return frases_busca

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Scriptura!"}

@app.post("/upload-livro")
async def upload_livro(
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_lancamento: Optional[int] = Form(None),
    genero: Optional[str] = Form(None),
    movimento_literario: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é um .pdf.")
    
    nome_arquivo_seguro = re.sub(r"[^a-zA-Z0-9_\-.]", "_", titulo.lower().replace(" ", "_"))
    nome_pdf = f"{nome_arquivo_seguro}.pdf"
    nome_txt = f"{nome_arquivo_seguro}.txt"
    
    caminho_pdf_salvar = os.path.join("static", "pdfs", nome_pdf)
    caminho_txt_gerar = os.path.join("corpus", nome_txt)

    try:
        with open(caminho_pdf_salvar, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar o PDF: {e}")
    finally:
        file.file.close()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO livros (
                titulo, autor, ano_lancamento, genero, movimento_literario, 
                caminho_arquivo, caminho_pdf, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'EM_REVISAO')
            """,
            (titulo, autor, ano_lancamento, genero, movimento_literario, 
             caminho_txt_gerar, caminho_pdf_salvar)
        )
        conn.commit()
        novo_id = cursor.lastrowid
        conn.close()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"Um livro com este título/caminho já existe.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao salvar no banco de dados: {e}")

    return {
        "mensagem": "Livro recebido! Ele está na fila para revisão do Administrador.",
        "livro_id": novo_id,
        "titulo": titulo,
        "status": "EM_REVISAO"
    }


@app.post("/recomendar-por-tema", response_model=List[ResultadoTema])
async def recomendar_por_tema(item: TextoParaAnalisar):
    """
    Endpoint de Recomendação por tema.
    Retorna os 10 chunks mais relevantes usando um score
    híbrido MULTIPLICATIVO e EXPONENCIAL (Vetor^0.5 * BM25^2.0).
    """
    if embeddings_matrix_TEMA is None or bm25_TEMA is None:
        raise HTTPException(status_code=500, detail="Cérebro de Tema (Vetor ou BM25) não está carregado.")

    frases_busca = limpar_texto_busca(item.texto)
    query_texto = " ".join(frases_busca) 

    # --- Lógica Híbrida (v16.2) ---
    vetor_medio_busca = np.array([np.mean(model.encode(frases_busca), axis=0)])
    similaridades_vetor = cosine_similarity(vetor_medio_busca, embeddings_matrix_TEMA)[0]
    query_tokenizada = query_texto.lower().split(" ")
    similaridades_bm25 = bm25_TEMA.get_scores(query_tokenizada)
    epsilon = 1e-9 
    norm_vetor = (similaridades_vetor - np.min(similaridades_vetor)) / (np.max(similaridades_vetor) - np.min(similaridades_vetor) + epsilon)
    norm_bm25 = (similaridades_bm25 - np.min(similaridades_bm25)) / (np.max(similaridades_bm25) - np.min(similaridades_bm25) + epsilon)
    W_VETOR_EXP = 0.5
    W_BM25_EXP  = 2.0
    score_final_hibrido = (norm_vetor ** W_VETOR_EXP) * (norm_bm25 ** W_BM25_EXP)
    score_final_hibrido = np.nan_to_num(score_final_hibrido, nan=0.0, posinf=0.0, neginf=0.0)
    
    INDICES_PARA_ANALISAR = 10
    indices_top_10 = np.argsort(score_final_hibrido)[:- (INDICES_PARA_ANALISAR + 1) :-1]
    
    resultados_finais = []
    dados_dos_livros = {}

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for i in indices_top_10:
            item_index = index_TEMA[i]
            id_livro = item_index['id_livro']
            texto_chunk = item_index['texto']
            
            if id_livro not in dados_dos_livros:
                cursor.execute("SELECT id, titulo, autor FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()
                dados_dos_livros[id_livro] = dict(livro_row) if livro_row else None
            
            if dados_dos_livros[id_livro] is not None:
                resultado = {
                    "score_fusao_multiplicativa": round(float(score_final_hibrido[i]), 6),
                    "score_vetor_normalizado": round(float(norm_vetor[i]), 6),
                    "score_bm25_normalizado": round(float(norm_bm25[i]), 6),
                    "obra": dados_dos_livros[id_livro],
                    "texto_chunk_encontrado": texto_chunk
                }
                resultados_finais.append(resultado)

        conn.close()
        return resultados_finais
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")


@app.post("/encontrar-por-trecho", response_model=List[ResultadoTrecho])
async def encontrar_por_trecho(item: TextoParaAnalisar):
    if embeddings_matrix_TRECHO is None:
        raise HTTPException(status_code=500, detail="Cérebro de Trecho não está carregado.")
    frases_busca = limpar_texto_busca(item.texto)
    texto_busca_final = frases_busca[0]
    texto_vetorizado = model.encode([texto_busca_final])
    similaridades = cosine_similarity(texto_vetorizado, embeddings_matrix_TRECHO)[0]
    indices_top_5 = np.argsort(similaridades)[:-6:-1]
    resultados_finais = []
    ids_de_livros_ja_adicionados = set()
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        for i in indices_top_5:
            item_index = index_TRECHO[i]
            id_livro = item_index['id_livro']
            texto_encontrado = item_index['texto']
            if id_livro not in ids_de_livros_ja_adicionados:
                cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()
                if livro_row:
                    resultado = {
                        "pontuacao": round(float(similaridades[i]), 4),
                        "texto_encontrado": texto_encontrado,
                        "obra": formatar_livro_saida(livro_row)
                    }
                    resultados_finais.append(resultado)
                    ids_de_livros_ja_adicionados.add(id_livro)
            if len(resultados_finais) >= 3:
                break 
        conn.close()
        return resultados_finais
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
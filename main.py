# main.py (v13.0 - "Dois Cérebros")
#
# ATUALIZAÇÃO ESTRUTURAL:
# - Carrega OS DOIS "cérebros" (.pkl) na inicialização.
#
# ATUALIZAÇÃO ENDPOINTS:
# - /encontrar-por-trecho (v9): Usa o cérebro de FRASES (embeddings.pkl)
# - /recomendar-por-tema (v10): Usa o cérebro de CONTEXTO (embeddings_CONTEXTO.pkl)
#   e a lógica de AGREGAÇÃO (v10), que é a correta para chunks.

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
RE_CONTROLE_INVISIVEL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

# --- INÍCIO DA MUDANÇA (v13.0): Carregando os 2 Cérebros ---

# Modelos de IA (Carregados uma vez)
print("Carregando modelo SentenceTransformer (MiniLM)...")
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
print("Carregando modelo spaCy (pt_core_news_lg)...")
nlp_main = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
nlp_main.add_pipe('sentencizer')

# Cérebro 1: TRECHO (Frases únicas)
print("Carregando 'Cérebro de Trecho' (embeddings.pkl)...")
try:
    embeddings_matrix_TRECHO = joblib.load('embeddings.pkl')
    ids_documentos_TRECHO = joblib.load('ids_documentos.pkl')
    print("Cérebro de Trecho carregado com sucesso.")
except FileNotFoundError:
    print("ERRO FATAL: Cérebro de Trecho (embeddings.pkl) não encontrado.")
    print("Execute 'processar_textos.py' primeiro.")
    embeddings_matrix_TRECHO = ids_documentos_TRECHO = None
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR 'embeddings.pkl': {e}")
    embeddings_matrix_TRECHO = ids_documentos_TRECHO = None

# Cérebro 2: TEMA (Chunks de Contexto)
print("Carregando 'Cérebro de Tema' (embeddings_CONTEXTO.pkl)...")
try:
    embeddings_matrix_TEMA = joblib.load('embeddings_CONTEXTO.pkl')
    ids_documentos_TEMA = joblib.load('ids_documentos_CONTEXTO.pkl')
    print("Cérebro de Tema carregado com sucesso.")
except FileNotFoundError:
    print("ERRO FATAL: Cérebro de Tema (embeddings_CONTEXTO.pkl) não encontrado.")
    print("Execute 'processar_contexto.py' primeiro.")
    embeddings_matrix_TEMA = ids_documentos_TEMA = None
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR 'embeddings_CONTEXTO.pkl': {e}")
    embeddings_matrix_TEMA = ids_documentos_TEMA = None

# --- FIM DA MUDANÇA (v13.0) ---


# --- Inicia a aplicação FastAPI ---
app = FastAPI(
    title="Scriptura API (v13.0 - Dois Cérebros)",
    description="API com busca de Trecho (Cérebro 1) e Tema (Cérebro 2).",
    version="13.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Funções helper (sem alteração) ---
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

# --- Endpoints da API ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Scriptura (v13.0 - Dois Cérebros)!"}

# --- O "RECEPCIONISTA" (v9.0 - Sem alterações) ---
@app.post("/upload-livro")
async def upload_livro(
    titulo: str = Form(...),
    autor: str = Form(...),
    ano_lancamento: Optional[int] = Form(None),
    genero: Optional[str] = Form(None),
    movimento_literario: Optional[str] = Form(None),
    file: UploadFile = File(...)
):
    # ... (O código deste endpoint não mudou) ...
    # ... (Aviso: este upload só atualiza o cérebro de TRECHO, não o de TEMA) ...
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
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'PENDENTE')
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
        "mensagem": "Livro recebido com sucesso! Ele está na fila para processamento (no cérebro de trechos).",
        "livro_id": novo_id,
        "titulo": titulo,
        "status": "PENDENTE"
    }


# --- ENDPOINT 1: BUSCA POR TEMA (Lógica v10 - AGREGAÇÃO) ---
# --- USA O CÉREBRO DE TEMA (CONTEXTO) ---
@app.post("/recomendar-por-tema", response_model=List[ResultadoComPontuacao])
async def recomendar_por_tema(item: TextoParaAnalisar):
    """
    Endpoint de Recomendação por TEMA (v10 "Agregador").
    Usa o CÉREBRO DE CONTEXTO (embeddings_CONTEXTO.pkl).
    Usa Média de Vetores + Agregação de Scores.
    """
    if embeddings_matrix_TEMA is None:
        raise HTTPException(status_code=500, detail="Cérebro de Tema (Contexto) não está carregado.")

    frases_busca = limpar_texto_busca(item.texto)
        
    # 1. Média de Vetores da busca do usuário
    vetores_de_busca = model.encode(frases_busca)
    vetor_medio_busca = np.array([np.mean(vetores_de_busca, axis=0)])

    # 2. Busca no CÉREBRO DE TEMA
    similaridades = cosine_similarity(vetor_medio_busca, embeddings_matrix_TEMA)[0]
    
    # 3. Agregação de Scores (Lógica v10)
    INDICES_PARA_ANALISAR = 100
    PONTO_DE_CORTE_SCORE = 0.3 
    
    indices_top_100 = np.argsort(similaridades)[:- (INDICES_PARA_ANALISAR + 1) :-1]
    
    pontuacao_total_por_livro = {}
    dados_dos_livros = {} 
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for i in indices_top_100:
            pontuacao_frase = float(similaridades[i])
            if pontuacao_frase < PONTO_DE_CORTE_SCORE:
                continue
            
            # Usa o MAPA DE TEMA
            id_livro = int(ids_documentos_TEMA[i]) 
            
            if id_livro not in dados_dos_livros:
                cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()
                dados_dos_livros[id_livro] = formatar_livro_saida(livro_row) if livro_row else None
            
            if dados_dos_livros[id_livro] is not None:
                if id_livro not in pontuacao_total_por_livro:
                    pontuacao_total_por_livro[id_livro] = 0
                pontuacao_total_por_livro[id_livro] += pontuacao_frase

        conn.close()
        
        ids_ordenados = sorted(
            pontuacao_total_por_livro, 
            key=pontuacao_total_por_livro.get, 
            reverse=True
        )
        
        resultados_finais = []
        for id_livro in ids_ordenados[:3]: # Pega os Top 3 livros
            resultado = {
                "pontuacao": round(pontuacao_total_por_livro[id_livro], 4),
                "obra": dados_dos_livros[id_livro]
            }
            resultados_finais.append(resultado)
        return resultados_finais
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")


# --- ENDPOINT 2: BUSCA POR TRECHO (Lógica v9 - CITAÇÃO) ---
# --- USA O CÉREBRO DE TRECHO (FRASES) ---
@app.post("/encontrar-por-trecho", response_model=List[ResultadoComPontuacao])
async def encontrar_por_trecho(item: TextoParaAnalisar):
    """
    Endpoint de Recomendação por TRECHO (v9.0 "Citação").
    Usa o CÉREBRO DE FRASES (embeddings.pkl).
    Ideal para citações exatas.
    """
    if embeddings_matrix_TRECHO is None:
        raise HTTPException(status_code=500, detail="Cérebro de Trecho (Frases) não está carregado.")

    frases_busca = limpar_texto_busca(item.texto)
    
    texto_busca_final = frases_busca[0]
    
    texto_vetorizado = model.encode([texto_busca_final])
    
    # Busca no CÉREBRO DE TRECHO
    similaridades = cosine_similarity(texto_vetorizado, embeddings_matrix_TRECHO)[0]
    
    indices_top_20 = np.argsort(similaridades)[:-21:-1]
    
    resultados_finais = []
    ids_de_livros_ja_adicionados = set()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for i in indices_top_20:
            # Usa o MAPA DE TRECHO
            id_livro = int(ids_documentos_TRECHO[i]) 
            
            if id_livro not in ids_de_livros_ja_adicionados:
                cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()
                
                if livro_row:
                    resultado = {
                        "pontuacao": round(float(similaridades[i]), 4),
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
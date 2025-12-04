# main.py (v11.0 - "Busca Dupla")
# ADICIONADO: Endpoint /encontrar-por-trecho (lógica v9.0)
# MANTIDO: Endpoint /recomendar-por-tema (lógica v10.0)

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
    # Para /recomendar-por-tema, é o score agregado (pode ser > 1.0)
    # Para /encontrar-por-trecho, é o score da melhor frase (max 1.0)
    pontuacao: float 
    obra: ObraBase

class TextoParaAnalisar(BaseModel):
    texto: str = Field(min_length=15)

# --- Carregamento dos Modelos e Definições Globais ---
DB_PATH = 'literatura.db'
RE_CONTROLE_INVISIVEL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

print("Carregando o 'cérebro' semântico (Embeddings)...")
try:
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings_matrix = joblib.load('embeddings.pkl')
    ids_documentos = joblib.load('ids_documentos.pkl')
    print("Modelo e índice de busca carregados com sucesso.")
except FileNotFoundError:
    print("AVISO: Arquivos de índice (embeddings.pkl, etc.) não encontrados.")
    model = embeddings_matrix = ids_documentos = None
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR ÍNDICE: {e}")
    model = embeddings_matrix = ids_documentos = None

print("Carregando modelo spaCy (pt_core_news_lg) para o 'Ouvido'...")
try:
    nlp_main = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
    nlp_main.add_pipe('sentencizer')
    print("Modelo spaCy do 'Ouvido' carregado.")
except Exception as e:
    print(f"ERRO CRÍTICO AO CARREGAR spaCy: {e}")
    nlp_main = None

# --- Inicia a aplicação FastAPI ---
app = FastAPI(
    title="Scriptura API (v11.0 - Busca Dupla)",
    description="Uma API com endpoints separados para busca por Tema e por Trecho.",
    version="11.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Função helper para formatar a saída do livro ---
def formatar_livro_saida(row):
    """Converte uma linha do DB (sqlite3.Row) em um dict com url_download."""
    if not row: return None
    livro = dict(row)
    if livro.get("caminho_pdf"):
        livro["url_download"] = f"/{livro['caminho_pdf']}"
    else:
        livro["url_download"] = None
    return livro

# --- Função helper para limpeza de texto ---
def limpar_texto_busca(texto_sujo: str):
    """Limpa e sentenciza o texto de busca do usuário."""
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
    return {"message": "Bem-vindo à API Semântica do Scriptura! Use /recomendar-por-tema ou /encontrar-por-trecho."}

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
        "mensagem": "Livro recebido com sucesso! Ele está na fila para processamento.",
        "livro_id": novo_id,
        "titulo": titulo,
        "status": "PENDENTE"
    }
# --- FIM DO "RECEPCIONISTA" ---


# --- ENDPOINT 1: BUSCA POR TEMA (Lógica v10.0) ---
@app.post("/recomendar-por-tema", response_model=List[ResultadoComPontuacao])
async def recomendar_por_tema(item: TextoParaAnalisar):
    """
    Endpoint de Recomendação por TEMA (v10.0 "Agregador").
    Usa Média de Vetores + Agregação de Scores.
    Ideal para parágrafos descritivos.
    """
    if model is None or nlp_main is None or embeddings_matrix is None:
        raise HTTPException(status_code=500, detail="Índice de busca ou spaCy não está carregado.")

    frases_busca = limpar_texto_busca(item.texto)
        
    # --- MELHORIA 1: Média de Vetores ---
    vetores_de_busca = model.encode(frases_busca)
    vetor_medio_busca = np.array([np.mean(vetores_de_busca, axis=0)])

    similaridades = cosine_similarity(vetor_medio_busca, embeddings_matrix)[0]
    
    # --- MELHORIA 2: Agregação de Scores ---
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
            id_livro = int(ids_documentos[i])
            
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


# --- ENDPOINT 2: BUSCA POR TRECHO (Lógica v9.0) ---
@app.post("/encontrar-por-trecho", response_model=List[ResultadoComPontuacao])
async def encontrar_por_trecho(item: TextoParaAnalisar):
    """
    Endpoint de Recomendação por TRECHO (v9.0 "Citação").
    Usa apenas o vetor da PRIMEIRA FRASE.
    Retorna os livros que contêm as frases mais parecidas.
    Ideal para citações exatas.
    """
    if model is None or nlp_main is None or embeddings_matrix is None:
        raise HTTPException(status_code=500, detail="Índice de busca ou spaCy não está carregado.")

    frases_busca = limpar_texto_busca(item.texto)
    
    # --- Lógica v9.0: Pega apenas a primeira frase ---
    texto_busca_final = frases_busca[0]
    
    texto_vetorizado = model.encode([texto_busca_final])
    similaridades = cosine_similarity(texto_vetorizado, embeddings_matrix)[0]
    
    # Pega as 20 frases mais parecidas
    indices_top_20 = np.argsort(similaridades)[:-21:-1]
    
    resultados_finais = []
    ids_de_livros_ja_adicionados = set()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        for i in indices_top_20:
            id_livro = int(ids_documentos[i])
            
            # Pega os 3 primeiros livros ÚNICOS
            if id_livro not in ids_de_livros_ja_adicionados:
                cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()
                
                if livro_row:
                    resultado = {
                        # A pontuação é o score daquela ÚNICA frase
                        "pontuacao": round(float(similaridades[i]), 4),
                        "obra": formatar_livro_saida(livro_row)
                    }
                    resultados_finais.append(resultado)
                    ids_de_livros_ja_adicionados.add(id_livro)
            
            if len(resultados_finais) >= 3:
                break # Para quando tivermos 3 livros
        
        conn.close()
        return resultados_finais
        
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
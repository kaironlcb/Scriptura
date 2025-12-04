# main.py (v8.0 - "Fatiador de Busca")
import sqlite3
import joblib
import numpy as np
import spacy # <-- IMPORTANTE: spaCy agora no main.py
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

# --- CARREGA O spaCy PARA O "OUVIDO" ---
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
    title="Scriptura API (v8.0 - Fatiador de Busca)",
    description="Uma API para Análise Semântica e Recomendação por Tema.",
    version="8.0.0",
)
app.mount("/static", StaticFiles(directory="static"), name="static")

# --- Endpoints da API ---
@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API Semântica do Scriptura!"}

@app.post("/recomendar-por-tema", response_model=List[ResultadoComPontuacao])
async def recomendar_por_tema(item: TextoParaAnalisar):
    if model is None or nlp_main is None or embeddings_matrix is None:
        raise HTTPException(status_code=500, detail="Índice de busca ou spaCy não está carregado.")

    # --- MUDANÇA v8.0: "FATIAMOS A BUSCA" ---
    texto_busca_sujo = item.texto
    texto_limpo = RE_CONTROLE_INVISIVEL.sub('', texto_busca_sujo)
    texto_limpo = texto_limpo.lstrip(string.whitespace)
    texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo)

    doc_spacy = nlp_main(texto_limpo)
    frases_busca = [s.text.strip() for s in doc_spacy.sents if s.text.strip()]

    if not frases_busca:
        raise HTTPException(status_code=422, detail="Nenhuma frase válida encontrada na busca.")

    # 4. Pegar SÓ A PRIMEIRA FRASE da busca
    texto_busca_final = frases_busca[0]
    # --- FIM DA MUDANÇA ---

    texto_vetorizado = model.encode([texto_busca_final])
    similaridades = cosine_similarity(texto_vetorizado, embeddings_matrix)[0]

    indices_top_20 = np.argsort(similaridades)[:-21:-1]

    resultados_finais = []
    ids_de_livros_ja_adicionados = set()

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        def formatar_livro(row):
            if not row: return None
            livro = dict(row)
            if livro.get("caminho_pdf"):
                livro["url_download"] = f"/{livMro['caminho_pdf']}"
            else:
                livro["url_download"] = None
            return livro

        for i in indices_top_20:
            id_livro = int(ids_documentos[i])

            if id_livro not in ids_de_livros_ja_adicionados:
                cursor.execute("SELECT * FROM livros WHERE id = ?", (id_livro,))
                livro_row = cursor.fetchone()

                if livro_row:
                    resultado = {
                        "pontuacao": round(float(similaridades[i]), 4),
                        "obra": formatar_livro(livro_row)
                    }
                    resultados_finais.append(resultado)
                    ids_de_livros_ja_adicionados.add(id_livro)

            if len(resultados_finais) >= 3:
                break

        conn.close()
        return resultados_finais

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Erro no banco de dados: {e}")
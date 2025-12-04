# -*- coding: utf-8 -*-

import sqlite3
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
import re 
import string
import math
import os

DB_PATH = 'literatura.db'

JUNK_KEYWORDS = [
    '(cid:', 'www.', 'http:', 'https:', '.br', '.com', '.org', '.pdf',
    'bibvirt', 'ciberfil', 'hpg.ig.com.br', 'nead', 'unama',
    'adobe acrobat', 'e-mail:', 'email:', 'digitalizado por:',
    'isbn:', 'cep:', 'alcindo cacela', 'série bom livro', 'usp.br',
    'ministério da cultura', 'biblioteca nacional', 'departamento nacional do livro'
]

RE_CONTROLE_INVISIVEL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

MANUAL_BATCH_SIZE = 512
MAX_CHUNK_LENGTH = 10000 
MIN_CHUNK_LENGTH = 10   

NLP = None
MODEL = None

def carregar_modelos_globais():
    global NLP, MODEL
    if NLP is None:
        print("Carregando modelo spaCy (pt_core_news_lg)...")
        try:
            NLP = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
            NLP.max_length = 5000000
            NLP.add_pipe('sentencizer')
        except OSError:
            print("ERRO: Modelo 'pt_core_news_lg' do spaCy não encontrado.")
            return False
    
    if MODEL is None:
        print("Carregando modelo SentenceTransformer (MiniLM)...")
        MODEL = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    print("Modelos carregados com sucesso.")
    return True

def fatiar_e_filtrar_livro_granular(livro_id, caminho_arquivo, titulo):
    print(f"  Processando (Trecho): {titulo} (ID: {livro_id})")
    
    index_data_livro = []
    chunks_descartados_lixo = 0
    chunks_descartados_veneno = 0
    chunks_descartados_curtos = 0

    texto_original = ""
    try:
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                texto_original = f.read()
        except UnicodeDecodeError:
            print(f"    AVISO: Falha no UTF-8. Tentando como 'latin-1'...")
            with open(caminho_arquivo, 'r', encoding='latin-1') as f:
                texto_original = f.read()
        
        texto_limpo = RE_CONTROLE_INVISIVEL.sub('', texto_original)
        texto_limpo = texto_limpo.lstrip(string.whitespace + '\x0c')
        
        texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo) 
        
        doc_spacy = NLP(texto_limpo)

        frases = [re.sub(r'\s+', ' ', s.text).strip() for s in doc_spacy.sents if s.text.strip()]
        
        if not frases:
            print(f"    Aviso: Livro '{titulo}' é muito curto, pulando.")
            return [], 0, 0, 0

        for chunk_texto_original in frases:
            
            if len(chunk_texto_original) > MAX_CHUNK_LENGTH:
                chunks_descartados_veneno += 1
                continue
            if len(chunk_texto_original) < MIN_CHUNK_LENGTH:
                chunks_descartados_curtos += 1
                continue

            chunk_texto_lower = chunk_texto_original.lower()
            is_junk = any(keyword.lower() in chunk_texto_lower for keyword in JUNK_KEYWORDS)
            
            if is_junk:
                chunks_descartados_lixo += 1
            else:
                index_data_livro.append({
                    'id_livro': livro_id,
                    'texto': chunk_texto_original
                })

    except FileNotFoundError:
        print(f"    AVISO: Arquivo '{caminho_arquivo}' não foi encontrado. Pulando.")
    except Exception as e:
        print(f"    ERRO: Falha ao processar '{caminho_arquivo}': {e}. Pulando.")
    
    return index_data_livro, 0, chunks_descartados_lixo, chunks_descartados_veneno, chunks_descartados_curtos

def gerar_embeddings_em_lotes(chunks_de_texto_puro):
    print(f"\nGerando vetores semânticos para {len(chunks_de_texto_puro)} frases em batches...")
    all_embeddings = []
    total_batches = math.ceil(len(chunks_de_texto_puro) / MANUAL_BATCH_SIZE)
    for i in range(0, len(chunks_de_texto_puro), MANUAL_BATCH_SIZE):
        batch_num = (i // MANUAL_BATCH_SIZE) + 1
        print(f"  Processando lote {batch_num}/{total_batches}...")
        batch_chunks = chunks_de_texto_puro[i : i + MANUAL_BATCH_SIZE]
        try:
            batch_embeddings = MODEL.encode(batch_chunks, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
        except Exception as e:
            print(f"    ERRO: Falha ao processar o lote {batch_num}: {e}")
    print("\nProcessamento de lotes concluído. Juntando os resultados...")
    return np.vstack(all_embeddings)

def rodar_build_limpo_completo():
    if not carregar_modelos_globais():
        return
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT id, caminho_arquivo, titulo FROM livros WHERE status = 'PROCESSADO'")
        livros = cursor.fetchall()
        conn.close()
        if not livros:
            print(f"ERRO: O banco de dados '{DB_PATH}' está vazio. Execute 'scripts_db.py' primeiro.")
            return
    except sqlite3.Error as e:
        print(f"ERRO: Banco de dados '{DB_PATH}' não encontrado. Execute 'scripts_db.py' primeiro.")
        return

    all_index_data = []
    total_lixo = 0
    total_veneno = 0
    total_curtos = 0
    print(f"\nIniciando fatiamento e filtragem de {len(livros)} trechos das obras...")

    for livro_id, caminho_arquivo, titulo in livros:
        index_data_livro, _, lixo, veneno, curtos = fatiar_e_filtrar_livro_granular(livro_id, caminho_arquivo, titulo)
        all_index_data.extend(index_data_livro)
        total_lixo += lixo
        total_veneno += veneno
        total_curtos += curtos
    
    if not all_index_data:
        print("\nERRO FATAL: Nenhum chunk puro foi gerado.")
        return

    print(f"\nFiltro de Trecho concluído:")
    print(f"  {len(all_index_data)} chunks puros retidos.")
    print(f"  {total_lixo} chunks de lixo descartados.")
    print(f"  {total_veneno} chunks muito longos descartados.")
    print(f"  {total_curtos} chunks curtos descartados.")
    
    chunks_para_vetorizar = [item['texto'] for item in all_index_data]
    embeddings = gerar_embeddings_em_lotes(chunks_para_vetorizar)

    print("\nSalvando os novos arquivos de índice de trecho...")
    joblib.dump(embeddings, 'embeddings_TRECHO.pkl')
    joblib.dump(all_index_data, 'index_TRECHO.pkl')
    
    print("\n--- Processamento de trecho concluído! ---")

if __name__ == '__main__':
    print("Limpando arquivos de índice antigos/novos...")
    for f in [
        'embeddings.pkl', 'ids_documentos.pkl',
        'embeddings_TRECHO.pkl', 'index_TRECHO.pkl'
    ]:
        if os.path.exists(f):
            os.remove(f)
    
    rodar_build_limpo_completo()
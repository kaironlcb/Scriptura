# processar_textos.py (v7.0 - "Granular" - A Solução do Zé)
import sqlite3
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
import re
import string
import math

DB_PATH = 'literatura.db'

# --- A "LISTA NEGRA" (FILTRO SANITÁRIO) ---
# Usamos ela para *identificar* um chunk poluído
JUNK_KEYWORDS = [
    '(cid:', # O "veneno" que trava o modelo
    'www.', 'http:', 'https:', '.br', '.com', '.org', '.pdf',
    'bibvirt', 'ciberfil', 'hpg.ig.com.br', 'nead', 'unama',
    'adobe acrobat', 'e-mail:', 'email:', 'digitalizado por:',
    'isbn:', 'cep:', 'alcindo cacela', 'série bom livro', 'usp.br',
    'ministério da cultura', 'biblioteca nacional', 'departamento nacional do livro'
]

# --- O "EXTERMINADOR" (v6.1) ---
RE_CONTROLE_INVISIVEL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]')

MANUAL_BATCH_SIZE = 512
MAX_CHUNK_LENGTH = 10000 # Filtro de veneno (chunks gigantes)
MIN_CHUNK_LENGTH = 10     # NOVO: Descarta frases inúteis (ex: "Sim.")

def processar_e_salvar_chunks_semanticos():
    """
    Versão 7.0: O "Granular" (A Solução do Zé).
    Usa CHUNK_SIZE = 1 (cada frase é um documento).
    Remove toda a lógica de "Bisturi" (MARCADORES_INICIO)
    e confia 100% no "Filtro Sanitário" (JUNK_KEYWORDS).
    """
    print("--- Iniciando processamento semântico v7.0 (Granular) ---")

    # 1. Carregar os Modelos
    print("Carregando modelo spaCy (pt_core_news_lg)...")
    try:
        nlp = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
        nlp.max_length = 5000000
        nlp.add_pipe('sentencizer')
    except OSError:
        print("ERRO: Modelo 'pt_core_news_lg' do spaCy não encontrado.")
        return
    
    print("Carregando modelo SentenceTransformer (MiniLM)...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # 2. Buscar Livros no DB
    print(f"Lendo banco de dados: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, caminho_arquivo, titulo FROM livros')
        livros = cursor.fetchall()
        conn.close()
        if not livros:
            print(f"ERRO: O banco de dados '{DB_PATH}' está vazio. Execute 'scripts_db.py' PRIMEIRO.")
            return
    except sqlite3.Error as e:
        print(f"ERRO: Banco de dados '{DB_PATH}' não encontrado. Execute 'scripts_db.py' PRIMEIRO.")
        return

    chunks_de_texto_puro = []
    ids_dos_chunks_puros = []
    chunks_descartados_lixo = 0
    chunks_descartados_veneno = 0
    chunks_descartados_curtos = 0

    print(f"\nIniciando fatiamento e filtragem de {len(livros)} obras...")

    # 3. Fatiar e Filtrar/Limpar...
    for livro_id, caminho_arquivo, titulo in livros:
        print(f"  Processando: {titulo} (ID: {livro_id})")
        texto_original = ""
        try:
            try:
                with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                    texto_original = f.read()
            except UnicodeDecodeError:
                print(f"    AVISO: Falha no UTF-8 (byte 0xc3?). Tentando como 'latin-1'...")
                with open(caminho_arquivo, 'r', encoding='latin-1') as f:
                    texto_original = f.read()
            
            # --- O "EXTERMINADOR" v6.1 ---
            texto_limpo = RE_CONTROLE_INVISIVEL.sub('', texto_original)
            
            # --- LÓGICA DO BISTURI (MARCADORES_INICIO) REMOVIDA ---

            texto_limpo = texto_limpo.lstrip(string.whitespace + '\x0c')
            texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo)
            
            doc_spacy = nlp(texto_limpo)
            
            # --- CHUNK_SIZE = 1 (A SOLUÇÃO DO ZÉ) ---
            frases = [s.text.strip() for s in doc_spacy.sents if s.text.strip()]
            
            if not frases:
                print(f"    Aviso: Livro '{titulo}' é muito curto, pulando.")
                continue

            for chunk_texto_original in frases:
                # Agora, "chunk_texto_original" é SÓ 1 FRASE
                
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
                    chunks_de_texto_puro.append(chunk_texto_original)
                    ids_dos_chunks_puros.append(livro_id)
            # --- FIM DA LÓGICA v7.0 ---

        except FileNotFoundError:
            print(f"    AVISO: Arquivo '{caminho_arquivo}' não foi encontrado. Pulando.")
        except Exception as e:
            print(f"    ERRO: Falha ao processar '{caminho_arquivo}': {e}. Pulando.")
    
    if not chunks_de_texto_puro:
        print("\nERRO FATAL: Nenhum chunk puro foi gerado.")
        return

    print(f"\nFiltro concluído:")
    print(f"  {len(chunks_de_texto_puro)} chunks puros retidos (frases).")
    print(f"  {chunks_descartados_lixo} chunks de lixo (lista negra) descartados.")
    print(f"  {chunks_descartados_veneno} chunks venenosos (muito longos) descartados.")
    print(f"  {chunks_descartados_curtos} chunks curtos (ex: 'Sim.') descartados.")
    
    # 4. Gerar os Embeddings (COM BATCH MANUAL)
    print("\nGerando os vetores semânticos (Embeddings) em lotes controlados...")
    
    all_embeddings = []
    total_batches = math.ceil(len(chunks_de_texto_puro) / MANUAL_BATCH_SIZE)

    for i in range(0, len(chunks_de_texto_puro), MANUAL_BATCH_SIZE):
        batch_num = (i // MANUAL_BATCH_SIZE) + 1
        print(f"  Processando lote {batch_num}/{total_batches}...")
        
        batch_chunks = chunks_de_texto_puro[i : i + MANUAL_BATCH_SIZE]
        
        try:
            batch_embeddings = model.encode(batch_chunks, show_progress_bar=False)
            all_embeddings.append(batch_embeddings)
        except Exception as e:
            print(f"    ERRO: Falha ao processar o lote {batch_num}. Pulando este lote.")
            print(f"    Detalhe do erro: {e}")
            num_chunks_no_lote_atual = len(batch_chunks)
            dimensao_modelo = 384
            all_embeddings.append(np.zeros((num_chunks_no_lote_atual, dimensao_modelo)))

    print("\nProcessamento de lotes concluído. Juntando os resultados...")
    embeddings = np.vstack(all_embeddings)

    # 5. Salvar os resultados
    print("\nSalvando os novos arquivos de índice (embeddings.pkl, ids_documentos.pkl)...")
    joblib.dump(embeddings, 'embeddings.pkl')
    joblib.dump(np.array(ids_dos_chunks_puros), 'ids_documentos.pkl')
    
    print("\n--- Processamento (v7.0) concluído! ---")

if __name__ == '__main__':
    processar_e_salvar_chunks_semanticos()
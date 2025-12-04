# processar_textos.py
import sqlite3
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer
import spacy
import re
import string # Vamos usar para a limpeza pesada

DB_PATH = 'literatura.db'

# --- NOSSAS NOVAS REGRAS DE CHUNKING (GOLD STANDARD) ---
CHUNK_SIZE = 3      # Agrupar de 3 em 3 frases
CHUNK_OVERLAP = 2   # Sobrepor 2 frases (ex: [1,2,3], [2,3,4], [3,4,5])
# Isso significa que o "passo" (STEP_SIZE) é 1
STEP_SIZE = CHUNK_SIZE - CHUNK_OVERLAP

def processar_e_salvar_chunks_semanticos():
    """
    Versão 3.3: Limpeza pesada e chunking "gold standard" (step 1)
    para garantir que NENHUMA frase seja pulada.
    """
    print("--- Iniciando processamento semântico v3.3 (Build Final) ---")

    # 1. Carregar os Modelos
    print("Carregando modelo spaCy (pt_core_news_lg) para fatiar frases...")
    try:
        nlp = spacy.load('pt_core_news_lg', disable=['parser', 'ner', 'tagger'])
        nlp.max_length = 5000000
        nlp.add_pipe('sentencizer')
    except OSError:
        print("ERRO: Modelo 'pt_core_news_lg' do spaCy não encontrado.")
        print("Execute: python -m spacy download pt_core_news_lg")
        return
    
    print("Carregando modelo SentenceTransformer (MiniLM) para gerar embeddings...")
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

    # 2. Buscar Livros no DB
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT id, caminho_arquivo, titulo FROM livros')
        livros = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"ERRO: Banco de dados '{DB_PATH}' não encontrado. Execute 'scripts_db.py'.")
        return

    chunks_de_texto = []
    ids_dos_chunks = []

    print(f"\nIniciando fatiamento (chunking) de {len(livros)} obras...")

    # Define os caracteres de "lixo" (espaços em branco, tabs, newlines, etc.)
    whitespace_chars = string.whitespace + '\x0c' # \x0c é o "form feed" comum de PDFs

    for livro_id, caminho_arquivo, titulo in livros:
        print(f"  Processando: {titulo}")
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                texto_original = f.read()
            
            # --- LIMPEZA PESADA v3.3 ---
            # 1. Remove qualquer "lixo" de controle/espaço no início do arquivo
            texto_limpo = texto_original.lstrip(whitespace_chars)
            # 2. Substitui quebras de linha múltiplas por uma só (para spaCy)
            texto_limpo = re.sub(r'(\n|\s){2,}', ' \n', texto_limpo)
            # --- FIM DA LIMPEZA ---
            
            # 3. FATIAR EM FRASES
            doc_spacy = nlp(texto_limpo)
            frases = [s.text.strip() for s in doc_spacy.sents if s.text.strip()]
            
            if len(frases) < CHUNK_SIZE:
                print(f"    Aviso: Livro '{titulo}' é muito curto, pulando.")
                continue

            # 4. CRIAR OS CHUNKS SOBREPOSTOS (STEP_SIZE = 1)
            for i in range(0, len(frases) - CHUNK_SIZE + 1, STEP_SIZE):
                chunk_frases = frases[i : i + CHUNK_SIZE]
                chunk_texto = " ".join(chunk_frases)
                chunks_de_texto.append(chunk_texto)
                ids_dos_chunks.append(livro_id)

        except FileNotFoundError:
            print(f"    AVISO: Arquivo '{caminho_arquivo}' não foi encontrado. Pulando.")
        except Exception as e:
            print(f"    ERRO: Falha ao processar '{caminho_arquivo}': {e}. Pulando.")
    
    if not chunks_de_texto:
        print("\nERRO FATAL: Nenhum chunk foi gerado. Verifique a pasta 'corpus/'.")
        return

    print(f"\nTotal de {len(chunks_de_texto)} chunks semânticos sobrepostos foram criados.")
    
    # 5. Gerar os Embeddings
    print("Gerando os vetores semânticos (Embeddings) para todos os chunks...")
    print("AVISO: Isso vai demorar...")
    
    embeddings = model.encode(chunks_de_texto, show_progress_bar=True)

    # 6. Salvar os resultados
    print("\nSalvando os novos arquivos de índice (embeddings.pkl, ids_documentos.pkl)...")
    joblib.dump(embeddings, 'embeddings.pkl')
    joblib.dump(ids_dos_chunks, 'ids_documentos.pkl')
    
    print("\n--- Processamento (Chunking v3.3) concluído! Agora é pra valer. ---")

if __name__ == '__main__':
    processar_e_salvar_chunks_semanticos()
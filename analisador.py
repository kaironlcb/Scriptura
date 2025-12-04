# analisador.py (v1.1 - O "Trabalhador Granular")
import sqlite3
import joblib
import numpy as np
import time
import os

# Importa as FUNÇÕES CORRETAS (v8.0 - "Granular")
from auto_converter import converter_pdf_para_txt_limpo
from processar_textos import carregar_modelos_globais, fatiar_e_filtrar_livro_granular, gerar_embeddings_em_lotes

DB_PATH = 'literatura.db'
EMBEDDINGS_PATH = 'embeddings.pkl'
IDS_PATH = 'ids_documentos.pkl'

def processar_livros_pendentes():
    """
    Verifica o DB por livros "PENDENTE" e os processa
    em modo de "Indexação Incremental" (GRANULAR).
    """
    print("\n[Analisador] Verificando se há novos livros...")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 1. Busca por livros pendentes
    cursor.execute("SELECT * FROM livros WHERE status = 'PENDENTE'")
    livros_pendentes = cursor.fetchall()
    
    if not livros_pendentes:
        print("[Analisador] Nenhum livro novo. Dormindo por 10s.")
        conn.close()
        return

    print(f"[Analisador] ACHADOS {len(livros_pendentes)} LIVROS NOVOS. Iniciando processamento...")
    
    # 2. Carrega os "cérebros" (spaCy e MiniLM)
    if not carregar_modelos_globais():
        print("[Analisador] ERRO FATAL: Não foi possível carregar os modelos de IA.")
        conn.close()
        return

    # 3. Carrega o "cérebro" (.pkl) antigo
    print("[Analisador] Carregando índice antigo (embeddings.pkl)...")
    try:
        embeddings_antigos = joblib.load(EMBEDDINGS_PATH)
        ids_antigos = joblib.load(IDS_PATH)
    except Exception as e:
        print(f"[Analisador] ERRO: Não foi possível carregar os arquivos .pkl! {e}")
        print("           O 'Build Limpo' (processar_textos.py) precisa ser rodado primeiro.")
        conn.close()
        return

    novos_chunks_para_adicionar = []
    novos_ids_para_adicionar = []
    ids_livros_processados = []

    # 4. Loop de Processamento (Livro por Livro)
    for livro in livros_pendentes:
        print(f"\n[Analisador] Processando Livro ID: {livro['id']} ({livro['titulo']})")
        
        # 4a. Converter PDF -> TXT
        if not converter_pdf_para_txt_limpo(livro['caminho_pdf'], livro['caminho_arquivo']):
            print(f"  ERRO: Falha ao converter PDF. Pulando este livro.")
            cursor.execute("UPDATE livros SET status = 'FALHA_CONVERSAO' WHERE id = ?", (livro['id'],))
            conn.commit()
            continue
            
        # 4b. Fatiar e Filtrar o .txt (USANDO A LÓGICA GRANULAR CORRETA)
        chunks, ids, _, lixo, veneno, curtos = fatiar_e_filtrar_livro_granular(livro['id'], livro['caminho_arquivo'], livro['titulo'])
        
        if not chunks:
            print(f"  AVISO: Nenhum chunk puro gerado para este livro. Pulando.")
            cursor.execute("UPDATE livros SET status = 'FALHA_PROCESSAMENTO' WHERE id = ?", (livro['id'],))
            conn.commit()
            continue

        print(f"  -> {len(chunks)} frases puras encontradas para {livro['titulo']}.")
        novos_chunks_para_adicionar.extend(chunks)
        novos_ids_para_adicionar.extend(ids)
        ids_livros_processados.append(livro['id'])

    # 5. Indexação Incremental (A Mágica)
    if not novos_chunks_para_adicionar:
        print("[Analisador] Nenhum chunk novo gerado. Processamento concluído.")
        conn.close()
        return

    print(f"\n[Analisador] Gerando embeddings para as {len(novos_chunks_para_adicionar)} frases novas...")
    embeddings_novos = gerar_embeddings_em_lotes(novos_chunks_para_adicionar)
    
    embeddings_finais = np.vstack([embeddings_antigos, embeddings_novos])
    ids_finais = np.hstack([ids_antigos, np.array(novos_ids_para_adicionar)])
    
    print("[Analisador] Salvando o novo índice (embeddings.pkl) atualizado...")
    joblib.dump(embeddings_finais, EMBEDDINGS_PATH)
    joblib.dump(ids_finais, IDS_PATH)
    
    # 6. Atualizar o Status no DB
    for livro_id in ids_livros_processados:
        cursor.execute("UPDATE livros SET status = 'PROCESSADO' WHERE id = ?", (livro['id'],))
    conn.commit()
    
    conn.close()
    print(f"\n[Analisador] SUCESSO! {len(ids_livros_processados)} livros novos foram adicionados ao 'cérebro'.")

if __name__ == '__main__':
    print("--- Iniciando o 'Analisador Granular' do Scriptura (v1.1) ---")
    print("Pressione Ctrl+C para parar.")
    while True:
        try:
            processar_livros_pendentes()
            time.sleep(10)
        except KeyboardInterrupt:
            print("\n[Analisador] Desligando...")
            break
        except Exception as e:
            print(f"[Analisador] ERRO INESPERADO: {e}")
            print("           Reiniciando em 30 segundos...")
            time.sleep(30)  
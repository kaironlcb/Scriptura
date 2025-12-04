# -*- coding: utf-8 -*-
# verificar_indices.py (v1.2 - Sintaxe Corrigida)
import sqlite3
import joblib
import os
import numpy as np

DB_NAME = 'literatura.db'
IDS_PKL = 'ids_documentos.pkl'
EMB_PKL = 'embeddings.pkl'

print("--- Auditoria Final de Sincronia (v4.2 vs v3.9) ---")

db_ids = set()
db_status_ok = False

# --- Verificação do DB (O "Mapa") ---
try:
    if not os.path.exists(DB_NAME):
        print(f"\n[VEREDITO DB]: ERRO FATAL! O arquivo '{DB_NAME}' NÃO EXISTE.")
        print("                 Rode 'scripts_db.py' (v4.2 - 46 livros) primeiro.")
        exit()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='livros';")
    if not cursor.fetchone():
        print(f"\n[VEREDITO DB]: ERRO FATAL! O .db existe, mas a tabela 'livros' NÃO FOI CRIADA.")
        conn.close()
        exit()

    cursor.execute("SELECT id FROM livros;")
    db_ids = set(row[0] for row in cursor.fetchall())
    total_livros = len(db_ids)
    conn.close()

    if total_livros == 0:
        print(f"\n[VEREDITO DB]: ERRO! O banco '{DB_NAME}' ESTÁ VAZIO (0 livros).")
        print("               Rode 'scripts_db.py' (v4.2) novamente.")
    elif total_livros == 46:
        print(f"\n[VEREDITO DB]: O BANCO DE DADOS ESTÁ PERFEITO! (Contém {total_livros} livros).")
        db_status_ok = True
    else:
        print(f"\n[VEREDITO DB]: DESSINCRONIZADO! O banco '{DB_NAME}' contém {total_livros} livros (esperava 46).")
        db_status_ok = True # Está dessincronizado, mas não é fatal

except sqlite3.Error as e:
    print(f"\n[VEREDITO DB]: ERRO AO LER O DB! {e}")
    exit()


# --- Verificação do Cérebro (.pkl) ---
pkl_ids = set()
pkl_status_ok = False

try:
    if not os.path.exists(IDS_PKL) or not os.path.exists(EMB_PKL):
        print("\n[ERRO CÉREBRO]: Os arquivos 'embeddings.pkl' e/ou 'ids_documentos.pkl' NÃO EXISTEM.")
        print("                 Rode o 'processar_textos.py' (v3.10) para criá-los.")
        exit()

    print("\nCarregando arquivos .pkl (o 'cérebro')...")
    ids_do_cerebro = joblib.load(IDS_PKL)
    if not isinstance(ids_do_cerebro, np.ndarray):
        ids_do_cerebro = np.array(ids_do_cerebro)
    
    pkl_ids = set(np.unique(ids_do_cerebro))
    print(f"[CÉREBRO OK]: 'ids_documentos.pkl' carregado. Contém {len(pkl_ids)} IDs de livros únicos.")
    pkl_status_ok = True

except Exception as e:
    print(f"\n[ERRO CÉREBRO]: Falha ao ler os arquivos .pkl! {e}")
    print("                Eles podem estar corrompidos. Delete-os e rode 'processar_textos.py'.")
    exit()

# --- A Comparação Final (O Veredito) ---
if db_status_ok and pkl_status_ok:
    print("\n--- VEREDITO DA SINCRONIZAÇÃO ---")

    if db_ids == pkl_ids:
        print("[SUCESSO!]: O 'cérebro' (.pkl) e o 'mapa' (.db) estão PERFEITAMENTE SINCRONIZADOS.")
        print(f"           Ambos usam os mesmos {len(db_ids)} IDs.")
        print("           Se a busca ainda dá '[]', o 'Filtro Sanitário' está agressivo demais.")
    else:
        print("[ERRO DE DESSINCRONIZAÇÃO!]: O 'cérebro' e o 'mapa' NÃO BATEM.")
        print(f"    IDs que estão no MAPA (.db) mas NÃO no CÉREBRO (.pkl): {sorted(list(db_ids - pkl_ids))}")
        print(f"    IDs que estão no CÉREBRO (.pkl) mas NÃO no MAPA (.db): {sorted(list(pkl_ids - db_ids))}")
        print("\n    CAUSA: O 'processar_textos.py' falhou ou foi rodado com um DB antigo.")
        print("    SOLUÇÃO: Siga o 'Build Limpo' (apague DB e PKLs, rode scripts_db.py, DEPOIS processar_textos.py).")
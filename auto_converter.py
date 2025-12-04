import pdfplumber
import os
import re
import string
import sqlite3 

DB_PATH = 'literatura.db' 

MARCADORES_INICIO = re.compile(
    r'\b(CAPÍTULO\s+(I|1)|CANTO\s+(I|1)|ATO\s+(I|1)|PARTE\s+(I|1)|LIVRO\s+(I|1)|INTRODUÇÃO|PRIMEIRA\s+PARTE)\b',
    re.IGNORECASE
)

def converter_pdf_para_txt_limpo(caminho_pdf_completo, caminho_txt_completo):
    if os.path.exists(caminho_txt_completo):
        print(f"  AVISO (converter): O arquivo .txt '{caminho_txt_completo}' já existe. Pulando conversão.")
        return True 

    print(f"  [CONVERTENDO]: {caminho_pdf_completo}")
    
    texto_completo_original = ""
    try:
        with pdfplumber.open(caminho_pdf_completo) as pdf:
            for i, pagina in enumerate(pdf.pages):
                texto_pagina = pagina.extract_text(x_tolerance=1, y_tolerance=1)
                if texto_pagina:
                    texto_completo_original += texto_pagina + "\n"
        
        match = MARCADORES_INICIO.search(texto_completo_original)
        texto_para_salvar = ""
        
        if match:
            start_index = match.end() 
            texto_para_salvar = texto_completo_original[start_index:]
            texto_para_salvar = texto_para_salvar.lstrip(string.whitespace + '-\n')
            print(f"    -> Marcador de início encontrado! Lixo da capa removido.")
        else:
            texto_para_salvar = texto_completo_original
            print(f"    -> Marcador não encontrado. Salvando o texto inteiro.")
        
        with open(caminho_txt_completo, 'w', encoding='utf-8') as f:
            f.write(texto_para_salvar)
        
        print(f"  [SUCESSO] -> Salvo em '{caminho_txt_completo}'")
        return True

    except Exception as e:
        print(f"  [ERRO] -> Não foi possível processar o arquivo {caminho_pdf_completo}.")
        print(f"          Motivo: {e}")
        return False

def rodar_build_limpo_completo():
    PASTA_PDFS = 'static/pdfs/'
    PASTA_CORPUS = 'corpus/'

    os.makedirs(PASTA_PDFS, exist_ok=True)
    os.makedirs(PASTA_CORPUS, exist_ok=True)
    
    print(f"--- Iniciando conversão ---")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT caminho_pdf, caminho_arquivo FROM livros WHERE status = 'PROCESSADO'")
        livros_a_processar = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"ERRO FATAL: Não foi possível ler o banco de dados '{DB_PATH}'. {e}")
        print("           Execute 'scripts_db.py' primeiro.")
        return

    if not livros_a_processar:
        print("Nenhum livro marcado como 'PROCESSADO' foi encontrado no DB.")
        return

    print(f"Encontrados {len(livros_a_processar)} livros marcados como 'PROCESSADO' no DB para converter.")

    sucesso = 0
    falha = 0

    for livro in livros_a_processar:
        caminho_pdf = livro['caminho_pdf']
        caminho_txt = livro['caminho_arquivo']
        
        if not caminho_pdf or not os.path.exists(caminho_pdf):
            print(f"  AVISO: PDF '{caminho_pdf}' não encontrado no disco. Pulando.")
            falha += 1
            continue
            
        if converter_pdf_para_txt_limpo(caminho_pdf, caminho_txt):
            sucesso += 1
        else:
            falha += 1

    print(f"\n--- Conversão inteligente (v6.0) concluída! ---")
    print(f"Sucesso: {sucesso} / Falha: {falha}")

if __name__ == '__main__':
    rodar_build_limpo_completo()
# converter_pdf.py

import pdfplumber
import os

# Define as pastas de origem (onde estão os PDFs) e de destino (onde salvar os TXTs)
PASTA_PDFS = 'static/pdfs/'
PASTA_CORPUS = 'corpus/'

# Garante que as pastas de destino existam
os.makedirs(PASTA_PDFS, exist_ok=True)
os.makedirs(PASTA_CORPUS, exist_ok=True)

print(f"--- Iniciando conversão de PDFs da pasta '{PASTA_PDFS}' ---")

# Verifica se a pasta de origem existe e não está vazia
if not os.path.exists(PASTA_PDFS) or not os.listdir(PASTA_PDFS):
    print(f"AVISO: A pasta de origem '{PASTA_PDFS}' não existe ou está vazia.")
    print("Por favor, adicione os arquivos PDF que deseja converter e tente novamente.")
else:
    # Lista todos os arquivos na pasta de PDFs
    arquivos_na_pasta = os.listdir(PASTA_PDFS)
    pdfs_encontrados = [arquivo for arquivo in arquivos_na_pasta if arquivo.lower().endswith('.pdf')]
    
    print(f"Encontrados {len(pdfs_encontrados)} arquivos PDF para processar.")

    for nome_arquivo_pdf in pdfs_encontrados:
        caminho_pdf_completo = os.path.join(PASTA_PDFS, nome_arquivo_pdf)
        
        # Define o nome do arquivo de texto de saída (mesmo nome, extensão .txt)
        nome_arquivo_txt = os.path.splitext(nome_arquivo_pdf)[0] + '.txt'
        caminho_txt_completo = os.path.join(PASTA_CORPUS, nome_arquivo_txt)
        
        print(f"\n[PROCESSANDO]: {nome_arquivo_pdf}")
        
        texto_completo = ""
        try:
            # Abre o arquivo PDF com o pdfplumber
            with pdfplumber.open(caminho_pdf_completo) as pdf:
                # Itera sobre cada página do PDF
                for i, pagina in enumerate(pdf.pages):
                    # Extrai o texto da página
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:  # Adiciona o texto se a extração for bem-sucedida
                        texto_completo += texto_pagina + "\n"
            
            # Salva o texto extraído no arquivo .txt com codificação UTF-8
            with open(caminho_txt_completo, 'w', encoding='utf-8') as f:
                f.write(texto_completo)
            
            print(f"  [SUCESSO] -> Salvo em '{caminho_txt_completo}'")
        
        except Exception as e:
            # Captura e informa erros que possam ocorrer (ex: PDF corrompido)
            print(f"  [ERRO] -> Não foi possível processar o arquivo {nome_arquivo_pdf}.")
            print(f"          Motivo: {e}")

    print("\n--- Conversão concluída! ---")
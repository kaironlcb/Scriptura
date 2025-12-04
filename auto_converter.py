import pdfplumber
import os
import re
import string

MARCADORES_INICIO = re.compile(
    r'\b(CAPÍTULO\s+(I|1)|CANTO\s+(I|1)|ATO\s+(I|1)|PARTE\s+(I|1)|LIVRO\s+(I|1)|INTRODUÇÃO|PRIMEIRA\s+PARTE)\b',
    re.IGNORECASE
)

def converter_pdf_para_txt_limpo(caminho_pdf_completo, caminho_txt_completo):
    """
    Converte um ÚNICO PDF para .txt, aplicando a limpeza "Bisturi".
    Verifica se o .txt já existe antes de processar.
    Retorna True se o .txt foi criado (ou já existia), False se deu erro.
    """
    
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
    """
    Função "mestre" que processa TODOS os 46 PDFs da pasta static/pdfs/.
    """
    PASTA_PDFS = 'static/pdfs/'
    PASTA_CORPUS = 'corpus/'

    os.makedirs(PASTA_PDFS, exist_ok=True)
    os.makedirs(PASTA_CORPUS, exist_ok=True)
    
    print(f"--- Iniciando conversão INTELIGENTE (v5.0) da pasta '{PASTA_PDFS}' ---")
    
    livros_no_db = [
        'a_cidade_e_as_serras.pdf', 'a_ilustre_casa_de_ramires.pdf', 'a_mao_e_a_luva.pdf',
        'a_moreninha.pdf', 'a_pata_da_gazela.pdf', 'a_reliquia.pdf', 'a_viuvinha.pdf',
        'americanas.pdf', 'cinco_minutos.pdf', 'contos_eca_de_queiroz.pdf',
        'contos_fluminenses.pdf', 'crisalidas.pdf', 'diva.pdf', 'dom_casmurro.pdf',
        'encarnacao.pdf', 'esau_e_jaco.pdf', 'falenas.pdf', 'helena.pdf',
        'historias_da_meia_noite.pdf', 'iaia_garcia.pdf', 'iracema.pdf', 'luciola.pdf',
        'macbeth.pdf', 'memorial_de_aires.pdf', 'memorias_postumas_de_bras_cubas.pdf',
        'noite_na_taverna.pdf', 'o_alienista.pdf', 'o_cortico.pdf',
        'o_crime_do_padre_amaro.pdf', 'o_gaucho.pdf', 'o_guarani.pdf', 'o_mandarim.pdf',
        'o_primo_basilio.pdf', 'o_sertanejo.pdf', 'o_tronco_do_ipe.pdf', 'ocidentais.pdf',
        'os_maias.pdf', 'paginas_recolhidas.pdf', 'papeis_avulsos.pdf',
        'poemas_de_fernando_pessoa.pdf', 'quincas_borba.pdf', 'reliquias_de_casa_velha.pdf',
        'senhora.pdf', 'sonhos_douro.pdf', 'til.pdf', 'varias_historias.pdf'
    ]
    
    pdfs_a_processar = [f for f in os.listdir(PASTA_PDFS) if f.lower() in livros_no_db]
    print(f"Encontrados {len(pdfs_a_processar)} arquivos PDF (do DB de 46) para processar.")

    sucesso = 0
    falha = 0

    for nome_arquivo_pdf in pdfs_a_processar:
        caminho_pdf = os.path.join(PASTA_PDFS, nome_arquivo_pdf)
        nome_txt = os.path.splitext(nome_arquivo_pdf)[0] + '.txt'
        caminho_txt = os.path.join(PASTA_CORPUS, nome_txt)
        
        if converter_pdf_para_txt_limpo(caminho_pdf, caminho_txt):
            sucesso += 1
        else:
            falha += 1

    print(f"\n--- Conversão inteligente (v5.0) concluída! ---")
    print(f"Sucesso: {sucesso} / Falha: {falha}")

if __name__ == '__main__':
    rodar_build_limpo_completo()
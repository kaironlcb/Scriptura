# processar_textos.py
import sqlite3
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer

DB_PATH = 'literatura.db'

def processar_e_salvar_indice():
    """
    Lê os textos do corpus, processa-os com TF-IDF e salva o vetorizador,
    a matriz e os IDs dos documentos para uso pela API.
    """
    print("--- Iniciando o processamento dos textos para o índice de busca ---")

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Pega o ID e o caminho do arquivo de texto para cada livro no banco
        cursor.execute('SELECT id, caminho_arquivo FROM livros')
        livros = cursor.fetchall()
        conn.close()
    except sqlite3.Error as e:
        print(f"ERRO: Não foi possível ler o banco de dados '{DB_PATH}'. Você já executou o 'scripts_db.py'?")
        print(f"Detalhe do erro: {e}")
        return

    documentos = []
    ids_documentos = []

    print(f"\nLendo e processando {len(livros)} obras literárias...")
    for livro_id, caminho_arquivo in livros:
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                texto = f.read()
                # Dividindo o texto em parágrafos para uma busca mais precisa e granular.
                # Isso melhora muito a qualidade dos resultados!
                paragrafos = texto.split('\n\n')
                for paragrafo in paragrafos:
                    # Ignorar parágrafos muito curtos que não têm muito significado
                    if len(paragrafo) > 100:
                        documentos.append(paragrafo)
                        ids_documentos.append(livro_id)
        except FileNotFoundError:
            print(f"  AVISO: O arquivo '{caminho_arquivo}' listado no banco de dados não foi encontrado na pasta 'corpus/'. Pulando.")
        except Exception as e:
            print(f"  AVISO: Erro ao ler o arquivo '{caminho_arquivo}': {e}. Pulando.")
            
    if not documentos:
        print("\nERRO: Nenhum documento foi processado. Verifique se a pasta 'corpus/' contém os arquivos .txt corretos.")
        return

    print(f"\nTotal de {len(documentos)} parágrafos válidos foram extraídos para indexação.")
    
    # Criando o vetorizador TF-IDF com algumas stop words em português
    print("Criando a matriz TF-IDF (isso pode levar alguns minutos)...")
    vectorizer = TfidfVectorizer(stop_words=['de', 'a', 'o', 'que', 'e', 'do', 'da', 'em', 'um', 'para', 'com', 'não', 'os', 'as'])
    tfidf_matrix = vectorizer.fit_transform(documentos)

    # Salvando os objetos para uso futuro na API
    print("\nSalvando os arquivos de índice (vectorizer.pkl, tfidf_matrix.pkl, ids_documentos.pkl)...")
    joblib.dump(vectorizer, 'vectorizer.pkl')
    joblib.dump(tfidf_matrix, 'tfidf_matrix.pkl')
    joblib.dump(ids_documentos, 'ids_documentos.pkl')
    
    print("\n--- Processamento concluído com sucesso! O 'cérebro' do motor de busca está pronto. ---")

if __name__ == '__main__':
    processar_e_salvar_indice()
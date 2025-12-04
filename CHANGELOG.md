# Changelog

## [0.3.0] - 2025-11-04
### Adicionado
- **Motor de Busca Neural:** Substituição do TF-IDF por `Sentence-Transformers` (modelo `paraphrase-multilingual-MiniLM-L12-v2`), permitindo busca semântica por significado real, não apenas palavras-chave.
- **Chunking Semântico:** Nova estratégia de indexação em `processar_textos.py` que divide o texto em janelas deslizantes de 3 frases com sobreposição (overlap) de 2 frases, garantindo contexto contínuo.
- **Ferramentas de Diagnóstico:** Script `verificar_indices.py` para validar a sincronia entre o banco de dados e os arquivos de índice `.pkl`[cite: 1304].
- **Endpoint de Auditoria:** Rota `GET /auditar-livro/{id}` na API para visualizar como o texto está sendo "lido" e fatiado pelo sistema em tempo real[cite: 998].
- **Limpeza de Dados:** pipeline de limpeza robusto com `Regex` e `Spacy` para remover artefatos de PDF (cabeçalhos, números de página, quebras de linha quebradas).

### Alterado
- **Banco de Dados:** `scripts_db.py` atualizado para povoar o banco com 46 obras literárias validadas e caminhos corrigidos[cite: 1293].
- **Estrutura de Arquivos:** Os índices agora são `embeddings.pkl` e `ids_documentos.pkl` (o vetorizador TF-IDF foi removido)[cite: 980].

---

## [0.2.0] - 2025-10-06
### Adicionado
- **Automação de ETL:** Script `auto_converter.py` implementado com `pdfplumber` para extrair texto de PDFs automaticamente.
- **Banco de Dados Populado:** Script `scripts_db.py` criado para inicializar o SQLite com 88 obras clássicas da literatura (Machado de Assis, José de Alencar, Eça de Queiroz, etc.).
- **Processamento de Texto:** Script `processar_textos.py` para gerar a matriz TF-IDF e persistir os índices (`.pkl`) em disco.
- **Sistema de Recomendação:** API atualizada para retornar sugestões baseadas em Autor e Gênero, além da busca principal.
- **Arquivos Estáticos:** Configuração no `main.py` para servir os PDFs originais através da rota `/static`.
- **Dependências:** Arquivo `requirements.txt` adicionado.

### Alterado
- O `main.py` foi refatorado para suportar `ResultadoComRecomendacoes` e tratar erros de conexão com o banco de forma mais robusta.

---

## [0.1.0] - 2025-09-30
### Adicionado
- **API Inicial:** Estrutura básica criada com FastAPI[cite: 838].
- **Endpoint de Identificação:** Rota `POST /identificar-obra` para receber trechos de texto[cite: 848].
- **Mecanismo de Busca:** Implementação inicial utilizando `cosine_similarity` sobre uma matriz TF-IDF (identificada pelos arquivos `vectorizer.pkl` e `tfidf_matrix.pkl`)[cite: 826, 854].
- **Integração com Banco de Dados:** Conexão de leitura com SQLite (`literatura.db`) para recuperar metadados (Título, Autor, Ano, Gênero)[cite: 867].
- **Modelos de Dados:** Schemas Pydantic `TextoParaAnalisar` (entrada) e `InfoObraResponse` (saída) [cite: 817-818].

### Observações Técnicas
- Esta versão opera de forma síncrona na carga de arquivos `.pkl`.
- Depende da execução prévia de um script interno `processar_textos.py` para gerar os índices.
# Changelog

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
- [cite_start]**API Inicial:** Estrutura básica criada com FastAPI[cite: 838].
- [cite_start]**Endpoint de Identificação:** Rota `POST /identificar-obra` para receber trechos de texto[cite: 848].
- [cite_start]**Mecanismo de Busca:** Implementação inicial utilizando `cosine_similarity` sobre uma matriz TF-IDF (identificada pelos arquivos `vectorizer.pkl` e `tfidf_matrix.pkl`)[cite: 826, 854].
- [cite_start]**Integração com Banco de Dados:** Conexão de leitura com SQLite (`literatura.db`) para recuperar metadados (Título, Autor, Ano, Gênero)[cite: 867].
- [cite_start]**Modelos de Dados:** Schemas Pydantic `TextoParaAnalisar` (entrada) e `InfoObraResponse` (saída) [cite: 817-818].

### Observações Técnicas
- Esta versão opera de forma síncrona na carga de arquivos `.pkl`.
- [cite_start]Depende da execução prévia de um script interno `processar_textos.py` para gerar os índices.
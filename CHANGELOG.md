# Changelog

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
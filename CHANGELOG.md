# Changelog

## [0.5.0] - 2025-11-20
### Adicionado
- **Busca por Fatiamento:** Nova lógica no endpoint `/recomendar-por-tema` que isola e utiliza apenas a primeira frase do texto de entrada. Isso foca o vetor semântico na ideia central e reduz o ruído causado por textos longos na busca.
- **Indexação Granular:** Alteração estratégica no `processar_textos.py` para `CHUNK_SIZE = 1`. O sistema agora indexa frase por frase individualmente, aumentando a precisão na recuperação de trechos específicos.
- **Filtro Sanitário:** Implementação de uma `blacklist` rigorosa (`JUNK_KEYWORDS`) para descartar chunks que contenham URLs, e-mails ou marcas de digitalização, substituindo lógicas anteriores mais complexas.
- **Integração SpaCy na API:** O `main.py` passou a carregar o modelo de linguagem `pt_core_news_lg` para garantir que a segmentação da frase de busca seja idêntica à usada na indexação.

### Alterado
- **Simplificação do Pipeline:** Remoção da lógica de "Bisturi" e marcadores de início. O sistema agora confia inteiramente no filtro de conteúdo e na indexação granular.

---

## [0.4.0] - 2025-11-15
### Adicionado
- **Processamento em Lotes:** Implementação de `MANUAL_BATCH_SIZE = 512` no script `processar_textos.py`. Agora a geração de embeddings é feita em pedaços, evitando estouro de memória RAM ao processar o corpus inteiro de uma vez.
- **Filtro "Light" de Conteúdo:** Substituição da lógica de limpeza agressiva por uma `blacklist` específica (`JUNK_KEYWORDS`). O sistema agora remove apenas artefatos digitais óbvios (ex: "www.", "adobe acrobat", URLs), preservando mais texto literário válido.
- **Tratamento de Codificação:** Adicionado fallback automático para `latin-1` caso a leitura do arquivo de texto em `utf-8` falhe, resolvendo erros de importação em textos mais antigos.
- **Proteção contra Chunks Gigantes:** Implementada verificação `MAX_CHUNK_LENGTH = 10000` para descartar chunks anormais que poderiam travar o modelo de embeddings.

### Alterado
- O script de processamento agora exibe estatísticas detalhadas de quantos chunks foram descartados por serem lixo ou por excesso de tamanho.

---

## [0.3.0] - 2025-11-04
### Adicionado
- **Motor de Busca Neural:** Substituição do TF-IDF por Sentence-Transformers (`paraphrase-multilingual-MiniLM-L12-v2`), permitindo busca semântica por significado real.
- **Chunking Semântico:** Estratégia de janelas deslizantes com 3 frases e overlap de 2, garantindo continuidade contextual.
- **Ferramentas de Diagnóstico:** Criação do script `verificar_indices.py` para validar sincronização entre banco de dados e arquivos `.pkl`.
- **Endpoint de Auditoria:** Implementação da rota `GET /auditar-livro/{id}` para visualizar como o texto foi fatiado e limpo pelo sistema.
- **Limpeza de Dados:** Pipeline robusto com Regex + SpaCy para remover artefatos de PDF, como cabeçalhos, numeração e quebras problemáticas.

### Alterado
- **Banco de Dados:** `scripts_db.py` atualizado com 46 obras literárias validadas e caminhos corrigidos.
- **Estrutura de Arquivos:** Os índices agora são `embeddings.pkl` e `ids_documentos.pkl`. Arquivos TF-IDF antigos removidos.

---

## [0.2.0] - 2025-10-06
### Adicionado
- **Automação de ETL:** Implementado `auto_converter.py` com `pdfplumber` para extrair texto de PDFs automaticamente.
- **Banco de Dados Populado:** `scripts_db.py` criado para inicializar o SQLite com 88 obras clássicas.
- **Processamento de Texto:** Script `processar_textos.py` para gerar a matriz TF-IDF e persistir índices `.pkl`.
- **Sistema de Recomendação:** API atualizada para retornar sugestões por Autor e Gênero.
- **Arquivos Estáticos:** Configuração no `main.py` para servir PDFs pela rota `/static`.
- **Dependências:** Criação do arquivo `requirements.txt`.

### Alterado
- `main.py` refatorado para suportar `ResultadoComRecomendacoes` e melhorar o tratamento de erros de banco de dados.

---

## [0.1.0] - 2025-09-30
### Adicionado
- **API Inicial:** Estrutura base criada com FastAPI.
- **Endpoint de Identificação:** Rota `POST /identificar-obra` para receber trechos de texto.
- **Mecanismo de Busca:** Implementação inicial de TF-IDF com `cosine_similarity` utilizando `vectorizer.pkl` e `tfidf_matrix.pkl`.
- **Integração com Banco de Dados:** Conexão com SQLite (`literatura.db`) para recuperar metadados das obras.
- **Modelos de Dados:** Schemas Pydantic `TextoParaAnalisar` (entrada) e `InfoObraResponse` (saída).

### Observações Técnicas
- A versão opera de forma síncrona na leitura dos arquivos `.pkl`.
- Dependente da execução prévia do script `processar_textos.py` para geração dos índices.

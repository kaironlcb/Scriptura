# Scriptura

**Sistema web de análise e recomendação literária utilizando Processamento de Linguagem Natural (PLN).**

O **Scriptura** é um protótipo acadêmico desenvolvido para analisar, processar e recomendar obras literárias de domínio público. Diferente de sistemas baseados em popularidade, o Scriptura utiliza vetores semânticos (embeddings) e modelos de linguagem para identificar similaridade de contexto, estilo e significado entre trechos e obras.

> Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC) no Centro Universitário do Distrito Federal (UDF).

---

## Índice

- [Sobre o Projeto](#sobre-o-projeto)  
- [Funcionalidades](#funcionalidades)  
- [Requisitos do Sistema](#requisitos-do-sistema)  
- [Instalação e Configuração](#instalacao-e-configuracao)
- [Estrutura do Projeto](#estrutura-do-projeto)  
- [Como Usar](#como-usar)  
- [Tecnologias Utilizadas](#tecnologias-utilizadas)  
- [Arquitetura](#arquitetura)  
- [Avisos](#avisos)  
- [Licença](#licenca)

---

<a name="sobre-o-projeto"></a>
## Sobre o Projeto

O projeto visa democratizar o acesso ao acervo literário, oferecendo ferramentas para:

- Identificar a origem exata de citações e trechos.  
- Recomendar obras baseadas em descrições abstratas de temas ou sentimentos.  
- Processar automaticamente textos em português, gerando metadados analíticos.

---

<a name="funcionalidades"></a>
## Funcionalidades

- **Busca por Trecho (Busca Vetorial):** Localiza a obra de origem de uma citação específica utilizando similaridade de cosseno em vetores de sentença.  
- **Busca por Contexto (Busca Híbrida):** Recomenda obras baseadas em temas. Utiliza uma fusão de Sentence-BERT (significado) e Okapi BM25 (palavras-chave).  
- **Upload de Obras:** Permite o envio de novos PDFs para o corpus (sujeito a revisão administrativa).  
- **Painel Administrativo:** Interface para validação, edição e exclusão de obras do acervo.

---

<a name="requisitos-do-sistema"></a>
## Requisitos do Sistema

- **SO:** Windows 10/11 (scripts `.bat` incluídos) ou Linux/macOS.  
- **Python:** 3.8 — 3.11.  
- **RAM:** Mínimo 4 GB (8 GB recomendados).  
- **Espaço em Disco:** ~2 GB (modelos + corpus).  

---

<a name="instalacao-e-configuracao"></a>
## Instalação e Configuração


> ### 1. Clonar o repositório
```bash
git clone https://github.com/kaironlcb/Scriptura.git
cd Scriptura
```
> ### 2. Execute o script de instalação
No Windows, execute o arquivo `instalacao.bat`. Este script criará o ambiente virtual, instalará as dependências e baixará o modelo do spaCy.

```bash
instalacao.bat
```

> ### 3. Inicialize o banco de dados
Após a instalação, ative o ambiente e popule o banco com o acervo inicial:
```bash
venv\Scripts\activate
python scripts_db.py
```
> ### 4. Converta os PDFs para texto
Processe os arquivos da pasta static/pdfs/ para gerar os textos brutos:
```bash
python auto_converter.py
```

> ### 5. Gere os índices de busca
Execute os scripts de processamento na ordem abaixo para criar os vetores de busca (embeddings):
```bash
python processar_textos.py
python processar_temas.py
```
> Atenção: O processamento inicial pode levar de 30 minutos a 2 horas, dependendo do seu hardware (CPU/GPU).

> ### 6. Inicie o servidor
```bash
iniciar.bat
```
> O servidor será iniciado em http://127.0.0.1:8000. Mantenha o terminal aberto.

> ### 7. Acesse a interface
Abra seu navegador e acesse: http://127.0.0.1:8000/static/frontend/home.html

<a name="estrutura-do-projeto"></a>

## Estrutura do Projeto

```tree
Scriptura/
│
├── corpus/                      # Arquivos de texto extraídos dos PDFs
├── static/
│   ├── pdfs/                    # Arquivos PDF das obras
│   └── frontend/                # Interface web (HTML, CSS, JS)
│       ├── home.html
│       ├── trecho.html
│       ├── contexto.html
│       ├── upload.html
│       ├── admin.html
│       ├── style.css
│       ├── app.js
│       └── admin.js
│
├── venv/                        # Ambiente virtual Python
├── literatura.db                # Banco de dados SQLite
│
├── main.py                      # API FastAPI principal
├── scripts_db.py                # Criação e população do banco
├── auto_converter.py            # Conversão PDF para TXT
├── processar_textos.py          # Geração de índices de trecho
├── processar_temas.py           # Geração de índices de tema
│
├── embeddings_TRECHO.pkl        # Vetores de embeddings (trecho)
├── index_TRECHO.pkl             # Índice de metadados (trecho)
├── embeddings_TEMA.pkl          # Vetores de embeddings (tema)
├── index_TEMA.pkl               # Índice de metadados (tema)
│
├── instalacao.bat               # Script de instalação
├── iniciar.bat                  # Script para iniciar o servidor
├── atualizar_lista.bat          # Atualiza índices sem apagar o DB
├── recons_cuidado.bat           # Reset completo do sistema
├── requirements.txt             # Dependências Python
└── README.md                    # Documentação
```
<a name="como-usar"></a>

## Como Usar
### Adicionando Novas Obras
Via Interface Web: Acesse "Enviar livro", selecione o PDF e preencha os metadados. A obra ficará como EM_REVISAO.
Manualmente: Coloque o PDF em static/pdfs/, adicione ao banco via script e execute:
```bash
atualizar_lista.bat
```

### Painel Administrativo
- Acesse admin.html (Senha padrão: admin123).
- Aprove obras enviadas por usuários.
- Edite metadados ou exclua registros.
> Importante: Após aprovar obras, rode atualizar_lista.bat para indexá-las.

### Resetar o Sistema
Para apagar tudo e restaurar apenas o acervo padrão (Cuidado!):
```bash
recons_cuidado.bat
```
<a name="tecnologias-utilizadas"></a>
## Tecnologias Utilizadas
### Backend
- Python 3.8+
- FastAPI (API REST assíncrona)
- SQLite (Banco de dados relacional)

### Processamento de Linguagem Natural (PLN)
- spaCy: Segmentação e análise linguística.
- Sentence-Transformers: Modelo paraphrase-multilingual-MiniLM-L12-v2.
- Scikit-learn: Cálculo de similaridade de cosseno.
- Rank-BM25: Busca por palavras-chave (Híbrida).

### Frontend
- HTML5 | CSS3 | JavaScript 

<a name="arquitetura"></a>
## Arquitetura
O Scriptura utiliza uma arquitetura de pipeline duplo:
- Pipeline Offline (ETL Semântico):
- Extração de texto de PDFs.
- Segmentação em sentenças.
- Geração de embeddings e persistência em arquivos .pkl.

### Camada Online (API):
- Carrega índices na memória RAM na inicialização.
- Realiza Busca Híbrida para temas: combina score vetorial (semântico) com score BM25 (palavras-chave).

<a name="avisos"></a>
## Avisos Importantes
- Direitos Autorais: O sistema foi projetado estritamente para obras de Domínio Público (Lei 9.610/98).
- Desempenho: A geração inicial de índices exige processamento intensivo.
- Manutenção: Sempre que alterar arquivos na pasta corpus/, regenere os índices.

<a name="licenca"></a>
## Licença
Este projeto foi desenvolvido como Trabalho de Conclusão de Curso (TCC) no Centro Universitário do Distrito Federal (UDF) em 2025.

## Autores:

- Alan Rocha Alves
- Iverson Cintra de Andrade Ferreira
- Kairon de Lima Castelo Branco

> Orientadora: Prof. Ma. Karla Roberto Sartin

#### O código fonte é disponibilizado para fins educacionais. O acervo literário incluído consiste apenas em obras de domínio público.

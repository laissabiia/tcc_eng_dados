# 📚 Análise de artigos do WIE e WEI em relação aos eixos da BNCC

Projeto acadêmico desenvolvido em notebooks para obter, tratar e analisar os
artigos publicados no Workshop de Informática na Escola (WIE) e no Workshop
sobre Educação em Computação (WEI). O fluxo identifica termos e expressões (bigramas)
relevantes nos títulos e usa descritores selecionados para classificar os
artigos nos eixos da BNCC Computação.

## 🔄 Etapas do projeto

1. coleta dos metadados dos artigos no portal SOL/SBC;
2. consolidação e preparação dos dados;
3. pré-processamento dos textos;
4. análise de termos e bigramas dos títulos;
5. classificação multirrótulo nos eixos da BNCC;
6. preparação de tabelas para o Power BI;
7. geração de nuvens de palavras por evento.

## 📁 Estrutura do repositório

```text
tcc_eng_dados/
├── apoio/
│   ├── funcoes.py
│   └── termos_bncc.yml
├── dados/
│   ├── 0_brutos/        # planilhas obtidas do WIE e do WEI
│   ├── 1_processados/   # arquivos intermediários em CSV
│   └── 2_consumo/       # planilha e imagens para consumo e apresentação
├── notebooks/
│   ├── 00_obtencao_dos_dados.ipynb
│   ├── 01_preparacao_dos_dados.ipynb
│   ├── 02_pre_processamento.ipynb
│   ├── 03_analise_termos_bigramas.ipynb
│   ├── 04_classificacao_bncc.ipynb
│   ├── 05_analise_dos_resultados.ipynb
│   └── 06_geracao_imagens.ipynb
├── .gitignore
├── README.md
└── requirements.txt
```

As três pastas de `dados/` são criadas pelos notebooks quando necessário e
não são versionadas. `apoio/funcoes.py` reúne funções de coleta, limpeza,
classificação e visualização; `apoio/termos_bncc.yml` contém o vocabulário de
descritores associado a cada eixo.

## 🛠️ Requisitos e instalação

- Python 3.10 ou superior;
- acesso à internet para a coleta no portal SOL/SBC e para o primeiro download
  das stopwords do NLTK.

No PowerShell, a partir da raiz do projeto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m nltk.downloader stopwords
python -m jupyter lab
```

Se a política de execução do PowerShell impedir a ativação do ambiente, os
comandos também podem ser executados diretamente com
`.\.venv\Scripts\python.exe`.

## ▶️ Execução

Abra os notebooks pelo JupyterLab e execute-os na ordem numérica, sempre a
partir da raiz do repositório:

1. `00_obtencao_dos_dados.ipynb` — coleta as edições do WIE e WEI entre 2007 e
   2025 e gera planilhas anuais e consolidadas em `dados/0_brutos`;
2. `01_preparacao_dos_dados.ipynb` — reúne as planilhas brutas, preservando a
   origem de cada registro;
3. `02_pre_processamento.ipynb` — normaliza os textos e separa registros
   editoriais, pré-textuais e páginas de abertura;
4. `03_analise_termos_bigramas.ipynb` — calcula termos e bigramas relevantes
   nos títulos e suas frequências por ano e evento;
5. `04_classificacao_bncc.ipynb` — classifica os artigos nos eixos Pensamento
   Computacional, Mundo Digital e Cultura Digital;
6. `05_analise_dos_resultados.ipynb` — organiza as tabelas analíticas e exporta
   o modelo para o Power BI;
7. `06_geracao_imagens.ipynb` — cria nuvens de termos e bigramas para WIE e
   WEI.

O intervalo de anos e as URLs dos eventos podem ser alterados na seção de
parâmetros do notebook `00`. Como a coleta consulta um serviço externo, o
tempo de execução e a quantidade de registros podem variar. Se as planilhas
brutas já existirem, é possível iniciar pelo notebook `01`.

## 📊 Principais saídas

### 📥 Dados brutos

O notebook `00` grava em `dados/0_brutos`:

- planilhas anuais `wie_artigos_<ano>.xlsx` e `wei_artigos_<ano>.xlsx`;
- consolidados `wie_artigos_consolidados.xlsx` e
  `wei_artigos_consolidados.xlsx`.

### ⚙️ Dados processados

Os notebooks `01` a `04` gravam em `dados/1_processados`:

- `01_artigos_consolidados.csv`;
- `02_artigos_pre_processados.csv`;
- `03_termos_titulos.csv` e `03_bigramas_titulos.csv`;
- `03_ranking_termos_titulos.csv` e
  `03_ranking_bigramas_titulos.csv`;
- `03_frequencia_termos_ano_evento.csv` e
  `03_frequencia_bigramas_ano_evento.csv`;
- `04_artigos_classificados_bncc.csv`;
- `04_classificacoes_bncc.csv`.

Na análise de relevância, o notebook `03` usa frequência mínima equivalente a
2% do corpus para termos e 1% para bigramas. As stopwords em português do NLTK
e palavras com até dois caracteres são removidas.

### 📤 Arquivos para consumo

Os notebooks `05` e `06` gravam em `dados/2_consumo`:

- `05_powerbi_bncc.xlsx`, com as tabelas para importação no Power BI;
- `imagens/nuvem_termos_wie.png` e `imagens/nuvem_termos_wei.png`;
- `imagens/nuvem_bigramas_wie.png` e `imagens/nuvem_bigramas_wei.png`.

## 🧭 Metodologia de classificação

O vocabulário em `apoio/termos_bncc.yml` associa termos e bigramas aos eixos
Pensamento Computacional, Mundo Digital e Cultura Digital. Apenas descritores
presentes nos rankings relevantes são ativados. A busca considera palavras e
expressões completas no texto normalizado do artigo, e um mesmo artigo pode
ser associado a mais de um eixo. As evidências encontradas são mantidas na
saída para permitir revisão.

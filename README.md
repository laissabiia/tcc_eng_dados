# Análise de artigos do WIE e WEI em relação aos eixos da BNCC

Projeto acadêmico desenvolvido em notebooks para reunir, tratar e analisar os
artigos publicados no WIE e no WEI. O fluxo identifica termos e bigramas
relevantes nos títulos e utiliza os descritores selecionados para classificar
os artigos em relação aos eixos da BNCC.

## Organização

```text
tcc_eng_dados/
├── apoio/
│   ├── bncc_computacao.txt
│   ├── funcoes.py
│   └── termos_bncc.yml
├── dados/
│   ├── 0_brutos/        # planilhas originais do WIE e do WEI
│   ├── 1_processados/   # arquivos intermediários das etapas 1 a 4
│   └── 2_consumo/       # planilhas finais para análise no Power BI
├── notebooks/
│   ├── 01_preparacao_dos_dados.ipynb
│   ├── 02_pre_processamento.ipynb
│   ├── 03_analise_termos_bigramas.ipynb
│   ├── 04_classificacao_bncc.ipynb
│   └── 05_analise_dos_resultados.ipynb
├── .gitignore
├── README.md
└── requirements.txt
```

- `apoio`: concentra as funções reutilizadas pelos notebooks, o texto de
  referência da BNCC Computação e o arquivo YAML que relaciona descritores aos
  eixos da BNCC;
- `dados/0_brutos`: armazena as planilhas originais do WIE e do WEI, mantidas
  sem alterações;
- `dados/1_processados`: recebe os arquivos CSV produzidos ao longo da
  preparação, do pré-processamento, da análise de termos e da classificação;
- `dados/2_consumo`: reúne as planilhas XLSX consolidadas para consumo no Power
  BI;
- `notebooks`: contém o fluxo de processamento e análise, numerado conforme a
  ordem em que deve ser executado;
- `requirements.txt`: lista as dependências Python necessárias para executar o
  projeto.

## Ambiente

```powershell
python -m pip install -r requirements.txt
python -m nltk.downloader stopwords
python -m jupyter lab
```

## Ordem de execução

1. `01_preparacao_dos_dados.ipynb`
2. `02_pre_processamento.ipynb`
3. `03_analise_termos_bigramas.ipynb`
4. `04_classificacao_bncc.ipynb`
5. `05_analise_dos_resultados.ipynb`

## 1. Preparação dos dados

Reúne todas as abas das planilhas WIE e WEI e preserva o evento, arquivo, aba
e linha de origem. Nenhum registro é removido nessa etapa.

Saídas:

- `artigos_consolidados.csv`.

Resultado de referência: 2.126 registros, sendo 1.269 do WIE e 857 do WEI.

## 2. Pré-processamento

Separa elementos pré-textuais, editoriais e páginas de abertura. As colunas
originais são preservadas. O texto usado nas análises é composto apenas por
título e resumo.

São criadas:

- `titulo_limpo`, para a análise de termos e bigramas dos títulos;
- `texto_original`, formado por título e resumo;
- `texto_limpo`, usado para localizar os descritores da classificação.

Saídas:

- `artigos_pre_processados.csv`;
- `registros_removidos.csv`.

Resultado de referência: 2.110 artigos mantidos e 16 registros separados.

## 3. Termos e bigramas relevantes

Remove stopwords em português disponibilizadas pelo NLTK e palavras com até
dois caracteres. A análise utiliza somente `titulo_limpo`.

Critérios utilizados:

- termos: frequência mínima equivalente a 2% dos 2.110 artigos;
- bigramas: frequência mínima equivalente a 1% dos 2.110 artigos.

Isso corresponde a limites de 43 ocorrências para termos e 22 para bigramas.
Foram encontrados 73 termos e 37 bigramas relevantes.

Saídas:

- `termos_titulos.csv`;
- `bigramas_titulos.csv`;
- `ranking_termos_titulos.csv`;
- `ranking_bigramas_titulos.csv`;
- `frequencia_termos_ano_evento.csv`;
- `frequencia_bigramas_ano_evento.csv`.

## 4. Classificação BNCC

O arquivo `apoio/termos_bncc.yml` associa parte dos termos e bigramas
relevantes aos eixos Pensamento Computacional, Mundo Digital e Cultura
Digital. Somente descritores que aparecem nos rankings relevantes são
ativados. A classificação procura esses descritores em `texto_limpo`, ou seja,
no título e no resumo.

A classificação é multirrótulo e registra separadamente termos e bigramas que
justificaram cada eixo.

Saídas:

- `artigos_classificados_bncc.csv`;
- `classificacoes_bncc.csv`;
- `artigos_nao_classificados.csv`;
- `resumo_classificacao_bncc.csv`;
- `frequencia_descritores_bncc.csv`.

## 5. Análise e Power BI

⚠️ Em desenvolvimento.

Arquivos gerados em `dados/2_consumo`:

- `modelo_power_bi_bncc.xlsx`;
- `resumos_power_bi_bncc.xlsx`.

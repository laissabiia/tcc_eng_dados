"""Funções simples compartilhadas pelos notebooks do TCC."""

import random
import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import yaml
from wordcloud import WordCloud
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from typing import Iterable

# -----------------------
# Funções de scraping e consolidação (WIE / WEI)
# -----------------------
def get_html(url: str, headers: dict | None = None, timeout: int = 30, retries: int = 3, backoff_factor: float = 1.0) -> str:
    """Fazer GET simples com retries e jitter. Retorna o texto HTML.

    Parâmetros:
    - url: URL a ser requisitada
    - headers: cabeçalhos HTTP
    - timeout: timeout por requisição
    - retries: número de tentativas em caso de erro transitório
    - backoff_factor: fator usado para calcular tempo de espera exponencial
    """
    headers = headers or {"User-Agent": "Mozilla/5.0"}
    last_err = None
    for tentativa in range(1, retries + 1):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            last_err = e
            if tentativa == retries:
                raise
            sleep_time = backoff_factor * (2 ** (tentativa - 1))
            # jitter
            sleep_time += random.uniform(0, 0.5)
            time.sleep(sleep_time)


def get_edicoes(archive_url: str) -> list[dict]:
    """Retornar lista de edições encontradas na página de arquivo do evento.

    Cada item: {'ano': 'YYYY'|'desconhecido', 'titulo': str, 'url': str}
    """
    html = get_html(archive_url)
    soup = BeautifulSoup(html, "html.parser")
    edicoes = []
    for link in soup.select("a.title"):
        titulo = link.text.strip()
        href = link.get("href")
        url_ed = urljoin(archive_url, href) if href else None
        match = re.search(r"\d{4}", titulo)
        ano = match.group() if match else "desconhecido"
        edicoes.append({"ano": ano, "titulo": titulo, "url": url_ed})
    return edicoes


def get_artigos(edicao_url: str) -> list[str]:
    """Retornar lista de URLs de artigos para uma edição."""
    html = get_html(edicao_url)
    soup = BeautifulSoup(html, "html.parser")
    artigos: list[str] = []
    for link in soup.select("div.title a"):
        href = link.get("href")
        if href:
            artigos.append(urljoin(edicao_url, href))
    return artigos


def get_dados_artigo(url: str, ano: int | str) -> dict:
    """Extrair título, resumo e palavras-chave de uma página de artigo."""
    html = get_html(url)
    soup = BeautifulSoup(html, "html.parser")
    titulo_el = soup.select_one("h1.page_title")
    titulo = titulo_el.text.strip() if titulo_el else ""
    resumo_el = soup.select_one(".item.abstract")
    resumo = resumo_el.text.strip() if resumo_el else ""
    palavras_el = soup.select_one(".item.keywords")
    palavras = palavras_el.text.strip() if palavras_el else ""
    return {"ano": ano, "titulo": titulo, "resumo": resumo, "palavras_chave": palavras, "url": url}


def consolidar(site_name: str, save_dir: Path, out_dir: Path, year_start: int, year_end: int) -> Path:
    """Consolidar arquivos anuais gerados pelo scraper em um único arquivo Excel com abas por ano.

    Retorna o Path do arquivo de saída.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    arquivo_saida = out_dir / f"{site_name.lower()}_artigos_consolidados.xlsx"
    with pd.ExcelWriter(arquivo_saida, engine="openpyxl") as writer:
        for ano in range(year_start, year_end + 1):
            nome_arquivo = save_dir / f"{site_name.lower()}_artigos_{ano}.xlsx"
            if nome_arquivo.exists():
                abas = pd.read_excel(nome_arquivo, sheet_name=None, engine="openpyxl")
                for aba_nome, df in abas.items():
                    df.columns = [normalizar_nome_coluna(c) for c in df.columns]
                    sheet_name = str(ano)[:31]
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # ignora anos sem arquivo
                continue
    return arquivo_saida

# -----------------------
# Funções de limpeza e tratamento de dados
# -----------------------
def normalizar_nome_coluna(nome: object) -> str:
    """Transformar um cabeçalho em minúsculas, sem acentos e com sublinhados."""
    texto = unicodedata.normalize("NFKD", str(nome))
    texto = "".join(letra for letra in texto if not unicodedata.combining(letra))
    return re.sub(r"[^a-zA-Z0-9]+", "_", texto.lower()).strip("_")


def limpar_texto(texto: object) -> str:
    """Preparar um texto para a busca posterior de termos da BNCC."""
    if pd.isna(texto):
        return ""

    texto_limpo = unicodedata.normalize("NFKD", str(texto).lower())
    texto_limpo = "".join(
        letra for letra in texto_limpo if not unicodedata.combining(letra)
    )
    texto_limpo = re.sub(r"[^a-z0-9\s]", " ", texto_limpo)
    texto_limpo = re.sub(r"\d+", " ", texto_limpo)
    return re.sub(r"\s+", " ", texto_limpo).strip()


def identificar_registro_nao_cientifico(titulo_limpo: str) -> str:
    """Informar por que um título não será tratado como artigo científico."""
    if re.search(r"elementos pre textuais", titulo_limpo):
        return "elementos pré-textuais"
    if re.search(r"\beditorial\b", titulo_limpo):
        return "editorial"
    if re.search(r"^abertura do .*workshop", titulo_limpo):
        return "abertura do evento"
    if re.search(r"^apresentacao e organizacao", titulo_limpo):
        return "apresentação e organização"
    return ""

# -----------------------
# Funções de consulta e análise de dados
# -----------------------
def carregar_eixos_bncc(caminho: object) -> dict[str, dict[str, object]]:
    """Carregar e normalizar o vocabulário dos eixos da BNCC."""
    with open(caminho, encoding="utf-8") as arquivo:
        configuracao = yaml.safe_load(arquivo)

    eixos = configuracao.get("eixos", {})
    for dados_eixo in eixos.values():
        dados_eixo["termos"] = [limpar_texto(termo) for termo in dados_eixo["termos"]]
        dados_eixo["bigramas"] = [
            limpar_texto(bigrama) for bigrama in dados_eixo["bigramas"]
        ]
    return eixos


def selecionar_descritores_relevantes(
    eixos: dict[str, dict[str, object]],
    termos_relevantes: set[str],
    bigramas_relevantes: set[str],
) -> dict[str, dict[str, object]]:
    """Manter no vocabulário BNCC somente descritores relevantes no corpus."""
    selecionados: dict[str, dict[str, object]] = {}
    for codigo, dados in eixos.items():
        selecionados[codigo] = {
            "nome": dados["nome"],
            "termos": [termo for termo in dados["termos"] if termo in termos_relevantes],
            "bigramas": [
                bigrama for bigrama in dados["bigramas"]
                if bigrama in bigramas_relevantes
            ],
        }
    return selecionados


def encontrar_evidencias_bncc(
    texto_limpo: str, eixos: dict[str, dict[str, object]]
) -> dict[str, dict[str, list[str]]]:
    """Retornar os termos encontrados em cada eixo para um texto normalizado."""
    evidencias: dict[str, dict[str, list[str]]] = {}

    for codigo_eixo, dados_eixo in eixos.items():
        termos_encontrados = []
        for termo in dados_eixo["termos"]:
            padrao = rf"\b{re.escape(termo)}\b"
            if re.search(padrao, texto_limpo):
                termos_encontrados.append(termo)

        bigramas_encontrados = []
        for bigrama in dados_eixo["bigramas"]:
            padrao = rf"\b{re.escape(bigrama)}\b"
            if re.search(padrao, texto_limpo):
                bigramas_encontrados.append(bigrama)

        if termos_encontrados or bigramas_encontrados:
            evidencias[codigo_eixo] = {
                "termos": termos_encontrados,
                "bigramas": bigramas_encontrados,
            }

    return evidencias

# -----------------------
# Funções para geração de nuvens de palavras
# -----------------------
def criar_paleta_unb() -> list[str]:
    """Retornar a paleta de cores do estilo visual da UnB."""
    return [
        "#003366",
        "#006633",
        "#C89B3C",
        "#A23B3B",
        "#7A5A3A",
    ]


def cor_unb(word: str, font_size: int, position: tuple[float, float], orientation, random_state=None, **kwargs) -> str:
    """Escolher uma cor da paleta UnB para a nuvem de palavras."""
    return random.choice(criar_paleta_unb())


def montar_frequencias_palavras(freq_df: pd.DataFrame, coluna: str, evento: str) -> dict[str, int]:
    """Agrupar frequências por evento para gerar nuvens de palavras."""
    return (
        freq_df.loc[freq_df["evento"] == evento]
        .groupby(coluna)["frequencia"]
        .sum()
        .sort_values(ascending=False)
        .to_dict()
    )


def gerar_nuvem_palavras(
    frequencias: dict[str, int],
    caminho_saida: str | Path,
    *,
    width: int = 1400,
    height: int = 850,
    max_words: int = 80,
    max_font_size: int = 170,
    min_font_size: int = 12,
    random_state: int = 42,
) -> Path:
    """Gerar uma imagem de nuvem de palavras e salvar em arquivo PNG."""
    caminho_saida = Path(caminho_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)

    wordcloud = WordCloud(
        width=width,
        height=height,
        background_color=None,
        mode="RGBA",
        max_words=max_words,
        collocations=False,
        prefer_horizontal=0.92,
        relative_scaling=0.25,
        max_font_size=max_font_size,
        min_font_size=min_font_size,
        random_state=random_state,
        margin=3,
    ).generate_from_frequencies(frequencias)

    wordcloud = wordcloud.recolor(color_func=cor_unb, random_state=random_state)

    plt.figure(figsize=(12, 7))
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.tight_layout(pad=0)
    plt.savefig(caminho_saida, transparent=True, dpi=300, bbox_inches="tight", pad_inches=0)
    plt.close()

    return caminho_saida
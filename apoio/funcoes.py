"""Funções simples compartilhadas pelos notebooks do TCC."""

import re
import unicodedata

import pandas as pd
import yaml


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

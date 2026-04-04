#!/usr/bin/env python3
from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sol.sbc.org.br/index.php"
BRACIS_SLUG = "bracis"
ANOS_ALVO = {2023, 2024, 2025}
REQUEST_TIMEOUT = 30
SLEEP_SECONDS = 0.2
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
)


@dataclass(frozen=True)
class Edicao:
    ano: int
    titulo: str
    link: str


def baixar_soup(url: str, session: requests.Session) -> BeautifulSoup:
    resposta = session.get(url, timeout=REQUEST_TIMEOUT)
    resposta.raise_for_status()
    return BeautifulSoup(resposta.text, "html.parser")


def extrair_ano(texto: str) -> int | None:
    if not texto:
        return None
    match = re.search(r"\b(20\d{2})\b", texto)
    return int(match.group(1)) if match else None


def listar_edicoes_bracis(
    session: requests.Session, anos_alvo: set[int]
) -> list[Edicao]:
    archive_url = f"{BASE_URL}/{BRACIS_SLUG}/issue/archive"
    soup = baixar_soup(archive_url, session)
    edicoes: list[Edicao] = []

    for bloco in soup.select("div.obj_issue_summary"):
        tag_titulo = bloco.select_one("a.title")
        if not tag_titulo:
            continue

        titulo_edicao = tag_titulo.get_text(" ", strip=True)
        ano_edicao = extrair_ano(titulo_edicao)

        if ano_edicao not in anos_alvo:
            continue

        link_edicao = urljoin(archive_url, tag_titulo.get("href", "").strip())
        edicoes.append(Edicao(ano=ano_edicao, titulo=titulo_edicao, link=link_edicao))

    edicoes.sort(key=lambda item: (item.ano, item.titulo), reverse=True)
    return edicoes


def listar_artigos_edicao(url_edicao: str, session: requests.Session) -> list[dict[str, str]]:
    soup = baixar_soup(url_edicao, session)
    artigos: list[dict[str, str]] = []
    links_vistos: set[str] = set()

    for bloco in soup.select("div.obj_article_summary"):
        tag_artigo = bloco.select_one("div.title a")
        if not tag_artigo:
            continue

        link_artigo = urljoin(url_edicao, tag_artigo.get("href", "").strip())
        if not link_artigo or link_artigo in links_vistos:
            continue

        links_vistos.add(link_artigo)
        artigos.append(
            {
                "titulo_edicao": tag_artigo.get_text(" ", strip=True),
                "link_artigo": link_artigo,
            }
        )

    return artigos


def extrair_titulo_resumo(
    url_artigo: str, titulo_fallback: str, session: requests.Session
) -> tuple[str, str]:
    soup = baixar_soup(url_artigo, session)

    tag_titulo = soup.select_one("h1.page_title")
    titulo = tag_titulo.get_text(" ", strip=True) if tag_titulo else titulo_fallback

    resumo = ""
    tag_resumo = soup.select_one("div.item.abstract")
    if tag_resumo:
        tag_label = tag_resumo.select_one("h3.label")
        if tag_label:
            tag_label.decompose()
        resumo = tag_resumo.get_text(" ", strip=True)

    return titulo, resumo


def coletar_trabalhos_bracis(
    anos_alvo: set[int] = ANOS_ALVO, sleep_seconds: float = SLEEP_SECONDS
) -> pd.DataFrame:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})

    registros: list[dict[str, str | int]] = []
    edicoes = listar_edicoes_bracis(session, anos_alvo)

    print(f"Edições BRACIS encontradas para {sorted(anos_alvo)}: {len(edicoes)}")

    for edicao in edicoes:
        print(f"- {edicao.ano}: {edicao.titulo}")
        artigos = listar_artigos_edicao(edicao.link, session)
        print(f"  Artigos na edicao: {len(artigos)}")

        total_artigos = len(artigos)
        for indice, artigo in enumerate(artigos, start=1):
            time.sleep(sleep_seconds)
            try:
                titulo, resumo = extrair_titulo_resumo(
                    artigo["link_artigo"], artigo["titulo_edicao"], session
                )
            except requests.RequestException as erro:
                print(f"  [aviso] erro em {artigo['link_artigo']}: {erro}")
                titulo = artigo["titulo_edicao"]
                resumo = ""

            registros.append(
                {
                    "Conferencia": "BRACIS",
                    "Ano": edicao.ano,
                    "Edicao": edicao.titulo,
                    "Titulo": titulo,
                    "Resumo": resumo,
                    "Link": artigo["link_artigo"],
                }
            )

            if indice % 25 == 0 or indice == total_artigos:
                print(f"  Progresso: {indice}/{total_artigos}")

    df = pd.DataFrame(
        registros,
        columns=["Conferencia", "Ano", "Edicao", "Titulo", "Resumo", "Link"],
    )

    if not df.empty:
        df = (
            df.drop_duplicates(subset=["Ano", "Titulo", "Link"])
            .sort_values(["Ano", "Titulo"], ascending=[False, True])
            .reset_index(drop=True)
        )

    return df


if __name__ == "__main__":
    df_bracis = coletar_trabalhos_bracis()
    print("\nDataFrame consolidado (amostra):")
    print(df_bracis.head(10).to_string(index=False))
    print(f"\nTotal de registros: {len(df_bracis)}")

    arquivo_saida = "bracis_trabalhos_2023_2025.csv"
    df_bracis.to_csv(arquivo_saida, index=False)
    print(f"CSV salvo em: {arquivo_saida}")

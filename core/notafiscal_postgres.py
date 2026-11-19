"""Persistência de campos de NFS-e usando uma conexão PostgreSQL DB-API."""

import os
import json
from pathlib import Path
import psycopg
from dotenv import load_dotenv

load_dotenv()

from core.html_parser import CampoHtml, extrair_campos_html


def _valor_unico(campos: list[CampoHtml], secao: str, label: str) -> str:
    valores = [
        campo["valor"]
        for campo in campos
        if campo["secao"] == secao and campo["label"] == label
    ]
    if len(valores) != 1 or not valores[0] or valores[0] == "-":
        raise ValueError(f"Esperado um valor para {secao} / {label}")
    return valores[0]


def inserir_nota(conexao, campos: list[CampoHtml]) -> None:
    """Insere uma nota; a transação e o fechamento pertencem ao chamador."""
    chave = _valor_unico(campos, "Identificação da NFS-e", "Chave de acesso")
    numero = _valor_unico(campos, "Identificação do DPS", "Número da Nota")
    with conexao.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO financeiro.tb_notafiscal (chave_acesso, numero_nfse, campos_html)
            VALUES (%s, %s, %s::jsonb)
            """,
            (chave, numero, json.dumps(campos, ensure_ascii=False)),
        )


def importar_htmls(conexao, diretorio: str | Path) -> int:
    """Insere os HTMLs de um diretório, sem efetuar commit ou rollback."""
    diretorio = Path(diretorio)
    if not diretorio.is_dir():
        raise NotADirectoryError(f"Diretório de HTMLs não encontrado: {diretorio}")
    arquivos = sorted(diretorio.glob("*.html"))
    if not arquivos:
        raise ValueError(f"Nenhum arquivo .html encontrado em {diretorio}")
    for arquivo in arquivos:
        inserir_nota(conexao, extrair_campos_html(arquivo))
    return len(arquivos)

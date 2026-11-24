"""Extração dos campos exibidos na visualização HTML da NFS-e Nacional."""

from pathlib import Path
from typing import TypedDict
from collections import defaultdict

from bs4 import BeautifulSoup
from bs4.element import Tag


class CampoHtml(TypedDict):
    secao: str
    #campo: str
    label: str
    valor: str

fields = defaultdict(list)

def get_fields():
    fields["Número da Nota"].append("numero")
    fields["Código de Verificação"].append("codigoverificacao")
    fields["Data de geração"].append("dataemissao")
    fields[""].append("naturezaoperacao")
    fields[""].append("regimeespecialtributacao")
    fields[""].append("optantesimplesnacional")
    fields[""].append("incentivocultural")
    fields["Data de geração"].append("competencia")
    fields[""].append("valorservicos")
    fields[""].append("issretido")
    fields[""].append("valoriss")
    fields[""].append("basecalculo")
    fields[""].append("aliquota")
    fields[""].append("valorliquidonfse")
    fields[""].append("valorissretido")
    fields[""].append("itemlistaservico")
    fields[""].append("codigotributacaomunicipio")
    fields[""].append("discriminacao")
    fields[""].append("municipioprestacaoservico")
    fields[""].append("valorcredito")
    fields[""].append("cnpjprestador")
    fields[""].append("inscricaomunicipalprestador")
    fields[""].append("razaosocialprestador")
    fields[""].append("enderecoprestador")
    fields[""].append("numeroprestador")
    fields[""].append("bairroprestador")
    fields[""].append("cidadeprestador")
    fields[""].append("estadoprestador")
    fields[""].append("cepprestador")
    fields[""].append("telefoneprestador")
    fields[""].append("emailprestador")
    fields[""].append("cpftomador")
    fields[""].append("razaosocialtomador")
    fields[""].append("enderecotomador")
    fields[""].append("numerotomador")
    fields[""].append("bairrotomador")
    fields[""].append("cidadetomador")
    fields[""].append("estadotomador")
    fields[""].append("ceptomador")
    fields[""].append("telefonetomador")
    fields[""].append("emailtomador")
    fields[""].append("codigomunicipiogerador")
    fields[""].append("estadomunicipiogerador")
    fields[""].append("cnpjtomador")
    fields[""].append("datacancelamento")
    fields[""].append("motivocancelamento")
    fields[""].append("inscricaomunicipaltomador")
    fields[""].append("identificacaotomador")
    fields["Chave de acesso"].append("chaveacesso")
    fields[""].append("situacaoadn")
    fields[""].append("codigocnae")
    fields[""].append("codigonbs")
    fields[""].append("complementoprestador")
    fields[""].append("codigoindicadorfinalidadenfse")
    fields[""].append("codigoindicadoroperacaousoconsumopessoal")
    fields[""].append("codigoindicadoroperacao")
    fields[""].append("inddest")
    fields[""].append("cst")
    fields[""].append("codigoclasstrib")
    fields[""].append("complementotomador")
    fields[""].append("codigomunicipioprestador")
    fields[""].append("codigomunicipiotomador")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")
    fields[""].append("")

    return fields


def _texto(elemento: Tag) -> str:
    if elemento is None:
        return ""
    return " ".join(elemento.get_text(" ", strip=True).split())


def extrair_campos_html(caminho: str | Path) -> list[CampoHtml]:
    """Retorna todos os rótulos e valores, preservando a seção e a ordem."""
    caminho = Path(caminho)
    soup = BeautifulSoup(caminho.read_text(encoding="utf-8"), "html.parser")
    principal = soup.select_one("#main-content")
    if principal is None:
        raise ValueError(f"Conteúdo principal da NFS-e não encontrado em {caminho}")

    campos: list[CampoHtml] = []
    for label in principal.select("label.control-label"):
        painel = label.find_parent(class_="panelExterno") if label.find_parent(class_="panelExterno") is not None else label.find_parent(class_="sujeito")
        titulo = painel.select_one(".panel-title") if isinstance(painel, Tag) else None
        seguinte = label.find_next_sibling()
        
        if (titulo is None or not isinstance(seguinte, Tag)) and ("Autor" not in text):
            raise ValueError(f"Rótulo sem seção ou valor em {caminho}: {_texto(label)}")
        valor = (
            seguinte
            if seguinte.name == "span" and "form-control-static" in seguinte.get("class", [])
            else seguinte.select_one(".form-control-static.texto")
        )
        if valor is None:
            raise ValueError(f"Valor não encontrado em {caminho}: {_texto(label)}")
        campos.append({"secao": _texto(titulo), "label": _texto(label), "valor": _texto(valor)})

    if not campos:
        raise ValueError(f"Nenhum campo de NFS-e encontrado em {caminho}")
    return campos


if __name__ == "__main__":
    import sys

    caminho = "/Users/viniciusnunes/desenvolvimento/emissor_nfse/downloads/CLIENTE_DESCONHECIDO/emitidas/2026/11/cancelada/htmls/23044002223674714000180000000000008426116201372416.html"

    try:
        campos = extrair_campos_html(caminho)
        for campo in campos:
            print(campo)
    except ValueError as e:
        print(f"Erro ao processar {caminho}: {e}")
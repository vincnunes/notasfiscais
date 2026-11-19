import json
from unittest.mock import MagicMock

import pytest

from core.html_parser import extrair_campos_html
from core.notafiscal_postgres import importar_htmls, inserir_nota

HTML = """
<div id="main-content">
  <div class="panelExterno">
    <h3 class="panel-title">Identificação da NFS-e</h3>
    <div class="form-group">
      <label class="control-label"><span>Chave de acesso</span></label>
      <span class="form-control-static texto">123</span>
    </div>
    <div class="form-group">
      <label class="control-label">Versão</label>
      <span class="form-control-static texto">1.01</span>
    </div>
  </div>
  <div class="panelExterno">
    <h3 class="panel-title">Identificação do DPS</h3>
    <div class="form-group">
      <label class="control-label">Número da Nota</label>
      <span class="form-control-static texto">73</span>
      <label class="control-label">Número</label>
      <span class="form-control-static texto">311</span>
    </div>
    <div class="form-group">
      <label class="control-label">Versão</label>
      <span class="form-control-static texto">1.02</span>
    </div>
  </div>
  <div class="panelExterno">
    <h3 class="panel-title">Tributação Municipal</h3>
    <div class="form-group">
      <label class="control-label">Valor do Serviço</label>
      <div class="input-group">
        <span class="input-group-addon">R$</span>
        <span class="form-control-static texto numero"> 2.899,80 </span>
      </div>
    </div>
    <div class="form-group">
      <label class="control-label">Observação</label>
      <span class="form-control-static texto">linha 1<br>linha 2</span>
    </div>
  </div>
</div>
"""


def test_extrai_pares_por_secao_sem_perder_labels_repetidos(tmp_path):
    caminho = tmp_path / "nota.html"
    caminho.write_text(HTML, encoding="utf-8")
    campos = extrair_campos_html(caminho)

    assert campos == [
        {"secao": "Identificação da NFS-e", "label": "Chave de acesso", "valor": "123"},
        {"secao": "Identificação da NFS-e", "label": "Versão", "valor": "1.01"},
        {"secao": "Identificação do DPS", "label": "Número da Nota", "valor": "73"},
        {"secao": "Identificação do DPS", "label": "Número", "valor": "311"},
        {"secao": "Identificação do DPS", "label": "Versão", "valor": "1.02"},
        {"secao": "Tributação Municipal", "label": "Valor do Serviço", "valor": "2.899,80"},
        {"secao": "Tributação Municipal", "label": "Observação", "valor": "linha 1 linha 2"},
    ]


def test_html_invalido_ou_valor_ausente_gera_erro(tmp_path):
    caminho = tmp_path / "nota.html"
    caminho.write_text("<html></html>", encoding="utf-8")
    with pytest.raises(ValueError, match="Conteúdo principal"):
        extrair_campos_html(caminho)
    caminho.write_text(HTML.replace('class="form-control-static texto">123', 'class="outro">123'))
    with pytest.raises(ValueError, match="Valor não encontrado"):
        extrair_campos_html(caminho)


def test_preserva_labels_repetidos_na_mesma_secao_e_valor_vazio(tmp_path):
    caminho = tmp_path / "nota.html"
    repetido = """
    <div class="form-group">
      <label class="control-label">Observação</label>
      <span class="form-control-static texto"></span>
    </div>
    """
    caminho.write_text(HTML.replace("</div>\n</div>\n", repetido + "</div>\n</div>\n"))
    campos = extrair_campos_html(caminho)
    observacoes = [campo["valor"] for campo in campos if campo["label"] == "Observação"]
    assert observacoes == ["linha 1 linha 2", ""]


def test_importa_com_parametros_e_deixa_transacao_para_chamador(tmp_path):
    (tmp_path / "nota.html").write_text(HTML, encoding="utf-8")
    conexao = MagicMock()
    cursor = conexao.cursor.return_value.__enter__.return_value

    assert importar_htmls(conexao, tmp_path) == 1
    sql, parametros = cursor.execute.call_args.args
    assert "financeiro.tb_notafiscal" in sql
    assert parametros[:2] == ("123", "73")
    assert json.loads(parametros[2]) == extrair_campos_html(tmp_path / "nota.html")
    conexao.commit.assert_not_called()
    conexao.rollback.assert_not_called()


def test_erros_de_importacao_e_banco_sao_propagados(tmp_path):
    conexao = MagicMock()
    with pytest.raises(ValueError, match="Nenhum arquivo"):
        importar_htmls(conexao, tmp_path)
    with pytest.raises(NotADirectoryError):
        importar_htmls(conexao, tmp_path / "ausente")
    with pytest.raises(ValueError, match="Chave de acesso"):
        inserir_nota(conexao, [])
    (tmp_path / "nota.html").write_text(HTML, encoding="utf-8")
    cursor = conexao.cursor.return_value.__enter__.return_value
    cursor.execute.side_effect = RuntimeError("erro SQL")
    with pytest.raises(RuntimeError, match="erro SQL"):
        importar_htmls(conexao, tmp_path)

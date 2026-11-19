# Importação de HTMLs de NFS-e

Foram analisados 17 HTMLs de visualização do Emissor Nacional, com 81 ou 83
rótulos por arquivo em 11 seções: identificação da NFS-e e do DPS, emitente,
tomador, tributação municipal e federal, serviço prestado, informações
complementares, outras informações, IBS/CBS e total dos tributos. Alguns
campos são opcionais (como CPF ou CNPJ do tomador); nomes como `Versão` e
`CNPJ` aparecem em seções diferentes.

`extrair_campos_html` devolve uma lista de objetos `{"secao": "...",
"label": "...", "valor": "..."}` na ordem do documento. Valores são strings,
inclusive números, datas, `-` e textos vazios; espaços e quebras de linha são
normalizados. A seção e a lista preservam rótulos repetidos. Símbolos de moeda
e porcentagem que aparecem em elementos separados não são acrescentados ao
valor. Campos ausentes não são criados. HTMLs sem estrutura ou sem valor de
um rótulo reconhecido geram erro, em vez de serem importados parcialmente.

## Proposta de armazenamento

[tb_notafiscal.sql](tb_notafiscal.sql) propõe uma tabela nova com:

| Coluna | Tipo | Conteúdo |
|---|---|---|
| `id` | `bigint` | Identificador interno |
| `chave_acesso` | `text`, único | Chave exibida na identificação da NFS-e |
| `numero_nfse` | `text` | Número da nota, distinto do número da DPS |
| `campos_html` | `jsonb` | Lista completa de seção, rótulo e valor textual |
| `criado_em` | `timestamptz` | Instante da inserção |

Para consultas financeiras estruturadas, sugere-se avaliar colunas adicionais:
`numero_dps` e `serie_dps` como `text`; `data_geracao` e `data_emissao_dps`
como `timestamptz`; CPF/CNPJ, nomes, situação e descrição do serviço como
`text`; `valor_servico`, base de cálculo, ISSQN, IBS, CBS e retenções como
`numeric(18,2)`; e alíquotas como `numeric` com escala adequada. É necessário
definir conversão, precisão e tratamento de valores ausentes antes de adicionar
essas colunas; os valores originais continuam disponíveis em `campos_html`.

O SQL é uma **proposta**, não uma migração: revise-o e adapte-o à tabela e ao
schema existentes antes de aplicá-lo. O código espera pelo menos as colunas
`chave_acesso`, `numero_nfse` e `campos_html` com tipos compatíveis e que
eventuais outras colunas obrigatórias tenham valores padrão. Não cria nem altera
tabelas. A chave única proposta rejeita duplicatas, sem sobrescrever dados.

## Uso

Instale um driver PostgreSQL DB-API opcional, por exemplo
`pip install 'psycopg[binary]>=3.2,<4'`. Prepare o banco a partir da proposta
revisada e configure `DATABASE_URL` no ambiente, sem incluir credenciais no código.
Em seguida:

```python
import os
import psycopg

from core.notafiscal_postgres import importar_htmls

diretorio = "/caminho/para/htmls"
with psycopg.connect(os.environ["DATABASE_URL"]) as conexao:
    quantidade = importar_htmls(conexao, diretorio)
print(f"{quantidade} notas importadas")
```

O contexto da conexão confirma a transação ao concluir ou faz rollback em
caso de erro; `importar_htmls` não faz commit nem rollback. Sem esse contexto,
o chamador deve gerenciar a transação. Erros de leitura, validação ou banco são
propagados. A importação não percorre subdiretórios e falha quando não encontra
arquivos `.html`. Uma duplicata rejeitada pelo banco interrompe o lote e, no
exemplo, desfaz toda a transação.

Os HTMLs e os campos extraídos podem conter dados fiscais e pessoais sensíveis.
Proteja os arquivos e o banco com controle de acesso e retenção apropriados.
O HTML completo não é armazenado: ele pode conter dados de sessão do portal.

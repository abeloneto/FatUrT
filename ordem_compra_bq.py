"""
ordem_compra_bq.py — busca a ORDEM DE COMPRA (nota fiscal de compra) no BigQuery
para enriquecer o faturamento do SISTEMA SOMBRA (Supabase).

Demanda temporária: o sombra roda até julho. Este módulo é isolado de propósito
— quando o sombra for aposentado, basta apagar este arquivo e a chamada a ele.

Cadeia de ligação (a nota de VENDA é o elo entre os dois mundos):
  nota_venda (Supabase OS_NF.nf)  ==  SC5.C5_NOTA
    -> SC5.C5_NUM  ==  OS.NUMERO_PEDIDO_VENDA
    -> OS.UUID     ==  TAREFAS.OS_ID
    -> TAREFAS.UUID == INSUMOS.TAREFA_ID
    -> INSUMOS.BAIXAS (JSON) -> nota_fiscal de compra (ignorando status 'Estornado')

A nota de compra é agregada por NOTA DE VENDA (equivalente a por OS).

Requisitos: pip install google-cloud-bigquery
"""

from google.cloud import bigquery
from google.oauth2 import service_account

CAMINHO_CHAVE = "credenciais/chave_bigquery.json"  # use a chave NOVA
PROJECT_ID    = "gcp-maas-proj-manutencao"

_credenciais = service_account.Credentials.from_service_account_file(
    CAMINHO_CHAVE,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
_client = bigquery.Client(credentials=_credenciais, project=PROJECT_ID)


# Para cada (nota de venda + PEÇA), agrega as notas de compra daquele insumo,
# descartando baixas estornadas. UNNEST abre o array JSON do campo BAIXAS.
# A descrição é normalizada (sem acento, maiúscula, espaço único) para casar
# com a descrição vinda do Supabase sombra.
SQL_ORDEM_COMPRA = """
SELECT
  LTRIM(TRIM(sc5.C5_NOTA), '0') AS nota_venda,
  TRIM(REGEXP_REPLACE(
        NORMALIZE_AND_CASEFOLD(prod.DESCRICAO, NFD),
        r'\\pM', '')) AS peca_norm,
  STRING_AGG(
      DISTINCT JSON_EXTRACT_SCALAR(baixa, '$.nota_fiscal'),
      ', '
  ) AS notas_compra
FROM `gcp-maas-proj-manutencao.silver.SC5_PedidoVendas` sc5
JOIN `gcp-maas-proj-manutencao.silver.SILVER_SIAN_SUPABASE_OS` o
     ON TRIM(o.NUMERO_PEDIDO_VENDA) = TRIM(sc5.C5_NUM)
JOIN `gcp-maas-proj-manutencao.silver.SILVER_SIAN_SUPABASE_TAREFAS` t
     ON t.OS_ID = o.UUID
JOIN `gcp-maas-proj-manutencao.silver.SILVER_SIAN_SUPABASE_INSUMOS` i
     ON i.TAREFA_ID = t.UUID
LEFT JOIN `gcp-maas-proj-manutencao.silver.SILVER_SIAN_SUPABASE_PRODUTOS` prod
     ON i.PRODUTO_ID = prod.UUID,
     UNNEST(JSON_EXTRACT_ARRAY(i.BAIXAS)) AS baixa
WHERE TRIM(sc5.C5_FILIAL) = '030101'
  AND LTRIM(TRIM(sc5.C5_NOTA), '0') IN UNNEST(@notas_venda)
  AND JSON_EXTRACT_SCALAR(baixa, '$.status') != 'Estornado'
  AND JSON_EXTRACT_SCALAR(baixa, '$.nota_fiscal') IS NOT NULL
GROUP BY nota_venda, peca_norm
"""


def normalizar_nota(n):
    """Padroniza um número de nota removendo zeros à esquerda e espaços.

    Resolve a diferença entre o Supabase (inteiro, ex: 147) e a SC5 do Protheus
    (string com padding variável, ex: '000000147'). Ambos viram '147'.
    Independe do número de zeros, então é robusto a variações de padding.
    Use esta mesma função no app ao consultar o dicionário de obter_ordens_compra.
    """
    if n is None:
        return ''
    s = str(n).strip()
    if not s or s == '-':
        return ''
    # remove eventual ".0" de notas que vieram como float do Supabase
    if s.endswith('.0'):
        s = s[:-2]
    # remove zeros à esquerda; se sobrar vazio (nota "000"), devolve vazio
    return s.lstrip('0')


def normalizar_peca(desc):
    """Normaliza a descrição de uma peça para casar entre sombra e silver.

    Deve produzir o MESMO resultado que o SQL (NORMALIZE_AND_CASEFOLD + remoção
    de acentos): minúsculas, sem acento, espaços colapsados. Use no app ao
    consultar o dicionário.
    """
    import unicodedata, re
    if not desc:
        return ''
    s = unicodedata.normalize('NFD', str(desc))
    s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')  # tira acento
    s = re.sub(r'\s+', ' ', s).strip().casefold()
    return s


def obter_ordens_compra(notas_venda):
    """
    Recebe uma lista de notas fiscais de VENDA (em qualquer formato) e devolve
    um dicionário casando POR PEÇA:
        { (nota_venda_normalizada, peca_normalizada): "nf_compra1, nf_compra2", ... }

    IMPORTANTE: ao consultar no app, use a chave
        (normalizar_nota(nota), normalizar_peca(descricao))
    """
    notas = sorted({normalizar_nota(n) for n in notas_venda})
    notas = [n for n in notas if n]
    if not notas:
        return {}

    cfg = bigquery.QueryJobConfig(query_parameters=[
        bigquery.ArrayQueryParameter("notas_venda", "STRING", notas),
    ])

    resultado = {}
    try:
        for r in _client.query(SQL_ORDEM_COMPRA, job_config=cfg).result():
            nv = r["nota_venda"]
            pc = r["peca_norm"]
            if nv and pc:
                resultado[(nv, pc)] = r["notas_compra"] or '-'
    except Exception as e:
        # Em caso de falha no BigQuery, não derruba o faturamento do sombra:
        # devolve vazio e o relatório sai sem a coluna de compra (com '-').
        print(f"[ordem_compra_bq] Falha ao buscar ordens de compra: {e}")
        return {}

    return resultado
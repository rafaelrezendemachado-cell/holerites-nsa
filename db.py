"""
db.py — Conexao com o Supabase.

O cliente eh criado uma unica vez por sessao do Streamlit
(via @st.cache_resource). Em scripts soltos, usar get_client() direto.
"""

from functools import lru_cache

from supabase import Client, create_client


def _carregar_secrets():
    """Tenta pegar credenciais do Streamlit; se nao, le do arquivo local."""
    try:
        import streamlit as st  # opcional fora do app
        url = st.secrets["supabase_url"]
        key = st.secrets["supabase_service_key"]
        return url, key
    except Exception:
        pass
    # Fallback: ler do arquivo local
    import tomllib
    from pathlib import Path
    secrets_path = Path(__file__).parent / ".streamlit" / "secrets.toml"
    with open(secrets_path, "rb") as f:
        data = tomllib.load(f)
    return data["supabase_url"], data["supabase_service_key"]


@lru_cache(maxsize=1)
def get_client() -> Client:
    """Cliente Supabase reusado dentro do processo."""
    url, key = _carregar_secrets()
    return create_client(url, key)


# ============================================================
# Helpers de leitura
# ============================================================

def listar_lojas():
    return get_client().table("lojas").select("*").eq("ativo", True).order("nome").execute().data


def loja_por_codigo(codigo: str):
    res = get_client().table("lojas").select("*").eq("codigo", codigo).limit(1).execute().data
    return res[0] if res else None


def listar_bancos(loja_id: str, ativos_apenas: bool = True):
    q = get_client().table("bancos").select("*").eq("loja_id", loja_id).order("ordem")
    if ativos_apenas:
        q = q.eq("ativo", True)
    return q.execute().data


def listar_funcionarias(loja_id: str, ativas_apenas: bool = True):
    q = get_client().table("funcionarias").select("*, banco:bancos(*)").eq("loja_id", loja_id).order("nome")
    if ativas_apenas:
        q = q.eq("ativa", True)
    return q.execute().data


def listar_meses(loja_id: str):
    return get_client().table("meses").select("*").eq("loja_id", loja_id) \
        .order("ano", desc=True).order("mes", desc=True).execute().data


def holerites_do_mes(mes_id: str):
    return get_client().table("holerites").select(
        "*, funcionaria:funcionarias(*), banco:bancos(*)"
    ).eq("mes_id", mes_id).execute().data


# ============================================================
# Helpers de escrita
# ============================================================

def upsert_funcionaria(loja_id: str, nome: str, banco_id: str | None,
                       comissionada: bool = False, ativa: bool = True):
    return get_client().table("funcionarias").insert({
        "loja_id": loja_id, "nome": nome, "banco_id": banco_id,
        "comissionada": comissionada, "ativa": ativa,
    }).execute().data


def upsert_banco(loja_id: str, nome: str, ordem: int = 0):
    return get_client().table("bancos").insert({
        "loja_id": loja_id, "nome": nome, "ordem": ordem,
    }).execute().data


def upsert_mes(loja_id: str, ano: int, mes: int, data_pagamento):
    """Cria ou retorna o registro do mes."""
    existente = get_client().table("meses").select("*") \
        .eq("loja_id", loja_id).eq("ano", ano).eq("mes", mes) \
        .limit(1).execute().data
    if existente:
        return existente[0]
    return get_client().table("meses").insert({
        "loja_id": loja_id, "ano": ano, "mes": mes,
        "data_pagamento": data_pagamento.isoformat(),
    }).execute().data[0]


def excluir_mes(mes_id: str):
    """Exclui o mes (cascade derruba todos os holerites dele)."""
    return get_client().table("meses").delete().eq("id", mes_id).execute()


def atualizar_holerite(holerite_id: str, dados: dict):
    return get_client().table("holerites").update(dados).eq("id", holerite_id).execute()


def salvar_holerites_em_lote(mes_id: str, registros: list[dict]):
    """
    Substitui completamente os holerites do mes.
    `registros` = lista de dicts com:
      funcionaria_id, banco_id, comissionada, motivacional, he, domingo,
      vales, uniodonto, plano_saude, emprestimo, vale_transporte, liquido
    """
    cli = get_client()
    cli.table("holerites").delete().eq("mes_id", mes_id).execute()
    if not registros:
        return []
    for r in registros:
        r["mes_id"] = mes_id
    return cli.table("holerites").insert(registros).execute().data

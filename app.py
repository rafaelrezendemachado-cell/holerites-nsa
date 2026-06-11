"""
app.py — Interface Streamlit do app de holerites.

Telas:
  - Login
  - Configuracoes (bancos)
  - Funcionarias (tabela editavel)
  - Processar holerite (placeholder Fase 3)
  - Meses (placeholder Fase 4)
"""

from datetime import date

import pandas as pd
import streamlit as st

import db


# ============================================================
# Setup geral
# ============================================================

st.set_page_config(
    page_title="Holerites NSA",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; padding-left: 1.5rem; padding-right: 1.5rem; max-width: 100%; }
    [data-testid="stSidebar"] {
        border-right: 1px solid #C7D0DB;
        min-width: 11rem !important;
        max-width: 11rem !important;
        width: 11rem !important;
    }
    [data-testid="stSidebar"] h3 { margin-top: 0; color: #1B3A5C; font-size: 1.05rem; }
    [data-testid="stSidebar"] label { font-size: 0.85rem; }
    h1, h2, h3 { color: #1B3A5C; font-weight: 600; }
    .block-container h3 { margin-top: 0.4rem !important; margin-bottom: 0.4rem !important; padding-top: 0 !important; padding-bottom: 0 !important; }
    div[data-testid="stDataFrame"], div[data-testid="stDataEditor"] {
        background-color: #FFFFFF; border-radius: 6px; padding: 4px;
        border: 1px solid #C7D0DB;
    }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF; padding: 12px 16px; border-radius: 6px;
        border: 1px solid #C7D0DB;
    }
    div[data-testid="stMetricValue"] { font-size: 1.4rem; color: #1B3A5C; font-weight: 600; }
    div[data-testid="stMetricLabel"] { font-size: 0.85rem; color: #6B7280; text-transform: uppercase; letter-spacing: 0.05em; }
    button[kind="primary"] { background-color: #1B3A5C; border-color: #1B3A5C; }
    button[kind="primary"]:hover { background-color: #15304B; border-color: #15304B; }
    div[data-testid="stExpander"] { background-color: #FFFFFF; border: 1px solid #C7D0DB; border-radius: 6px; }

    /* AgGrid: fonte e padding compactos pra caber valores grandes na tela */
    .ag-theme-streamlit, .ag-theme-streamlit-dark {
        --ag-font-size: 9px;
        --ag-row-height: 22px;
        --ag-header-height: 25px;
    }
    .ag-theme-streamlit .ag-cell,
    .ag-theme-streamlit .ag-header-cell {
        padding-left: 4px !important;
        padding-right: 4px !important;
        font-size: 9px !important;
    }
    .ag-theme-streamlit .ag-header-cell-label { justify-content: center; }
    .ag-theme-streamlit .ag-cell { line-height: 22px !important; }

    /* Colorir grupos de colunas na tabela editavel (tentativa) */
    /* Ordem das colunas: Nome(1) Banco(2) Comiss(3) Motivac(4) HE(5) Domingo(6) HE Total(7)
       Comissao(8) Salario(9) Vales(10) Uniod(11) Plano(12) Empr(13) VT(14) Tot Desc(15) Liquido(16) */
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(5),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(6),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(7),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(5),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(6),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(7) {
        background-color: #EAF1F8 !important;
    }
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(7) { font-weight: 700 !important; }

    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(8),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(9),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(8),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(9) {
        background-color: #F2EBE0 !important;
    }

    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(10),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(11),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(12),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(13),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(14),
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(15),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(10),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(11),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(12),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(13),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(14),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(15) {
        background-color: #F5E8E8 !important;
    }
    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(15) { font-weight: 700 !important; }

    div[data-testid="stDataEditor"] [role="gridcell"]:nth-child(16),
    div[data-testid="stDataEditor"] [role="columnheader"]:nth-child(16) {
        background-color: #E8F0E8 !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


import math


# Converte para float, tratando NaN/None/string-vazia como 0
def safe_float(v):
    try:
        f = float(v)
        if math.isnan(f) or math.isinf(f):
            return 0.0
        return f
    except (TypeError, ValueError):
        return 0.0


# Helper de formatacao brasileira: 1234.56 -> "R$ 1.234,56"
def fmt_real(v):
    try:
        v = float(v)
        if math.isnan(v) or math.isinf(v):
            return "R$ 0,00"
    except (TypeError, ValueError):
        return ""
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


# Helper: sigla do banco
_SIGLAS_BANCO = {
    "Caixa Econômica": "CEF",
    "Caixa Economica": "CEF",
    "Caixa": "CEF",
    "Dinheiro": "DIN",
    "Sicredi": "SICR",
    "Banco do Brasil": "BB",
    "Itaú": "ITAU",
    "Itau": "ITAU",
    "Bradesco": "BRAD",
    "Santander": "SANT",
    "Inter": "INT",
    "Nubank": "NU",
    "Banrisul": "BANRI",
}


def sigla_banco(nome):
    if not nome:
        return ""
    if nome in _SIGLAS_BANCO:
        return _SIGLAS_BANCO[nome]
    return nome[:4].upper().strip()


def card_total(label, valor, cor_fundo):
    """Card destacado com label em cima e valor formatado em R$."""
    st.markdown(
        f"""
        <div style="background-color: {cor_fundo}; padding: 14px 10px;
                    border-radius: 6px; border: 1px solid #C7D0DB; text-align: center;
                    min-height: 78px; display: flex; flex-direction: column;
                    justify-content: center;">
            <div style="font-size: 0.7rem; color: #6B7280;
                        text-transform: uppercase; letter-spacing: 0.05em;
                        margin-bottom: 4px; font-weight: 600;">{label}</div>
            <div style="font-size: 1.05rem; color: #1B3A5C; font-weight: 700;">{fmt_real(valor)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_cards_banco(df, cor_he, cor_cs, cor_de, cor_li):
    """6 cards destacados pra um banco: Motivac, HE Total, Comissao, Salario, Tot.Desc, Liquido."""
    items = [
        ("MOTIVACIONAL",    float(df["Motivac."].sum()),  "#F4F7FA"),
        ("HE TOTAL",        float(df["HE Total"].sum()),  cor_he),
        ("COMISSÃO",        float(df["Comissão"].sum()),  cor_cs),
        ("SALÁRIO",         float(df["Salário"].sum()),   cor_cs),
        ("TOTAL DESCONTOS", float(df["Tot. Desc."].sum()), cor_de),
        ("LÍQUIDO",         float(df["Líquido"].sum()),   cor_li),
    ]
    cols = st.columns(len(items))
    for col, (label, valor, cor) in zip(cols, items):
        with col:
            card_total(label, valor, cor)


# ============================================================
# Login
# ============================================================

def tela_login():
    col_a, col_b, col_c = st.columns([1, 2, 1])
    with col_b:
        st.markdown("### Holerites NSA")
        st.caption("Controle de pagamentos mensais — Arezzo / Schutz")
        st.write("")
        senha = st.text_input("Senha de acesso", type="password",
                              placeholder="Digite a senha")
        if st.button("Entrar", type="primary", use_container_width=True):
            if senha == st.secrets["app_password"]:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("Senha incorreta.")


def exige_login():
    if not st.session_state.get("autenticado"):
        tela_login()
        st.stop()


# ============================================================
# Sidebar
# ============================================================

def sidebar():
    with st.sidebar:
        st.markdown("### Holerites NSA")
        st.write("")

        lojas = db.listar_lojas()
        if not lojas:
            st.error("Nenhuma loja cadastrada.")
            st.stop()
        codigos = [l["codigo"] for l in lojas]
        nomes = {l["codigo"]: l["nome"] for l in lojas}

        if "loja_codigo" not in st.session_state:
            st.session_state["loja_codigo"] = codigos[0]

        escolha = st.selectbox(
            "Loja",
            codigos,
            index=codigos.index(st.session_state["loja_codigo"]),
            format_func=lambda c: nomes[c],
        )
        if escolha != st.session_state["loja_codigo"]:
            st.session_state["loja_codigo"] = escolha
            st.rerun()

        st.write("")
        st.divider()

        if st.button("Sair", use_container_width=True):
            st.session_state.clear()
            st.rerun()

    return next(l for l in lojas if l["codigo"] == st.session_state["loja_codigo"])


# ============================================================
# Tela: Configuracoes (bancos)
# ============================================================

def tela_configuracoes(loja):
    st.title("Configurações")
    st.caption(f"Loja: **{loja['nome']}**")
    st.write("")

    st.subheader("Formas de pagamento")
    st.caption("Cada banco vira uma seção no Excel exportado. Edite na tabela e clique em Salvar.")

    bancos = db.listar_bancos(loja["id"], ativos_apenas=False)

    if bancos:
        df = pd.DataFrame([
            {"id": b["id"], "Nome": b["nome"], "Ordem": int(b["ordem"]), "Ativo": b["ativo"]}
            for b in bancos
        ])

        edited = st.data_editor(
            df.drop(columns=["id"]),
            num_rows="fixed",
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nome":  st.column_config.TextColumn(width="large", required=True),
                "Ordem": st.column_config.NumberColumn(width="small", min_value=0, step=1),
                "Ativo": st.column_config.CheckboxColumn(width="small"),
            },
            key="editor_bancos",
        )

        col_a, _ = st.columns([1, 5])
        with col_a:
            if st.button("Salvar alterações", type="primary", key="salvar_bancos"):
                cli = db.get_client()
                for orig, novo in zip(df.to_dict("records"), edited.to_dict("records")):
                    if (orig["Nome"] != novo["Nome"] or
                        orig["Ordem"] != novo["Ordem"] or
                        orig["Ativo"] != novo["Ativo"]):
                        cli.table("bancos").update({
                            "nome": novo["Nome"],
                            "ordem": int(novo["Ordem"]),
                            "ativo": bool(novo["Ativo"]),
                        }).eq("id", orig["id"]).execute()
                st.success("Salvo.")
                st.rerun()
    else:
        st.info("Nenhum banco cadastrado ainda.")

    st.write("")
    with st.expander("Adicionar banco"):
        with st.form("form_novo_banco", clear_on_submit=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                novo_nome = st.text_input("Nome do banco", placeholder="ex: Itaú")
            with col2:
                nova_ordem = st.number_input(
                    "Ordem", min_value=0, step=1,
                    value=(max(b["ordem"] for b in bancos) + 1) if bancos else 1,
                )
            if st.form_submit_button("Adicionar", type="primary"):
                if novo_nome.strip():
                    db.upsert_banco(loja["id"], novo_nome.strip(), int(nova_ordem))
                    st.success(f"Banco '{novo_nome}' adicionado.")
                    st.rerun()
                else:
                    st.error("Informe o nome.")

    st.write("")
    st.divider()
    st.caption(
        "Para trocar a senha do app, edite o arquivo `.streamlit/secrets.toml` "
        "(local) ou as Secrets do Streamlit Cloud (quando publicado)."
    )


# ============================================================
# Tela: Funcionarias (tabela unica)
# ============================================================

def tela_funcionarias(loja):
    st.title("Funcionárias")
    st.caption(f"Loja: **{loja['nome']}**")
    st.write("")

    bancos = db.listar_bancos(loja["id"])
    bancos_por_id = {b["id"]: b["nome"] for b in bancos}
    nome_pra_id = {b["nome"]: b["id"] for b in bancos}
    opcoes_banco = list(bancos_por_id.values())

    funcs = db.listar_funcionarias(loja["id"], ativas_apenas=False)
    ativas = [f for f in funcs if f["ativa"]]
    inativas = [f for f in funcs if not f["ativa"]]

    col_m1, col_m2, col_m3 = st.columns(3)
    col_m1.metric("Ativas", len(ativas))
    col_m2.metric("Inativas", len(inativas))
    col_m3.metric("Total", len(funcs))

    st.write("")

    aba_ativas, aba_inativas = st.tabs([f"Ativas ({len(ativas)})",
                                          f"Inativas ({len(inativas)})"])

    with aba_ativas:
        if ativas:
            df = pd.DataFrame([
                {
                    "id": f["id"],
                    "Nome": f["nome"],
                    "Banco": bancos_por_id.get(f["banco_id"], ""),
                    "Comiss.": f["comissionada"],
                    "Inativar": False,
                }
                for f in ativas
            ])

            edited = st.data_editor(
                df.drop(columns=["id"]),
                num_rows="fixed",
                use_container_width=True,
                hide_index=True,
                height=min(700, 50 + 35 * len(ativas)),
                column_config={
                    "Nome": st.column_config.TextColumn(width="large", required=True),
                    "Banco": st.column_config.SelectboxColumn(
                        options=opcoes_banco, required=True, width="medium",
                    ),
                    "Comiss.": st.column_config.CheckboxColumn(
                        width="small", help="Recebe por comissão",
                    ),
                    "Inativar": st.column_config.CheckboxColumn(
                        width="small",
                        help="Marque pra inativar ao salvar",
                    ),
                },
                key="editor_funcs",
            )

            col_a, _ = st.columns([2, 5])
            with col_a:
                if st.button("Salvar alterações", type="primary",
                              use_container_width=True, key="salvar_funcs"):
                    cli = db.get_client()
                    n_alt = 0
                    n_inativadas = 0
                    for orig, novo in zip(df.to_dict("records"), edited.to_dict("records")):
                        novo_banco_id = nome_pra_id.get(novo["Banco"])
                        update = {}
                        if orig["Nome"] != novo["Nome"]:
                            update["nome"] = novo["Nome"]
                        if orig["Banco"] != novo["Banco"]:
                            update["banco_id"] = novo_banco_id
                        if orig["Comiss."] != novo["Comiss."]:
                            update["comissionada"] = bool(novo["Comiss."])
                        if novo["Inativar"]:
                            update["ativa"] = False
                            update["data_inativacao"] = date.today().isoformat()
                            n_inativadas += 1
                        if update:
                            cli.table("funcionarias").update(update).eq("id", orig["id"]).execute()
                            n_alt += 1
                    if n_alt:
                        msg = f"{n_alt} alteração(ões) salvas."
                        if n_inativadas:
                            msg += f" {n_inativadas} inativada(s)."
                        st.success(msg)
                        st.rerun()
                    else:
                        st.info("Nenhuma alteração detectada.")
        else:
            st.info("Nenhuma funcionária ativa.")

        st.write("")
        with st.expander("Cadastrar nova funcionária"):
            _form_nova_funcionaria(loja, nome_pra_id)

    with aba_inativas:
        if inativas:
            df_i = pd.DataFrame([
                {"id": f["id"], "Nome": f["nome"],
                 "Banco anterior": bancos_por_id.get(f["banco_id"], "—"),
                 "Inativada em": f.get("data_inativacao") or "—",
                 "Reativar": False}
                for f in inativas
            ])
            edited_i = st.data_editor(
                df_i.drop(columns=["id"]),
                num_rows="fixed",
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Nome":           st.column_config.TextColumn(width="large", disabled=True),
                    "Banco anterior": st.column_config.TextColumn(width="medium", disabled=True),
                    "Inativada em":   st.column_config.TextColumn(width="small", disabled=True),
                    "Reativar":       st.column_config.CheckboxColumn(width="small"),
                },
                key="editor_inativas",
            )
            if st.button("Reativar marcadas", key="reativar_btn", type="primary"):
                cli = db.get_client()
                n = 0
                for orig, novo in zip(df_i.to_dict("records"), edited_i.to_dict("records")):
                    if novo["Reativar"]:
                        cli.table("funcionarias").update({
                            "ativa": True, "data_inativacao": None,
                        }).eq("id", orig["id"]).execute()
                        n += 1
                if n:
                    st.success(f"{n} reativada(s).")
                    st.rerun()
                else:
                    st.info("Marque pelo menos uma pra reativar.")
        else:
            st.info("Nenhuma funcionária inativa.")


def _form_nova_funcionaria(loja, nome_pra_id):
    if not nome_pra_id:
        st.warning("Cadastre pelo menos um banco em Configurações.")
        return
    with st.form("form_nova_func", clear_on_submit=True):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            nome = st.text_input("Nome completo", placeholder="ex: Maria da Silva")
        with col2:
            banco_nome = st.selectbox("Forma de pagamento", list(nome_pra_id.keys()))
        with col3:
            comissionada = st.checkbox("Comissionada")
        if st.form_submit_button("Cadastrar", type="primary"):
            if nome.strip():
                db.upsert_funcionaria(
                    loja_id=loja["id"], nome=nome.strip(),
                    banco_id=nome_pra_id[banco_nome],
                    comissionada=comissionada,
                )
                st.success(f"'{nome}' cadastrada.")
                st.rerun()
            else:
                st.error("Informe o nome.")


# ============================================================
# Placeholders das proximas fases
# ============================================================

def tela_processar(loja):
    st.title("Processar holerite")
    st.caption(f"Loja: **{loja['nome']}**")
    st.write("")

    # Roteamento por etapa (sessao)
    etapa_key = f"proc_etapa_{loja['codigo']}"
    if etapa_key not in st.session_state:
        st.session_state[etapa_key] = "upload"

    if st.session_state[etapa_key] == "upload":
        _etapa_upload(loja, etapa_key)
    elif st.session_state[etapa_key] == "conferencia":
        _etapa_conferencia(loja, etapa_key)
    elif st.session_state[etapa_key] == "sucesso":
        _etapa_sucesso(loja, etapa_key)


def _etapa_upload(loja, etapa_key):
    from config import MES_NOME

    st.subheader("1. Carregar PDF do holerite")
    st.caption("Selecione o PDF e diga qual tipo de holerite é.")

    pdf = st.file_uploader("Arquivo PDF", type=["pdf"], label_visibility="collapsed")

    st.write("")

    # Tipo de holerite
    tipo_labels = {
        "regular": "Regular (mensal)",
        "13_1": "13º salário — 1ª parcela",
        "13_2": "13º salário — 2ª parcela",
    }
    tipo = st.radio(
        "Tipo de holerite",
        list(tipo_labels.keys()),
        format_func=lambda k: tipo_labels[k],
        horizontal=True,
    )

    st.write("")

    # Data de pagamento + competência
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        data_pag = st.date_input(
            "Data de pagamento",
            value=date.today(),
            format="DD/MM/YYYY",
        )

    if tipo == "regular":
        # Auto-sugere competência = mês de pagamento - 1
        mes_default = data_pag.month - 1 if data_pag.month > 1 else 12
        ano_default = data_pag.year if data_pag.month > 1 else data_pag.year - 1
        with col_b:
            competencia_mes = st.selectbox(
                "Mês de competência",
                options=list(range(1, 13)),
                index=mes_default - 1,
                format_func=lambda m: MES_NOME[m],
            )
        with col_c:
            competencia_ano = st.number_input(
                "Ano de competência",
                min_value=2020, max_value=2099, step=1,
                value=ano_default,
            )
    else:
        # 13º: só ano (mês não faz sentido)
        with col_b:
            competencia_mes = None
            competencia_ano = st.number_input(
                "Ano do 13º",
                min_value=2020, max_value=2099, step=1,
                value=data_pag.year,
            )

    # Identificação
    if tipo == "regular":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year}"
    elif tipo == "13_1":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (1ª)"
    else:
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (2ª)"
    st.markdown(f"**Identificação:** {aba}")

    st.write("")

    pode_processar = pdf is not None
    if st.button("Processar PDF", type="primary", disabled=not pode_processar):
        with st.spinner("Lendo o PDF…"):
            from parser import extrair_holerites
            dados_pdf = extrair_holerites(pdf.read())

        st.session_state[f"proc_dados_{loja['codigo']}"] = dados_pdf
        st.session_state[f"proc_data_{loja['codigo']}"] = data_pag.isoformat()
        st.session_state[f"proc_tipo_{loja['codigo']}"] = tipo
        st.session_state[f"proc_comp_mes_{loja['codigo']}"] = competencia_mes
        st.session_state[f"proc_comp_ano_{loja['codigo']}"] = int(competencia_ano)
        st.session_state[etapa_key] = "conferencia"
        st.rerun()


def _etapa_conferencia(loja, etapa_key):
    from config import MES_NOME

    dados_pdf = st.session_state.get(f"proc_dados_{loja['codigo']}", {})
    data_iso = st.session_state.get(f"proc_data_{loja['codigo']}")
    tipo = st.session_state.get(f"proc_tipo_{loja['codigo']}", "regular")
    comp_mes = st.session_state.get(f"proc_comp_mes_{loja['codigo']}")
    comp_ano = st.session_state.get(f"proc_comp_ano_{loja['codigo']}")
    if not dados_pdf or not data_iso:
        st.error("Dados perdidos. Volte e faça upload de novo.")
        if st.button("Voltar"):
            st.session_state[etapa_key] = "upload"
            st.rerun()
        return

    from datetime import datetime
    data_pag = datetime.fromisoformat(data_iso).date()
    if tipo == "regular":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year}"
    elif tipo == "13_1":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (1ª)"
    else:
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (2ª)"

    st.subheader(f"2. Conferência — {aba}")
    legenda = f"Data de pagamento: {data_pag.strftime('%d/%m/%Y')}"
    if tipo == "regular" and comp_mes:
        legenda += f"  •  Competência: {MES_NOME[comp_mes]} {comp_ano}"
    elif tipo != "regular":
        legenda += f"  •  Ano: {comp_ano}"
    st.caption(legenda)

    # ===== Match com cadastro =====
    funcs_banco = db.listar_funcionarias(loja["id"], ativas_apenas=True)
    bancos = db.listar_bancos(loja["id"])
    bancos_por_id = {b["id"]: b["nome"] for b in bancos}
    nome_pra_id = {b["nome"]: b["id"] for b in bancos}
    opcoes_banco = list(bancos_por_id.values())

    # Index funcionarias do banco por chave normalizada
    import unicodedata
    def chave(s):
        return "".join(c for c in unicodedata.normalize("NFKD", s)
                       if not unicodedata.combining(c)).lower().strip()

    func_por_chave = {chave(f["nome"]): f for f in funcs_banco}

    # Monta dataframe
    linhas = []
    for nome_pdf, d in dados_pdf.items():
        f_banco = func_por_chave.get(chave(nome_pdf))
        if f_banco:
            status = "Cadastrada"
            banco_nome = bancos_por_id.get(f_banco["banco_id"], "")
            comiss = f_banco["comissionada"]
            funcionaria_id = f_banco["id"]
        else:
            status = "Nova"
            banco_nome = opcoes_banco[0] if opcoes_banco else ""
            comiss = False
            funcionaria_id = None

        validou = not any("Validacao nao bateu" in a for a in d.get("avisos", []))
        linhas.append({
            "_id": funcionaria_id,
            "Status": status,
            "Nome": nome_pdf,
            "Banco": banco_nome,
            "Comiss.": comiss,
            "Motivac.": float(d.get("motivacional", 0)),
            "HE": float(d.get("he", 0)),
            "Domingo": float(d.get("domingo", 0)),
            "Vales": float(d.get("vales", 0)),
            "Uniod.": float(d.get("uniodonto", 0)),
            "Plano": float(d.get("plano_saude", 0)),
            "Empr.": float(d.get("emprestimo", 0)),
            "VT": float(d.get("vale_transporte", 0)),
            "Líquido": float(d.get("liquido", 0)),
            "OK": validou,
            "Ignorar": False,
        })

    # Funcionarias ausentes (cadastradas mas nao vieram no PDF)
    nomes_pdf_keys = {chave(n) for n in dados_pdf}
    ausentes = [f for f in funcs_banco if chave(f["nome"]) not in nomes_pdf_keys]

    # Resumo
    n_total = len(linhas)
    n_novas = sum(1 for l in linhas if l["Status"] == "Nova")
    n_ok = sum(1 for l in linhas if l["OK"])
    n_aviso = n_total - n_ok

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Detectadas", n_total)
    col2.metric("Novas", n_novas)
    col3.metric("Validadas", n_ok)
    col4.metric("Com aviso", n_aviso)
    col5.metric("Ausentes", len(ausentes))

    st.write("")

    if n_novas > 0:
        st.info(f"**{n_novas} funcionária(s) nova(s)** detectada(s) — vão ser cadastradas automaticamente ao salvar. Confira o banco e marque se é comissionada.")

    if ausentes:
        with st.expander(f"{len(ausentes)} funcionária(s) cadastrada(s) não veio(vieram) no PDF", expanded=False):
            for f in ausentes:
                st.markdown(f"- **{f['nome']}** — {bancos_por_id.get(f['banco_id'], '?')}")
            st.caption("Provavelmente férias, afastamento ou desligamento. Não serão lançadas neste mês.")

    st.write("")

    df = pd.DataFrame(linhas)
    df_exibir = df.drop(columns=["_id"])

    edited = st.data_editor(
        df_exibir,
        num_rows="fixed",
        use_container_width=True,
        hide_index=True,
        height=min(800, 60 + 35 * len(df)),
        column_config={
            "Status": st.column_config.TextColumn(width="small", disabled=True),
            "Nome": st.column_config.TextColumn(width="large", required=True),
            "Banco": st.column_config.SelectboxColumn(options=opcoes_banco, required=True, width="medium"),
            "Comiss.": st.column_config.CheckboxColumn(width="small", help="Recebe por comissão"),
            "Motivac.": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "HE": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Domingo": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Vales": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Uniod.": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Plano": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Empr.": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "VT": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "Líquido": st.column_config.NumberColumn(format="R$ %.2f", width="small"),
            "OK": st.column_config.CheckboxColumn(width="small", disabled=True, help="Validação cruzada do PDF"),
            "Ignorar": st.column_config.CheckboxColumn(width="small", help="Marque pra não lançar essa linha"),
        },
        key=f"editor_proc_{loja['codigo']}",
    )

    # Avisos detalhados
    avisos_visiveis = [(l["Nome"], dados_pdf[l["Nome"]].get("avisos", []))
                       for l in linhas if not l["OK"]]
    if avisos_visiveis:
        with st.expander(f"Avisos de {len(avisos_visiveis)} funcionária(s)", expanded=False):
            for nome, av in avisos_visiveis:
                st.markdown(f"**{nome}**")
                for a in av:
                    st.markdown(f"- {a}")

    st.write("")
    col_voltar, _, col_salvar = st.columns([1, 3, 1])
    with col_voltar:
        if st.button("← Voltar", use_container_width=True):
            st.session_state[etapa_key] = "upload"
            st.rerun()
    with col_salvar:
        if st.button("Salvar mês", type="primary", use_container_width=True):
            _salvar_mes(loja, etapa_key, data_pag, df, edited, nome_pra_id, bancos_por_id,
                        tipo=tipo, competencia_mes=comp_mes, competencia_ano=comp_ano)


def _salvar_mes(loja, etapa_key, data_pag, df_orig, df_edit, nome_pra_id, bancos_por_id,
                tipo="regular", competencia_mes=None, competencia_ano=None):
    cli = db.get_client()

    # 1) Cria/recupera o mes
    mes = db.upsert_mes(
        loja["id"], data_pag.year, data_pag.month, data_pag,
        tipo=tipo,
        competencia_mes=competencia_mes,
        competencia_ano=competencia_ano,
    )

    # 2) Cadastra novas funcionarias e ajusta nome_id
    registros = []
    n_novas = 0
    for orig, novo in zip(df_orig.to_dict("records"), df_edit.to_dict("records")):
        if novo["Ignorar"]:
            continue

        banco_id = nome_pra_id.get(novo["Banco"])
        if not banco_id:
            continue

        func_id = orig.get("_id")
        if not func_id:
            # Cadastra nova
            r = db.upsert_funcionaria(
                loja_id=loja["id"], nome=novo["Nome"],
                banco_id=banco_id, comissionada=bool(novo["Comiss."]),
            )
            func_id = r[0]["id"] if isinstance(r, list) else r["id"]
            n_novas += 1

        # Pra 13º, ignora comiss. e marca tudo como comissionada (assim o valor
        # vai todo pra coluna Comissão, sem distinção entre Comissão e Salário)
        comissionada_save = True if tipo != "regular" else bool(novo["Comiss."])

        registros.append({
            "funcionaria_id": func_id,
            "banco_id": banco_id,
            "comissionada": comissionada_save,
            "motivacional": safe_float(novo["Motivac."]),
            "he": safe_float(novo["HE"]),
            "domingo": safe_float(novo["Domingo"]),
            "vales": safe_float(novo["Vales"]),
            "uniodonto": safe_float(novo["Uniod."]),
            "plano_saude": safe_float(novo["Plano"]),
            "emprestimo": safe_float(novo["Empr."]),
            "vale_transporte": safe_float(novo["VT"]),
            "liquido": safe_float(novo["Líquido"]),
        })

    db.salvar_holerites_em_lote(mes["id"], registros)

    st.session_state[f"proc_resumo_{loja['codigo']}"] = {
        "mes_id": mes["id"],
        "n_lancadas": len(registros),
        "n_novas": n_novas,
        "data_pag": data_pag.isoformat(),
    }
    st.session_state[etapa_key] = "sucesso"
    st.rerun()


def _etapa_sucesso(loja, etapa_key):
    from config import MES_NOME

    resumo = st.session_state.get(f"proc_resumo_{loja['codigo']}", {})
    if not resumo:
        st.session_state[etapa_key] = "upload"
        st.rerun()
        return

    from datetime import datetime
    data_pag = datetime.fromisoformat(resumo["data_pag"]).date()
    tipo = st.session_state.get(f"proc_tipo_{loja['codigo']}", "regular")
    if tipo == "regular":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year}"
    elif tipo == "13_1":
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (1ª)"
    else:
        aba = f"{MES_NOME[data_pag.month]} {data_pag.year} — 13º (2ª)"

    st.success(f"**{aba}** salvo com sucesso.")
    st.write("")

    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Funcionárias lançadas", resumo["n_lancadas"])
    col_b.metric("Cadastros novos", resumo["n_novas"])
    col_c.metric("Data de pagamento", data_pag.strftime("%d/%m/%Y"))

    st.write("")
    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Processar outro mês", use_container_width=True):
            # limpa estado da tela
            for k in list(st.session_state.keys()):
                if k.startswith(f"proc_") and k.endswith(loja['codigo']):
                    del st.session_state[k]
            st.session_state[etapa_key] = "upload"
            st.rerun()
    with col_b:
        st.caption("A tela de Meses (em construção) vai listar todos os meses salvos.")


def tela_meses(loja):
    aberto_key = f"mes_aberto_{loja['codigo']}"
    if st.session_state.get(aberto_key):
        _meses_detalhe(loja, aberto_key)
    else:
        _meses_lista(loja, aberto_key)


def _meses_lista(loja, aberto_key):
    from config import MES_NOME

    st.title("Meses")
    st.caption(f"Loja: **{loja['nome']}**")
    st.write("")

    meses = db.listar_meses(loja["id"])
    if not meses:
        st.info("Nenhum mês processado ainda. Vá em **Processar holerite** pra começar.")
        return

    # Resumo de cada mes (precisa contar holerites e somar liquido)
    cli = db.get_client()
    linhas = []
    for m in meses:
        hols = cli.table("holerites").select("liquido,banco_id").eq("mes_id", m["id"]).execute().data
        total = sum(float(h["liquido"]) for h in hols)
        tipo_m = m.get("tipo", "regular")
        if tipo_m == "regular":
            label_mes = f"{MES_NOME[m['mes']]} {m['ano']}"
        elif tipo_m == "13_1":
            label_mes = f"{MES_NOME[m['mes']]} {m['ano']} — 13º (1ª)"
        else:
            label_mes = f"{MES_NOME[m['mes']]} {m['ano']} — 13º (2ª)"

        # Competência (só preenche pra regular)
        comp = ""
        if m.get("competencia_mes") and m.get("competencia_ano"):
            comp = f"Competência: {MES_NOME[m['competencia_mes']]} {m['competencia_ano']}"
        elif tipo_m != "regular" and m.get("competencia_ano"):
            comp = f"Ano do 13º: {m['competencia_ano']}"

        linhas.append({
            "id": m["id"],
            "Mês": label_mes,
            "Competência": comp,
            "Data pagamento": m["data_pagamento"],
            "Funcionárias": len(hols),
            "Total líquido (R$)": round(total, 2),
        })

    df = pd.DataFrame(linhas)

    # Mostra cada mes como linha clicavel
    for _, row in df.iterrows():
        with st.container(border=True):
            col_a, col_b, col_c, col_d, col_e = st.columns([3, 3, 2, 2, 1])
            with col_a:
                st.markdown(f"**{row['Mês']}**")
                if row["Competência"]:
                    st.caption(row["Competência"])
            with col_b:
                from datetime import datetime
                d = datetime.fromisoformat(row["Data pagamento"]).date()
                st.caption(f"Pagamento: {d.strftime('%d/%m/%Y')}")
            with col_c:
                st.caption(f"{row['Funcionárias']} funcionárias")
            with col_d:
                st.caption(f"Total: R$ {row['Total líquido (R$)']:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            with col_e:
                if st.button("Abrir", key=f"abrir_{row['id']}", use_container_width=True):
                    st.session_state[aberto_key] = row["id"]
                    st.rerun()


def _meses_detalhe(loja, aberto_key):
    from config import MES_NOME
    from datetime import datetime

    cli = db.get_client()
    mes_id = st.session_state[aberto_key]
    mes = cli.table("meses").select("*").eq("id", mes_id).limit(1).execute().data
    if not mes:
        st.error("Mês não encontrado.")
        del st.session_state[aberto_key]
        st.rerun()
        return
    mes = mes[0]

    data_pag = datetime.fromisoformat(mes["data_pagamento"]).date()
    tipo_m = mes.get("tipo", "regular")
    if tipo_m == "regular":
        aba = f"{MES_NOME[mes['mes']]} {mes['ano']}"
    elif tipo_m == "13_1":
        aba = f"{MES_NOME[mes['mes']]} {mes['ano']} — 13º (1ª parcela)"
    else:
        aba = f"{MES_NOME[mes['mes']]} {mes['ano']} — 13º (2ª parcela)"

    caption = f"Data de pagamento: {data_pag.strftime('%d/%m/%Y')}  •  Loja: {loja['nome']}"
    if mes.get("competencia_mes") and mes.get("competencia_ano"):
        caption += f"  •  Competência: {MES_NOME[mes['competencia_mes']]} {mes['competencia_ano']}"
    elif tipo_m != "regular" and mes.get("competencia_ano"):
        caption += f"  •  Ano do 13º: {mes['competencia_ano']}"

    col_a, col_b = st.columns([4, 1])
    with col_a:
        st.title(aba)
        st.caption(caption)
    with col_b:
        st.write("")
        if st.button("← Voltar", use_container_width=True):
            del st.session_state[aberto_key]
            st.rerun()

    st.write("")

    hols = db.holerites_do_mes(mes_id)
    bancos = db.listar_bancos(loja["id"], ativos_apenas=False)
    bancos_por_id = {b["id"]: b for b in bancos}
    nome_pra_id = {b["nome"]: b["id"] for b in bancos}
    opcoes_banco = [b["nome"] for b in bancos if b["ativo"]]

    if not hols:
        st.warning("Esse mês não tem holerites lançados.")
        return

    # Metricas por banco + total
    totais_por_banco = {}
    for h in hols:
        banco_nome = (h.get("banco") or {}).get("nome", "—")
        totais_por_banco[banco_nome] = totais_por_banco.get(banco_nome, 0) + float(h["liquido"])

    cols = st.columns(len(totais_por_banco) + 2)
    cols[0].metric("Funcionárias", len(hols))
    for i, (nome, total) in enumerate(sorted(totais_por_banco.items()), start=1):
        cols[i].metric(nome, f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    cols[-1].metric("Total geral", f"R$ {sum(totais_por_banco.values()):,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    st.write("")

    # === Totais globais por componente (Motivacional, HE Total, Comissao, Salario) ===
    cor_he = "#EAF1F8"
    cor_cs = "#F2EBE0"
    cor_de = "#F5E8E8"
    cor_li = "#E8F0E8"

    tot_motiv = 0.0
    tot_he_total = 0.0
    tot_comissao = 0.0
    tot_salario = 0.0
    tot_descontos = 0.0
    tot_liquido = 0.0
    for h in hols:
        motiv = float(h["motivacional"])
        he = float(h["he"])
        dom = float(h["domingo"])
        he_total = he + dom
        vales = float(h["vales"])
        uni = float(h["uniodonto"])
        plano = float(h["plano_saude"])
        emp = float(h["emprestimo"])
        vt = float(h["vale_transporte"])
        liq = float(h["liquido"])
        tot_desc_row = vales + uni + plano + emp + vt
        inv = liq - motiv - he_total + tot_desc_row
        tot_motiv += motiv
        tot_he_total += he_total
        tot_descontos += tot_desc_row
        tot_liquido += liq
        if h["comissionada"]:
            tot_comissao += inv
        else:
            tot_salario += inv

    items_globais = [
        ("MOTIVACIONAL",    tot_motiv,     "#FFFFFF"),
        ("HE TOTAL",        tot_he_total,  "#FFFFFF"),
        ("COMISSÃO",        tot_comissao,  "#FFFFFF"),
        ("SALÁRIO",         tot_salario,   "#FFFFFF"),
        ("TOTAL DESCONTOS", tot_descontos, "#FFFFFF"),
        ("LÍQUIDO",         tot_liquido,   "#FFFFFF"),
    ]
    cols_g = st.columns(len(items_globais))
    for col, (label, valor, cor) in zip(cols_g, items_globais):
        with col:
            card_total(label, valor, cor)

    # Espaco entre os totais gerais e o primeiro banco
    st.write("")
    st.write("")
    st.write("")

    # Agrupa por banco
    def banco_ordem(h):
        b = h.get("banco") or {}
        return (b.get("ordem", 99), b.get("nome", "—"))

    hols_ordenados = sorted(hols, key=lambda h: (banco_ordem(h), (h.get("funcionaria") or {}).get("nome", "")))
    grupos = {}
    for h in hols_ordenados:
        b = h.get("banco") or {}
        chave_b = (b.get("ordem", 99), b.get("nome", "—"))
        grupos.setdefault(chave_b, []).append(h)

    # Colunas editaveis (valores que vem do PDF)
    COL_INPUT = ["Motivac.", "HE", "Domingo", "Vales", "Uniod.",
                 "Plano", "Empr.", "VT", "Líquido"]
    # Colunas calculadas (read-only)
    COL_CALC = ["HE Total", "Comissão", "Salário", "Tot. Desc."]
    # Ordem de exibicao
    COLUNAS_NUM = ["Motivac.", "HE", "Domingo", "HE Total",
                   "Comissão", "Salário",
                   "Vales", "Uniod.", "Plano", "Empr.", "VT", "Tot. Desc.",
                   "Líquido"]
    COL_CONFIG = {
        "Nome": st.column_config.TextColumn(width=280, disabled=True),
        "Banco": st.column_config.SelectboxColumn(options=opcoes_banco, width=140),
        "Comiss.": st.column_config.CheckboxColumn(width="small"),
        **{c: st.column_config.NumberColumn(format="R$ %.2f", width="small") for c in COL_INPUT},
        **{c: st.column_config.NumberColumn(format="R$ %.2f", width="small", disabled=True) for c in COL_CALC},
    }

    from st_aggrid import AgGrid, GridOptionsBuilder, JsCode, DataReturnMode, GridUpdateMode
    import json as _json

    # Cores dos blocos
    COR_HE = "#EAF1F8"
    COR_CS = "#F2EBE0"
    COR_DE = "#F5E8E8"
    COR_LI = "#E8F0E8"

    # Formato brasileiro via JS
    js_fmt_real = JsCode("""
        function(params) {
            if (params.value == null || params.value === '') return '';
            const v = Number(params.value);
            if (isNaN(v)) return '';
            return 'R$ ' + v.toLocaleString('pt-BR',
                {minimumFractionDigits: 2, maximumFractionDigits: 2});
        }
    """)

    # Mapa nome do banco -> sigla, usado no display
    siglas_map = {b["nome"]: sigla_banco(b["nome"]) for b in bancos}
    siglas_js = _json.dumps(siglas_map, ensure_ascii=False)
    js_fmt_sigla = JsCode(f"""
        function(params) {{
            const m = {siglas_js};
            if (!params.value) return '';
            return m[params.value] || params.value.substring(0, 4).toUpperCase();
        }}
    """)

    # Renderiza cada grupo + acumula edits
    edits_por_grupo = []
    for (ordem, banco_nome), grupo_hols in grupos.items():
        # Visibilidade individual por banco (default: mostra a tabela)
        vis_key = f"vis_{mes_id}_{ordem}_{banco_nome}"
        if vis_key not in st.session_state:
            st.session_state[vis_key] = True

        # Cabecalho: nome do banco + setinha mostrar/ocultar
        h_col1, h_col2 = st.columns([20, 0.7])
        with h_col1:
            st.subheader(banco_nome)
        with h_col2:
            st.write("")
            label = "▼" if st.session_state[vis_key] else "▶"
            if st.button(label, key=f"btn_{vis_key}", use_container_width=True):
                st.session_state[vis_key] = not st.session_state[vis_key]
                st.rerun()

        mostrar_tabela = st.session_state[vis_key]
        # Placeholder pros cards (sera preenchido logo abaixo do nome)
        cards_placeholder = st.empty()

        linhas = []
        for h in grupo_hols:
            f = h.get("funcionaria") or {}
            b = h.get("banco") or {}
            motiv = float(h["motivacional"])
            he = float(h["he"])
            dom = float(h["domingo"])
            vales = float(h["vales"])
            uni = float(h["uniodonto"])
            plano = float(h["plano_saude"])
            emp = float(h["emprestimo"])
            vt = float(h["vale_transporte"])
            liq = float(h["liquido"])
            he_total = he + dom
            tot_desc = vales + uni + plano + emp + vt
            inv = liq - motiv - he_total + tot_desc
            linhas.append({
                "_id": h["id"],
                "Nome": f.get("nome", "?"),
                "Banco": b.get("nome", ""),
                "Comiss.": h["comissionada"],
                "Motivac.": motiv,
                "HE": he,
                "Domingo": dom,
                "HE Total": round(he_total, 2),
                "Comissão": round(inv, 2) if h["comissionada"] else 0.0,
                "Salário": round(inv, 2) if not h["comissionada"] else 0.0,
                "Vales": vales,
                "Uniod.": uni,
                "Plano": plano,
                "Empr.": emp,
                "VT": vt,
                "Tot. Desc.": round(tot_desc, 2),
                "Líquido": liq,
            })
        df_g = pd.DataFrame(linhas)
        # Banco e Comiss. vao no fim
        ordem_cols = ["Nome"] + COLUNAS_NUM + ["Banco", "Comiss."]
        df_exibir = df_g.drop(columns=["_id"])[ordem_cols]

        # ===== Configura AgGrid =====
        gb = GridOptionsBuilder.from_dataframe(df_exibir)
        gb.configure_default_column(resizable=True, sortable=False, editable=False)

        # Colunas de identificacao
        gb.configure_column("Nome", width=250, editable=False, pinned="left")
        gb.configure_column(
            "Banco", width=68, editable=True,
            cellEditor="agSelectCellEditor",
            cellEditorParams={"values": opcoes_banco},
            valueFormatter=js_fmt_sigla,
            headerName="Banco",
        )
        gb.configure_column(
            "Comiss.", width=42, editable=True,
            cellEditor="agCheckboxCellEditor",
            cellRenderer="agCheckboxCellRenderer",
        )

        # Liquido na linha TOTAL (pinned bottom) ocupa o espaco de Banco e Comiss
        js_colspan_liquido_total = JsCode("""
            function(params) {
                if (params.node && params.node.rowPinned === 'bottom') {
                    return 3;
                }
                return 1;
            }
        """)

        # Inputs editaveis
        for c in COL_INPUT:
            if c == "VT":
                w = 78
            elif c == "Líquido":
                w = 130
            else:
                w = 95
            kwargs = dict(
                width=w, editable=True, type=["numericColumn"],
                valueFormatter=js_fmt_real,
                cellEditor="agNumberCellEditor",
                cellEditorParams={"precision": 2},
            )
            if c == "Líquido":
                kwargs["colSpan"] = js_colspan_liquido_total
            gb.configure_column(c, **kwargs)

        # Calculadas (read-only)
        for c in COL_CALC:
            # Comissão/Salário podem chegar a 5 digitos
            if c in ("Comissão", "Salário"):
                w = 115
            elif c == "Tot. Desc.":
                w = 112
            else:
                w = 100
            gb.configure_column(
                c, width=w, editable=False, type=["numericColumn"],
                valueFormatter=js_fmt_real,
            )

        # Cores por grupo
        estilos = {
            "HE":          {"backgroundColor": COR_HE},
            "Domingo":     {"backgroundColor": COR_HE},
            "HE Total":    {"backgroundColor": COR_HE, "fontWeight": "700"},
            "Comissão":    {"backgroundColor": COR_CS},
            "Salário":     {"backgroundColor": COR_CS},
            "Vales":       {"backgroundColor": COR_DE},
            "Uniod.":      {"backgroundColor": COR_DE},
            "Plano":       {"backgroundColor": COR_DE},
            "Empr.":       {"backgroundColor": COR_DE},
            "VT":          {"backgroundColor": COR_DE},
            "Tot. Desc.":  {"backgroundColor": COR_DE, "fontWeight": "700"},
        }
        for col, est in estilos.items():
            gb.configure_column(col, cellStyle=est)

        # Liquido: estilo diferente pra linha TOTAL (pinned)
        js_liquido_style = JsCode(f"""
            function(params) {{
                const isTotal = params.node && params.node.rowPinned === 'bottom';
                return {{
                    backgroundColor: '{COR_LI}',
                    fontWeight: '700',
                    fontSize: isTotal ? '10px' : '9px'
                }};
            }}
        """)
        gb.configure_column("Líquido", cellStyle=js_liquido_style)

        # Linha TOTAL fixa no rodape (pinned)
        totais = {"Nome": "TOTAL", "Banco": "", "Comiss.": ""}
        for c in COLUNAS_NUM:
            totais[c] = float(df_exibir[c].sum())
        gb.configure_grid_options(pinnedBottomRowData=[totais])

        if mostrar_tabela:
            grid_resp = AgGrid(
                df_exibir,
                gridOptions=gb.build(),
                data_return_mode=DataReturnMode.AS_INPUT,
                update_mode=GridUpdateMode.VALUE_CHANGED,
                allow_unsafe_jscode=True,
                fit_columns_on_grid_load=False,
                height=min(700, 55 + 20 * (len(df_g) + 1)),
                theme="streamlit",
                custom_css={
                    ".ag-cell, .ag-cell-value": {
                        "font-size": "9px",
                        "line-height": "20px !important",
                        "padding-left": "4px !important",
                        "padding-right": "4px !important",
                    },
                    ".ag-header-cell, .ag-header-cell-text": {
                        "font-size": "9px !important",
                        "padding-left": "4px !important",
                        "padding-right": "4px !important",
                    },
                    ".ag-row": {
                        "height": "20px !important",
                    },
                    ".ag-header": {
                        "min-height": "23px !important",
                        "height": "23px !important",
                    },
                    ".ag-header-cell": {
                        "height": "23px !important",
                    },
                },
                key=f"aggrid_mes_{mes_id}_{ordem}_{banco_nome}",
            )

            edited_g = pd.DataFrame(grid_resp["data"])
            # Re-calcula colunas derivadas pra refletir edits sem salvar
            for c in COL_INPUT + ["Líquido"]:
                edited_g[c] = pd.to_numeric(edited_g[c], errors="coerce").fillna(0)
            edited_g["HE Total"] = (edited_g["HE"] + edited_g["Domingo"]).round(2)
            edited_g["Tot. Desc."] = (
                edited_g["Vales"] + edited_g["Uniod."] + edited_g["Plano"]
                + edited_g["Empr."] + edited_g["VT"]
            ).round(2)
            inv = (edited_g["Líquido"] - edited_g["Motivac."]
                   - edited_g["HE Total"] + edited_g["Tot. Desc."])
            edited_g["Comissão"] = (inv.where(edited_g["Comiss."].astype(bool), 0)).round(2)
            edited_g["Salário"] = (inv.where(~edited_g["Comiss."].astype(bool), 0)).round(2)
            edits_por_grupo.append((df_g, edited_g))
            df_cards = edited_g
        else:
            df_cards = df_g

        # Preenche o placeholder com os cards (aparecem logo abaixo do nome do banco)
        with cards_placeholder.container():
            render_cards_banco(df_cards, COR_HE, COR_CS, COR_DE, COR_LI)

    # Concatena pra usar no Salvar
    df = pd.concat([t[0] for t in edits_por_grupo], ignore_index=True) if edits_por_grupo else pd.DataFrame()
    edited = pd.concat([t[1] for t in edits_por_grupo], ignore_index=True) if edits_por_grupo else pd.DataFrame()

    # Se o usuario trocou o banco em qualquer linha, salva ja e re-renderiza
    # (move automaticamente pro bloco do novo banco)
    movidas = 0
    for orig, novo in zip(df.to_dict("records"), edited.to_dict("records")):
        if orig["Banco"] != novo["Banco"]:
            novo_banco_id = nome_pra_id.get(novo["Banco"])
            if novo_banco_id:
                update = {"banco_id": novo_banco_id}
                # Salva tambem outras edicoes pendentes nessa linha pra nao perder
                if orig["Comiss."] != novo["Comiss."]:
                    update["comissionada"] = bool(novo["Comiss."])
                for lbl, dbcol in [
                    ("Motivac.", "motivacional"), ("HE", "he"), ("Domingo", "domingo"),
                    ("Vales", "vales"), ("Uniod.", "uniodonto"), ("Plano", "plano_saude"),
                    ("Empr.", "emprestimo"), ("VT", "vale_transporte"), ("Líquido", "liquido"),
                ]:
                    o = safe_float(orig[lbl])
                    n_ = safe_float(novo[lbl])
                    if abs(o - n_) > 0.005:
                        update[dbcol] = n_
                db.atualizar_holerite(orig["_id"], update)
                movidas += 1
    if movidas:
        st.toast(f"{movidas} funcionária(s) movida(s) de banco.")
        st.rerun()

    st.write("")
    col_sal, col_xlsx, _, col_del = st.columns([2, 2, 3, 2])

    with col_sal:
        if st.button("Salvar alterações", type="primary", use_container_width=True):
            n = 0
            for orig, novo in zip(df.to_dict("records"), edited.to_dict("records")):
                update = {}
                if orig["Banco"] != novo["Banco"]:
                    update["banco_id"] = nome_pra_id.get(novo["Banco"])
                if orig["Comiss."] != novo["Comiss."]:
                    update["comissionada"] = bool(novo["Comiss."])
                for campo_lbl, campo_db in [
                    ("Motivac.", "motivacional"), ("HE", "he"), ("Domingo", "domingo"),
                    ("Vales", "vales"), ("Uniod.", "uniodonto"), ("Plano", "plano_saude"),
                    ("Empr.", "emprestimo"), ("VT", "vale_transporte"), ("Líquido", "liquido"),
                ]:
                    o = safe_float(orig[campo_lbl])
                    n_ = safe_float(novo[campo_lbl])
                    if abs(o - n_) > 0.005:
                        update[campo_db] = n_
                if update:
                    db.atualizar_holerite(orig["_id"], update)
                    n += 1
            if n:
                st.success(f"{n} linha(s) atualizada(s).")
                st.rerun()
            else:
                st.info("Nenhuma alteração detectada.")

    with col_xlsx:
        # Prepara dados pro Excel
        linhas_xlsx = []
        for h in hols:
            f = h.get("funcionaria") or {}
            b = h.get("banco") or {}
            linhas_xlsx.append({
                "nome": f.get("nome", "?"),
                "banco_nome": b.get("nome", "Outros"),
                "banco_ordem": b.get("ordem", 99),
                "comissionada": h["comissionada"],
                "motivacional": float(h["motivacional"]),
                "he": float(h["he"]),
                "domingo": float(h["domingo"]),
                "vales": float(h["vales"]),
                "uniodonto": float(h["uniodonto"]),
                "plano_saude": float(h["plano_saude"]),
                "emprestimo": float(h["emprestimo"]),
                "vale_transporte": float(h["vale_transporte"]),
                "liquido": float(h["liquido"]),
            })
        from excel_writer import gerar_xlsx_de_holerites
        # Texto de competencia que vai aparecer no header da secao no Excel
        if mes.get("competencia_mes") and mes.get("competencia_ano"):
            comp_label = f"Competência: {MES_NOME[mes['competencia_mes']]} {mes['competencia_ano']}"
        elif tipo_m == "13_1":
            comp_label = f"13º (1ª parcela) — Ano {mes.get('competencia_ano') or mes['ano']}"
        elif tipo_m == "13_2":
            comp_label = f"13º (2ª parcela) — Ano {mes.get('competencia_ano') or mes['ano']}"
        else:
            comp_label = None
        xlsx_bytes = gerar_xlsx_de_holerites(
            linhas_xlsx, data_pag,
            tipo=tipo_m, competencia_label=comp_label,
        )
        nome_arquivo = f"Holerites_{loja['codigo']}_{mes['ano']}-{mes['mes']:02d}"
        if tipo_m == "13_1":
            nome_arquivo += "_13o-1a"
        elif tipo_m == "13_2":
            nome_arquivo += "_13o-2a"
        nome_arquivo += ".xlsx"
        st.download_button(
            "Baixar Excel",
            data=xlsx_bytes,
            file_name=nome_arquivo,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with col_del:
        if st.button("Excluir mês", use_container_width=True):
            st.session_state[f"confirmar_excluir_{mes_id}"] = True
            st.rerun()

    if st.session_state.get(f"confirmar_excluir_{mes_id}"):
        st.warning(f"Tem certeza que quer excluir **{aba}**? Todos os holerites desse mês serão apagados. Esta ação **não pode ser desfeita**.")
        col_n, col_s = st.columns(2)
        with col_n:
            if st.button("Não, cancelar", use_container_width=True):
                del st.session_state[f"confirmar_excluir_{mes_id}"]
                st.rerun()
        with col_s:
            if st.button("Sim, excluir", type="primary", use_container_width=True):
                db.excluir_mes(mes_id)
                del st.session_state[f"confirmar_excluir_{mes_id}"]
                del st.session_state[aberto_key]
                st.toast(f"{aba} excluído.")
                st.rerun()


# ============================================================
# Roteamento
# ============================================================

def main():
    exige_login()

    loja = sidebar()

    paginas = {
        "Meses":               lambda: tela_meses(loja),
        "Processar holerite":  lambda: tela_processar(loja),
        "Funcionárias":        lambda: tela_funcionarias(loja),
        "Configurações":       lambda: tela_configuracoes(loja),
    }

    with st.sidebar:
        escolha = st.radio("Menu", list(paginas.keys()), label_visibility="collapsed")

    paginas[escolha]()


if __name__ == "__main__":
    main()

"""
parser.py — Extrai dados de holerites mensais da Arezzo (PDF).

Estrategia: agrupa palavras do PDF por POSICAO (x0, top). Cada codigo
da folha vira uma linha; o valor de vencimento e o de desconto sao
identificados pela faixa de x0 onde caem. Assim, codigos como 9199
(garantia minima) que confundem extracoes lineares nao contaminam
os codigos de hora extra vizinhos.
"""

import re
import unicodedata
from io import BytesIO

import pdfplumber

from config import (
    CODIGOS_MOTIVACIONAL, CODIGOS_HE, CODIGOS_DOMINGO,
    CODIGOS_VALES, CODIGOS_UNIODONTO, CODIGOS_PLANO_SAUDE,
    CODIGOS_EMPRESTIMO, CODIGOS_GARANTIA_MINIMA,
    CODIGOS_EMP_IGNORAR, CODIGOS_DESCONTOS_NAO_CAPTURADOS,
    EXCLUIR_SEMPRE, INCLUIR_CEF, CEF, CAIXA_LOJA,
)


# Universo de nomes canonicos conhecidos (do config) para corrigir nomes
# que sairam com caracteres quebrados do PDF.
_NOMES_CANONICOS = list(CEF) + list(CAIXA_LOJA) + list(EXCLUIR_SEMPRE) + list(INCLUIR_CEF)


def _strip_acentos(s):
    return "".join(
        c for c in unicodedata.normalize("NFKD", s)
        if not unicodedata.combining(c)
    )


def _chave_nome(s):
    """Chave canonica para comparar nomes ignorando acentos, caracteres
    quebrados e capitalizacao."""
    s = _strip_acentos(s).lower()
    # troca tudo que nao seja letra/espaco por '?' e depois remove '?'
    s = re.sub(r"[^a-z\s]", "?", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _resolver_nome_canonico(nome_cru):
    """Se o nome cru bate com um da lista de config (ignorando acentos
    e chars quebrados), retorna o nome canonico do config. Senao,
    retorna o nome capitalizado normalmente."""
    if not nome_cru:
        return nome_cru
    alvo = _chave_nome(nome_cru)
    # Match exato ignorando acentos
    for canonico in _NOMES_CANONICOS:
        if _chave_nome(canonico) == alvo:
            return canonico
    # Match tolerando ate 1 caractere '?' (PDF quebrou letra acentuada)
    alvo_pattern = re.compile("^" + re.escape(alvo).replace(r"\?", ".") + "$")
    for canonico in _NOMES_CANONICOS:
        if alvo_pattern.match(_chave_nome(canonico)):
            return canonico
    return _capitalizar(nome_cru)

# Vale transporte (codigo 48) entra na coluna L
CODIGO_VALE_TRANSPORTE = 48

# Faixas horizontais (em pontos do PDF) onde cada valor aparece
X_CODIGO_MAX  = 35       # codigos ficam em x0 entre 5 e 20
X_VENC_MIN    = 370      # valores de vencimento ~ x0 399-404
X_VENC_MAX    = 440
X_DESC_MIN    = 455      # valores de desconto ~ x0 480-486
X_DESC_MAX    = 510

# Acima desse "top", comeca a copia espelho de assinatura
TOP_LIMITE_COPIA_ESPELHO = 270

RE_VALOR = re.compile(r"^\d{1,3}(?:\.\d{3})*,\d{2}$")


def _eh_valor(texto):
    return bool(RE_VALOR.match(texto))


def _para_float(texto):
    return float(texto.replace(".", "").replace(",", "."))


def _agrupar_por_linha(words, tolerancia=3):
    if not words:
        return []
    words = sorted(words, key=lambda w: w["top"])
    linhas = []
    linha_atual = [words[0]]
    for w in words[1:]:
        if abs(w["top"] - linha_atual[0]["top"]) <= tolerancia:
            linha_atual.append(w)
        else:
            linhas.append(sorted(linha_atual, key=lambda x: x["x0"]))
            linha_atual = [w]
    linhas.append(sorted(linha_atual, key=lambda x: x["x0"]))
    return linhas


def _capitalizar(nome):
    """'TALITA KELEN SILVA LIBORIO' -> 'Talita Kelen Silva Liborio'."""
    miudas = {"de", "da", "do", "das", "dos", "e"}
    palavras = nome.split()
    out = []
    for i, p in enumerate(palavras):
        pl = p.lower()
        if i > 0 and pl in miudas:
            out.append(pl)
        else:
            out.append(pl.capitalize())
    return " ".join(out)


def _extrair_nome(words):
    """
    Acha a linha 'Codigo Nome do Funcionario CBO Departamento Filial'
    e captura a linha de baixo: <id> NOME EM MAIUSCULAS <CBO 6 digitos> ...
    """
    linhas = _agrupar_por_linha(words)
    for linha in linhas:
        textos = [w["text"] for w in linha]
        if len(textos) < 3:
            continue
        # Primeiro item deve ser id curto numerico
        if not textos[0].isdigit() or len(textos[0]) > 4:
            continue
        # Encontra CBO de 6 digitos
        for i, t in enumerate(textos[1:], 1):
            if t.isdigit() and len(t) == 6:
                nome_parts = textos[1:i]
                nome = " ".join(nome_parts).strip()
                if len(nome) < 5:
                    continue
                # Conserta caracteres mal decodificados (ex. "LU�ZA" -> "LUIZA")
                # Heuristica: nome tem que ter so letras/espacos/acentos
                # Se contem ?, trocamos por melhor palpite caso a caso (manual)
                # O nome cru pode ter acentos (Í, ã, é). _chave_nome
                # ja faz strip de acentos, entao passamos direto.
                return _resolver_nome_canonico(nome)
    return None


def _extrair_linhas_codigo(words):
    """[(codigo, valor_venc, valor_desc), ...] na metade superior."""
    linhas = _agrupar_por_linha(words)
    resultado = []
    for linha in linhas:
        if not linha:
            continue
        if linha[0]["top"] >= TOP_LIMITE_COPIA_ESPELHO:
            continue
        first = linha[0]
        if first["x0"] > X_CODIGO_MAX:
            continue
        if not first["text"].isdigit():
            continue
        codigo = int(first["text"])
        venc = 0.0
        desc = 0.0
        for w in linha[1:]:
            if not _eh_valor(w["text"]):
                continue
            if X_VENC_MIN <= w["x0"] <= X_VENC_MAX:
                venc = _para_float(w["text"])
            elif X_DESC_MIN <= w["x0"] <= X_DESC_MAX:
                desc = _para_float(w["text"])
        resultado.append((codigo, venc, desc))
    return resultado


def _extrair_liquido_e_totais(words):
    """
    Devolve (liquido, total_vencimentos, total_descontos).

    No PDF Arezzo, a linha de totais fica em top ~290-300 com:
      Total Vencimentos ~ x0 387
      Total Descontos    ~ x0 469
    E "Valor Liquido" tem o valor em x0 ~469 em top ~315-320.
    """
    liquido = None
    total_venc = None
    total_desc = None
    for w in words:
        if not _eh_valor(w["text"]):
            continue
        v = _para_float(w["text"])
        # Total descontos (coluna direita, top ~296)
        if 455 <= w["x0"] <= 510 and 285 <= w["top"] <= 305:
            total_desc = v
        # Total vencimentos (coluna central, top ~296)
        elif 380 <= w["x0"] <= 425 and 285 <= w["top"] <= 305:
            total_venc = v
        # Liquido (coluna direita, top ~318)
        elif 455 <= w["x0"] <= 510 and 310 <= w["top"] <= 335:
            liquido = v
    return liquido, total_venc, total_desc


def _parsear_pagina(page):
    words = page.extract_words()
    nome = _extrair_nome(words)
    if not nome:
        return None
    linhas = _extrair_linhas_codigo(words)
    liquido, _tot_venc, total_desc_pdf = _extrair_liquido_e_totais(words)
    texto = (page.extract_text() or "").upper()
    eh_transportar = "A TRANSPORTAR" in texto and liquido is None

    motivacional = sum(v for c, v, _ in linhas if c in CODIGOS_MOTIVACIONAL)
    he = sum(v for c, v, _ in linhas if c in CODIGOS_HE)
    domingo = sum(v for c, v, _ in linhas if c in CODIGOS_DOMINGO)
    vales = sum(d for c, _, d in linhas if c in CODIGOS_VALES)
    uniodonto = sum(d for c, _, d in linhas if c in CODIGOS_UNIODONTO)
    plano_saude = sum(d for c, _, d in linhas if c in CODIGOS_PLANO_SAUDE)
    emprestimo = sum(
        d for c, _, d in linhas
        if c in CODIGOS_EMPRESTIMO and c not in CODIGOS_EMP_IGNORAR
    )
    vale_transp = sum(d for c, _, d in linhas if c == CODIGO_VALE_TRANSPORTE)
    nao_capt = sum(
        d for c, _, d in linhas if c in CODIGOS_DESCONTOS_NAO_CAPTURADOS
    )
    soma_capt = vales + uniodonto + plano_saude + emprestimo + vale_transp

    avisos = []
    cods_garantia = [c for c, v, _ in linhas if c in CODIGOS_GARANTIA_MINIMA]
    if cods_garantia:
        avisos.append(
            f"Codigo de garantia minima detectado ({cods_garantia[0]}) - valor descartado."
        )

    return {
        "nome": nome,
        "motivacional": round(motivacional, 2),
        "he": round(he, 2),
        "domingo": round(domingo, 2),
        "vales": round(vales, 2),
        "uniodonto": round(uniodonto, 2),
        "plano_saude": round(plano_saude, 2),
        "emprestimo": round(emprestimo, 2),
        "vale_transporte": round(vale_transp, 2),
        "liquido": round(liquido or 0, 2),
        "total_descontos_pdf": round(total_desc_pdf or 0, 2),
        "_soma_capturados": round(soma_capt, 2),
        "_nao_capturados": round(nao_capt, 2),
        "a_transportar": eh_transportar,
        "avisos": avisos,
    }


def _mesclar_paginas_transportar(dados_paginas):
    if not dados_paginas:
        return []
    out = [dados_paginas[0]]
    for p in dados_paginas[1:]:
        ultima = out[-1]
        if ultima["a_transportar"] and ultima["nome"] == p["nome"]:
            for k in [
                "motivacional", "he", "domingo", "vales", "uniodonto",
                "plano_saude", "emprestimo", "vale_transporte",
                "_soma_capturados", "_nao_capturados",
            ]:
                ultima[k] = round(ultima[k] + p[k], 2)
            ultima["liquido"] = p["liquido"]
            ultima["total_descontos_pdf"] = p["total_descontos_pdf"]
            ultima["a_transportar"] = False
            ultima["avisos"].append("Holerite multi-pagina (A TRANSPORTAR) mesclado.")
        else:
            out.append(p)
    return out


def extrair_holerites(pdf_bytes):
    """
    Entrada: bytes do PDF.
    Saida: dict { nome -> dict com colunas e validacao }.
    Aplica exclusoes da config.EXCLUIR_SEMPRE.
    """
    paginas = []
    with pdfplumber.open(BytesIO(pdf_bytes)) as pdf:
        for page in pdf.pages:
            dados = _parsear_pagina(page)
            if dados:
                paginas.append(dados)

    paginas = _mesclar_paginas_transportar(paginas)

    resultado = {}
    for p in paginas:
        nome = p["nome"]
        if nome in EXCLUIR_SEMPRE:
            continue
        soma_total = round(p["_soma_capturados"] + p["_nao_capturados"], 2)
        diff = round(soma_total - p["total_descontos_pdf"], 2)
        if abs(diff) > 0.005:
            p["avisos"].append(
                f"Validacao nao bateu: capturado+nao-capt={soma_total:.2f} "
                f"vs Total Descontos PDF={p['total_descontos_pdf']:.2f} "
                f"(diferenca R$ {diff:+.2f})"
            )
        resultado[nome] = p
    return resultado

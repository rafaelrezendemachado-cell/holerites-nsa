"""
config.py — Configurações do app de holerites Arezzo.

Tudo que pode mudar de mês pra mês (listas de funcionárias, códigos da
folha, cores da planilha) fica concentrado aqui. Nenhuma lógica de
parsing/Excel mora neste arquivo — só dados.
"""

# ============================================================
# LISTAS DE FUNCIONÁRIAS (válidas a partir de Junho/2026)
# ============================================================

# Grupo CAIXA ECONÔMICA — pagamento via banco
CEF = [
    "Amanda Caroline do Nascimento Queiroz",
    "Amanda Gabryela Duarte Pedroso",
    "Crislaine Amaral Gomes",
    "Eliane de Oliveira Alves",
    "Francieli de Souza Cunha de Morais",
    "Glauce Coutinho Arsamendia",
    "Izabeli dos Santos Ribeiro",
    "Jamila Russo Tarouco",
    "Josieli Ortiz Silva",
    "Juliana Teixeira Baldez",
    "Karine Cansian",
    "Katia Franciele dos Santos",
    "Larissa dos Santos Ferreira",
    "Maria Luíza Gallindo de Carvalho",
    "Sineia de Brito Pimenta",
    "Talita Kelen Silva Liborio",
    "Tatiane Aparecida Lacerda Gamarra",
    "Vania Verao de Oliveira",
]

# Grupo CAIXA DA LOJA — pagamento em dinheiro
CAIXA_LOJA = [
    "Amanda da Silva Santos",
    "Ana Gabriely Matos de Paula",
    "Geisiane Guilherme Vilhalva",
    "Gislaine Marconsini da Silva",
    "Krishma Evelyn Freitas Goncalves",
    "Luzia Tais Pereira da Silva",
    "Mariete Souza Cavalcante",
    "Thielly Portilho da Mata",
    "Yasmim Alves Tenorio Bitsch",
]

# Recebem por comissão (fórmula inversa vai na coluna F).
# As demais recebem salário fixo (fórmula vai na coluna G).
COMISSIONADAS = {
    "Amanda Caroline do Nascimento Queiroz",
    "Crislaine Amaral Gomes",
    "Jamila Russo Tarouco",
    "Josieli Ortiz Silva",
    "Karine Cansian",
    "Katia Franciele dos Santos",
    "Krishma Evelyn Freitas Goncalves",
    "Sineia de Brito Pimenta",
    "Talita Kelen Silva Liborio",
    "Tatiane Aparecida Lacerda Gamarra",
    "Gislaine Marconsini da Silva",
    "Mariete Souza Cavalcante",
    "Geisiane Guilherme Vilhalva",
    # "Drielly ..."  ← preencher nome completo quando confirmar
}

# Sempre descartar do PDF, mesmo se aparecerem
EXCLUIR_SEMPRE = {
    "Raquel Aparecida Rezende Machado",
    "Renan Rezende Machado",
    "Gabrielly Fernanda Nunes Ortiz",
}

# Forçar na CEF (caso a regra padrão tentasse jogar em outro lugar)
INCLUIR_CEF = {
    "Rafael Rezende Machado",
}


# ============================================================
# CÓDIGOS DA FOLHA DE PAGAMENTO
# ============================================================
# Cada conjunto abaixo lista os "cods" da folha que somam numa
# coluna específica da planilha. Códigos novos: adicionar aqui.

CODIGOS_MOTIVACIONAL  = {205}                                  # coluna B
CODIGOS_HE            = {202, 214, 221, 248, 250}              # coluna C
CODIGOS_DOMINGO       = {240}                                  # coluna D (raro)
CODIGOS_VALES         = {207}                                  # coluna H
CODIGOS_UNIODONTO     = {239}                                  # coluna I
CODIGOS_PLANO_SAUDE   = {8111}                                 # coluna J
CODIGOS_EMPRESTIMO    = {                                      # coluna K
    9750, 9751,
    258, 259, 260, 261, 262, 263, 264, 265,
    266, 267, 268, 269, 271,
}

# ⚠️ ARMADILHA: garantia mínima desalinha o parser e contamina HE.
# Detectar e descartar ANTES de mapear códigos de hora extra.
CODIGOS_GARANTIA_MINIMA = {9199, 8702}

# Empréstimo que NÃO entra em K (provisão e estouro)
CODIGOS_EMP_IGNORAR = {9752, 991}

# Descontos que não vão pra nenhuma coluna específica, mas compõem
# o total de descontos do PDF (e são "embutidos" via fórmula inversa)
CODIGOS_DESCONTOS_NAO_CAPTURADOS = {
    998,  # I.N.S.S.
    999,  # Imposto de Renda
    226, 227, 40, 42,  # Horas faltas e variantes
    812, 821,           # INSS férias / diferença
    937,                # Adiantamento de férias
    991,                # Estouro mês anterior
    9752,               # Provisão desc emp férias (cancela com 9754 no venc)
}


# ============================================================
# MÊS DE PAGAMENTO → NOME DA ABA
# ============================================================

MES_NOME = {
    1: "Janeiro",  2: "Fevereiro", 3: "Março",     4: "Abril",
    5: "Maio",     6: "Junho",     7: "Julho",     8: "Agosto",
    9: "Setembro", 10: "Outubro",  11: "Novembro", 12: "Dezembro",
}


def nome_aba_por_data(data_pagamento):
    """Ex: 05/06/2026 → 'Junho 2026'."""
    return f"{MES_NOME[data_pagamento.month]} {data_pagamento.year}"


# ============================================================
# FORMATAÇÃO DA PLANILHA
# ============================================================

# Cores no padrão ARGB do openpyxl ("FF" + RRGGBB)
COR_AZUL_INPUT     = "FF000040"  # valores que vieram do PDF
COR_PRETO_FORMULA  = "FF000000"  # células com fórmula (E, M, F/G, N)
COR_VERDE_LIQUIDO  = "FFEBF1DE"  # fundo da coluna N (Líquido)
COR_CINZA_OCULTA   = "FFF2F2F2"  # fundo da coluna O (oculta)
COR_AMARELO_HEADER = "FFFFFF00"  # cabeçalho de seção e linha TOTAL
COR_CINZA_ESCURO   = "FF595959"  # fundo dos cabeçalhos de coluna
COR_BRANCO         = "FFFFFFFF"  # texto dos cabeçalhos de coluna

# Larguras de coluna (em "caracteres" do Excel)
LARGURAS = {
    "A": 34, "B": 13, "C": 12, "D": 11, "E": 15, "F": 13,
    "G": 13, "H": 11, "I": 12, "J": 14, "K": 13, "L": 15,
    "M": 17, "N": 13, "O": 14,
}

# Alturas (em pontos do Excel)
ALTURA_DADOS         = 15.0
ALTURA_TOTAL         = 15.75
ALTURA_HEADER_SECAO  = 18.0
ALTURA_HEADER_COLS   = 30.0

# Formato dos valores em R$
FORMATO_REAL = '"R$ "#,##0.00'

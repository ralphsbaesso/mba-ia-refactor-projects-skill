"""Constantes de domínio, num único lugar (evita magic strings/numbers espalhados)."""

CATEGORIAS_VALIDAS = [
    "informatica",
    "moveis",
    "vestuario",
    "geral",
    "eletronicos",
    "livros",
]

STATUS_PEDIDO_VALIDOS = [
    "pendente",
    "aprovado",
    "enviado",
    "entregue",
    "cancelado",
]

NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200

# (limiar de faturamento, taxa de desconto) — avaliados do maior para o menor.
DISCOUNT_TIERS = [
    (10_000, 0.10),
    (5_000, 0.05),
    (1_000, 0.02),
]

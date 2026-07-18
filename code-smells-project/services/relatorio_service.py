"""Regra de negócio do relatório de vendas (faixas de desconto)."""

from models import pedido as pedido_model
from utils.constants import DISCOUNT_TIERS


def desconto_para(faturamento):
    for limiar, taxa in DISCOUNT_TIERS:
        if faturamento > limiar:
            return faturamento * taxa
    return 0


def gerar_relatorio(db):
    agg = pedido_model.aggregates(db)
    faturamento = agg["faturamento"]
    total_pedidos = agg["total_pedidos"]
    desconto = desconto_para(faturamento)

    return {
        "total_pedidos": total_pedidos,
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": agg["pendentes"],
        "pedidos_aprovados": agg["aprovados"],
        "pedidos_cancelados": agg["cancelados"],
        "ticket_medio": round(faturamento / total_pedidos, 2) if total_pedidos > 0 else 0,
    }

"""Model de Pedido: acesso a dados parametrizado + leitura com JOIN (sem N+1)."""


def insert_pedido(db, usuario_id, total, status="pendente"):
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, status, total),
    )
    return cursor.lastrowid


def insert_item(db, pedido_id, produto_id, quantidade, preco_unitario):
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) "
        "VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def update_status(db, pedido_id, status):
    db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))
    db.commit()


def count(db):
    return db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def _fetch(db, where="", params=()):
    """Uma única query com JOIN (elimina o N+1) e agrupamento em memória."""
    query = (
        "SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em, "
        "       i.produto_id, i.quantidade, i.preco_unitario, pr.nome AS produto_nome "
        "FROM pedidos p "
        "LEFT JOIN itens_pedido i ON i.pedido_id = p.id "
        "LEFT JOIN produtos pr ON pr.id = i.produto_id "
        + where
        + " ORDER BY p.id"
    )
    rows = db.execute(query, params).fetchall()

    pedidos = {}
    ordem = []
    for row in rows:
        pid = row["id"]
        if pid not in pedidos:
            pedidos[pid] = {
                "id": pid,
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            ordem.append(pid)
        if row["produto_id"] is not None:
            pedidos[pid]["itens"].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or "Desconhecido",
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
    return [pedidos[pid] for pid in ordem]


def get_all(db):
    return _fetch(db)


def get_by_usuario(db, usuario_id):
    return _fetch(db, "WHERE p.usuario_id = ?", (usuario_id,))


def aggregates(db):
    """Métricas de vendas numa só query agregada (sem loop de COUNTs)."""
    row = db.execute(
        "SELECT COUNT(*) AS total_pedidos, "
        "COALESCE(SUM(total), 0) AS faturamento, "
        "SUM(CASE WHEN status = 'pendente' THEN 1 ELSE 0 END) AS pendentes, "
        "SUM(CASE WHEN status = 'aprovado' THEN 1 ELSE 0 END) AS aprovados, "
        "SUM(CASE WHEN status = 'cancelado' THEN 1 ELSE 0 END) AS cancelados "
        "FROM pedidos"
    ).fetchone()
    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento": row["faturamento"] or 0,
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }

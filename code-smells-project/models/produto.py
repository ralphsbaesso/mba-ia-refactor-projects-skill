"""Model de Produto: acesso a dados com queries parametrizadas. Sem HTTP."""

_COLUNAS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")


def _to_dict(row):
    return {coluna: row[coluna] for coluna in _COLUNAS}


def get_all(db):
    rows = db.execute("SELECT * FROM produtos").fetchall()
    return [_to_dict(row) for row in rows]


def get_by_id(db, produto_id):
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return _to_dict(row) if row else None


def create(db, nome, descricao, preco, estoque, categoria):
    cursor = db.execute(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) "
        "VALUES (?, ?, ?, ?, ?)",
        (nome, descricao, preco, estoque, categoria),
    )
    db.commit()
    return cursor.lastrowid


def update(db, produto_id, nome, descricao, preco, estoque, categoria):
    db.execute(
        "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, "
        "categoria = ? WHERE id = ?",
        (nome, descricao, preco, estoque, categoria, produto_id),
    )
    db.commit()


def delete(db, produto_id):
    db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
    db.commit()


def decrement_estoque(db, produto_id, quantidade):
    db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ?",
        (quantidade, produto_id),
    )


def count(db):
    return db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]


def search(db, termo=None, categoria=None, preco_min=None, preco_max=None):
    clausulas = ["1=1"]
    params = []
    if termo:
        clausulas.append("(nome LIKE ? OR descricao LIKE ?)")
        curinga = f"%{termo}%"
        params.extend([curinga, curinga])
    if categoria:
        clausulas.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        clausulas.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        clausulas.append("preco <= ?")
        params.append(preco_max)

    query = "SELECT * FROM produtos WHERE " + " AND ".join(clausulas)
    rows = db.execute(query, params).fetchall()
    return [_to_dict(row) for row in rows]

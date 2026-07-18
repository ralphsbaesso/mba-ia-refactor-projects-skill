"""Model de Usuário: acesso a dados parametrizado. A senha (hash) nunca é serializada."""

_COLUNAS_PUBLICAS = ("id", "nome", "email", "tipo", "criado_em")


def to_public_dict(row):
    """Serialização segura: expõe apenas campos públicos, jamais a senha."""
    return {coluna: row[coluna] for coluna in _COLUNAS_PUBLICAS}


def get_all(db):
    rows = db.execute("SELECT * FROM usuarios").fetchall()
    return [to_public_dict(row) for row in rows]


def get_by_id(db, usuario_id):
    row = db.execute("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return to_public_dict(row) if row else None


def get_by_email(db, email):
    """Retorna a linha crua (inclui o hash da senha) — uso exclusivo de autenticação."""
    return db.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()


def create(db, nome, email, senha_hash, tipo="cliente"):
    cursor = db.execute(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        (nome, email, senha_hash, tipo),
    )
    db.commit()
    return cursor.lastrowid


def count(db):
    return db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]

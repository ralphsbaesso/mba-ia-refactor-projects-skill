# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Diferente dos outros projetos, este já possui alguma separação de camadas (`models/`, `routes/`, `services/`, `utils/`), mas ainda contém problemas arquiteturais e de qualidade.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://localhost:5000`. O `seed.py` popula o banco SQLite (`tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Toda configuração vem de variáveis de ambiente (com defaults de desenvolvimento): `SECRET_KEY`, `DATABASE_URL`, `FLASK_DEBUG`, `HOST`, `PORT`, e `SMTP_HOST`/`SMTP_PORT`/`SMTP_USER`/`SMTP_PASSWORD` para o serviço de notificação. Veja `config/settings.py`.

## Testes

```bash
pytest
```

A suíte (em `tests/`) cobre regras de negócio dos models e services, o contrato dos endpoints via test client (banco em memória) e testes de regressão dos findings de segurança (senha nunca sai na API, hash forte de senha, secret via env).

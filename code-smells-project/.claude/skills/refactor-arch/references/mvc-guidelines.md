# Guidelines de Arquitetura — MVC Alvo

Regras do padrão MVC que a Fase 3 deve produzir, agnósticas de tecnologia. O objetivo é separação de responsabilidades testável, não uma estrutura de diretórios decorativa.

## Camadas e responsabilidades

### `config/`
- **Faz**: centraliza toda configuração — secrets, porta, path/URL do banco, flags de debug — lida de **variáveis de ambiente**, com defaults sensatos para desenvolvimento (a app deve subir sem env configurado).
- **Não faz**: não contém valores secretos hardcoded. `SECRET_KEY` default só como placeholder claramente de dev (ex.: `os.environ.get("SECRET_KEY", "dev-only-change-me")`).

### `models/`
- **Faz**: acesso a dados (queries **parametrizadas** ou ORM) e regras intrínsecas da entidade (ex.: `is_overdue()`). Um módulo por entidade/domínio.
- **Não faz**: não conhece HTTP (nada de `request`/`jsonify`/`res`), não formata resposta, não envia notificações. Não expõe campos sensíveis na serialização (senha nunca sai em `to_dict`).

### `views/` ou `routes/`
- **Faz**: apenas mapeamento rota → controller (blueprints/routers). Extração trivial de parâmetros de path.
- **Não faz**: zero regra de negócio, zero acesso a banco, zero validação além de tipos do framework.

### `controllers/` (ou `services/` quando a stack já os usa)
- **Faz**: orquestra o fluxo — interpreta o request, valida input (ou delega a validators), chama models, monta a resposta com status code correto. Regras de negócio que cruzam entidades (checkout, relatórios) vivem aqui ou em services dedicados.
- **Não faz**: não monta SQL, não contém detalhes de conexão de banco.

### `middlewares/` — Error handling centralizado (obrigatório)
- Um único ponto trata exceções: converte erros de domínio em status apropriado (400/404/409) e erros inesperados em 500 **sem vazar internals** (`str(e)` nunca vai ao cliente; stack trace vai para o log).
- Handlers/controllers não precisam de try/catch repetido — lançam exceções de domínio.

### Entry point (composition root) — obrigatório
- Um arquivo pequeno e óbvio (`app.py`, `src/app.js`) que: carrega config, inicializa o banco, registra rotas e o error handler, e sobe o servidor. Nada de regra de negócio.
- Padrão recomendado em Flask: `create_app()` (application factory). Em Express: separar `app` (montagem) do `listen`.

## Regras transversais

1. **Dependências apontam para dentro**: routes → controllers → models. Nunca o contrário.
2. **Contrato preservado**: método + path + formato de resposta dos endpoints originais não mudam.
3. **Segurança mínima**: senhas com hash forte (bcrypt/scrypt/argon2), queries parametrizadas, secrets via env, dados sensíveis fora de logs e respostas.
4. **Sem estado global mutável**: conexão de banco por request/pool ou injetada; caches explícitos.
5. **DRY**: validações e serializações compartilhadas extraídas para um lugar só.
6. **Logging** via biblioteca de logging da stack, não `print`/`console.log` solto.

## Adaptação ao nível de organização do projeto

| Estado atual | Ação da Fase 3 |
|---|---|
| Monolito sem camadas | Criar a estrutura completa acima e migrar o código |
| God Class | Explodir a classe nas camadas acima; entry point vira composition root |
| Camadas parciais (`models/`, `routes/`, `services/` já existem) | **Não recriar nem renomear estrutura existente.** Mover regra de negócio das rotas para services/controllers, extrair `config`, centralizar erros, corrigir segurança/N+1/deprecated. Criar apenas os diretórios que faltam. |

Estrutura de referência para monolitos (adapte nomes à convenção da stack):

```
<projeto>/
├── app.py|app.js          # composition root
├── config/
├── models/
├── views/ ou routes/
├── controllers/
└── middlewares/
```

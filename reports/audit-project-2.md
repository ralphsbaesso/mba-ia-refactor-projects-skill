================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express ^4.18.2 + sqlite3 ^5.1.6 (in-memory)
Files:   3 analyzed | ~180 lines of code
Date:    2026-07-16

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 5 | LOW: 1

## Findings

### [CRITICAL] Hardcoded Credentials / Secrets
File: src/utils.js:1-7
Description: Objeto `config` embute credenciais de produção no código-fonte: senha de banco `dbPass: "senha_super_secreta_prod_123"` (linha 3), chave live de gateway de pagamento `paymentGatewayKey: "pk_live_1234567890abcdef"` (linha 4) e usuário SMTP (linha 5). A chave do gateway ainda é impressa em log junto com o cartão em src/AppManager.js:45.
Impact: Qualquer pessoa com acesso ao repositório obtém credenciais de produção; vazamento da chave `pk_live` permite cobranças reais. Rotação exige mudança de código e redeploy.
Recommendation: Mover secrets para variáveis de ambiente lidas por um módulo `config/` com defaults apenas para valores não-secretos (playbook: "Extrair configuração para ambiente").

### [CRITICAL] God Class / God Module
File: src/AppManager.js:4-139
Description: A classe `AppManager` concentra todas as responsabilidades: cria a conexão SQLite (linha 7), define o schema das 5 tabelas e o seed (linhas 10-23), registra as rotas HTTP (linha 25 em diante) e implementa a regra de negócio de checkout, pagamento, matrícula e relatório financeiro dentro dos handlers.
Impact: Impossível testar regra de negócio sem subir HTTP + banco; qualquer mudança em um domínio arrisca os demais; separação de responsabilidades inexistente.
Recommendation: Decompor em camadas MVC: `config/database.js` (conexão + schema/seed), `models/` (acesso a dados por entidade), `services/` (checkout, relatório), `controllers/` + `routes/` (HTTP) — playbook: "Explodir God Class".

### [CRITICAL] Armazenamento inseguro de senhas
File: src/utils.js:17-23, src/AppManager.js:18, src/AppManager.js:68
Description: `badCrypto()` é "criptografia" caseira — loop de 10.000 iterações concatenando os 2 primeiros chars do base64 da senha, truncado em 10 chars (determinística, sem salt, trivialmente reversível por dicionário). O seed grava senha em texto plano `'123'` (AppManager.js:18) e o checkout usa senha default `"123456"` quando o cliente não envia `pwd` (AppManager.js:68).
Impact: Todas as senhas são recuperáveis; contas criadas sem senha ficam com credencial conhecida publicamente.
Recommendation: Substituir por `bcrypt` (ou `crypto.scrypt` nativo) com salt; rejeitar cadastro sem senha ou com senha fraca (playbook: "Hash de senha seguro").

### [HIGH] Regra de negócio em Controller/Rota (Fat Controller)
File: src/AppManager.js:28-78, src/AppManager.js:80-129
Description: O handler de `POST /api/checkout` (50 linhas) faz validação de payload, lookup/criação de usuário, decisão de pagamento (aprovação por `cc.startsWith("4")`, linha 46), matrícula, registro de pagamento e audit log — tudo inline na rota. O handler de `GET /api/admin/financial-report` monta a agregação do relatório iterando queries dentro da própria rota.
Impact: Regra de negócio intestável isoladamente e não reutilizável; qualquer ajuste de fluxo exige editar o handler HTTP.
Recommendation: Extrair `CheckoutService` e `ReportService`; controllers apenas traduzem HTTP ↔ service (playbook: "Extrair service de fat controller").

### [HIGH] Estado global mutável / Singleton implícito
File: src/utils.js:9-15, src/utils.js:25
Description: `globalCache` (objeto mutável de módulo, alimentado por `logAndCache()` a cada checkout) e o contador `totalRevenue` são estado global compartilhado exportado pelo módulo. `totalRevenue` é exportado por valor e nunca atualizado — estado morto.
Impact: Estado compartilhado entre requests sem controle de ciclo de vida; cache cresce sem limite; comportamento não determinístico em testes.
Recommendation: Eliminar o cache global (ou encapsular em um serviço injetável com política de expiração); remover `totalRevenue` (playbook: "Eliminar estado global").

### [HIGH] Ausência de camadas / acoplamento direto
File: src/app.js:8-10, src/AppManager.js:37-57
Description: O entry point instancia `AppManager` e delega tudo a ele; os handlers HTTP executam SQL diretamente (`this.db.get/run/all`) sem camada de model ou injeção de dependência — o acoplamento HTTP→SQL é direto.
Impact: Nenhuma fronteira arquitetural: impossível trocar banco, mockar acesso a dados ou testar camadas isoladamente.
Recommendation: Introduzir camadas `routes/ → controllers/ → services/ → models/` com a conexão injetada (playbook: "Introduzir camadas + DI").

### [HIGH] Callback Hell / controle de fluxo assíncrono manual
File: src/AppManager.js:37-77, src/AppManager.js:83-128, src/AppManager.js:26
Description: O checkout aninha callbacks em 5 níveis (get curso → get user → run enrollment → run payment → run audit_log), com `const self = this` (linha 26) para driblar o binding de `function(err)`. O relatório financeiro sincroniza a resposta com contadores manuais de pendências (`coursesPending--`/`enrPending--`, linhas 97-98 e 117-121) para decidir quando chamar `res.json`.
Impact: Fluxo frágil e ilegível; um erro esquecido em qualquer nível deixa a request pendurada; race conditions no relatório se um callback falhar.
Recommendation: Promisificar o acesso ao banco e reescrever com `async/await` (playbook: "Callbacks → async/await").

### [MEDIUM] Queries N+1
File: src/AppManager.js:83-126
Description: O relatório financeiro faz 1 query para cursos, depois 1 por curso para matrículas e, para cada matrícula, 2 queries (usuário e pagamento) — para C cursos e E matrículas: 1 + C + 2E queries.
Impact: Latência cresce linearmente com o volume de dados; o padrão de contadores torna o custo ainda mais opaco.
Recommendation: Substituir por uma única query com JOIN entre courses/enrollments/users/payments e agregar em memória (playbook: "N+1 → JOIN").

### [MEDIUM] Tratamento de erros ausente ou genérico
File: src/AppManager.js:57-61, src/AppManager.js:92, src/AppManager.js:104-106, src/AppManager.js:133-136
Description: Erros de DB são ignorados nos callbacks: o insert de audit_log descarta `err` (linha 57), o relatório não checa `err` de enrollments/users/payments (linhas 92, 104, 106) e o DELETE responde sucesso mesmo se a query falhar (linha 133). Onde há tratamento, a resposta é genérica ("Erro DB") sem log estruturado. Não existe error handler centralizado do Express.
Impact: Falhas silenciosas (relatório com dados incompletos, deleção "confirmada" que não ocorreu); depuração impossível.
Recommendation: Checar todos os erros, propagar via `next(err)` e adicionar middleware de erro centralizado (playbook: "Error handler centralizado").

### [MEDIUM] Validação ausente ou duplicada
File: src/AppManager.js:35, src/AppManager.js:66-72, src/AppManager.js:131-137
Description: A única validação do checkout é presença de 4 campos (linha 35) — `pwd` é opcional (cai no default "123456"), não há validação de formato de e-mail nem de cartão. O DELETE de usuário não valida existência nem integridade referencial — a própria mensagem admite que "matrículas e pagamentos ficaram sujos no banco" (linha 135).
Impact: Dados inconsistentes e órfãos no banco; contas criadas com credenciais fracas; payloads arbitrários aceitos.
Recommendation: Camada de validação nos controllers (presença + formato) e regras de integridade no service de usuários (deleção em cascata ou bloqueio) — playbook: "Validação em camada própria".

### [MEDIUM] Configuração hardcoded (não-secreta)
File: src/utils.js:6, src/AppManager.js:7
Description: Porta `3000` fixa no objeto `config` e path do banco `':memory:'` hardcoded no construtor. O banco em memória perde todos os dados a cada restart (comportamento a preservar ou parametrizar conscientemente).
Impact: Impossível variar ambiente (porta/banco) sem editar código.
Recommendation: `config/` lendo `process.env.PORT` e `process.env.DB_PATH` com defaults (playbook: "Extrair configuração para ambiente").

### [MEDIUM] API Deprecated — sqlite3 com API de callbacks
File: src/AppManager.js:1, src/AppManager.js:7
Description: Uso do driver `sqlite3` (^5.1.6) com API de callbacks — padrão legado que induz o callback hell do finding acima.
Impact: Código assíncrono manual, propenso a erros engolidos; ecossistema migrou para APIs promisificadas/síncronas.
Recommendation: Migrar para `better-sqlite3` (síncrono) ou wrapper promisificado do `sqlite3`, viabilizando `async/await`.

### [LOW] Nomenclatura ruim / código morto / console.log como log
File: src/AppManager.js:29-33, src/AppManager.js:45, src/utils.js:13, src/utils.js:10
Description: Variáveis de 1-3 letras no checkout (`u`, `e`, `p`, `cid`, `cc`); mistura de idiomas (rotas/mensagens PT + código EN); `console.log` como único mecanismo de log — incluindo o log do número do cartão com a chave do gateway (AppManager.js:45, também um vazamento de dado sensível); `totalRevenue` exportado e nunca usado (código morto).
Impact: Legibilidade baixa; dados sensíveis em stdout; código morto confunde manutenção.
Recommendation: Renomear para nomes descritivos, remover código morto, nunca logar cartão/secret (playbook: "Higiene de nomes e logs").

## Deprecated APIs
- `sqlite3` callback API → `better-sqlite3` ou wrapper promisificado (`node:sqlite` no Node ≥ 22) — src/AppManager.js:1, src/AppManager.js:7.
- Nenhuma outra API deprecated detectada (o projeto já usa `express.json()` embutido e `Buffer.from(...)`).

================================
Total: 13 findings
================================

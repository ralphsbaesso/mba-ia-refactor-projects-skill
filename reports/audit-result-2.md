
```bash
  PHASE 3: REFACTORING COMPLETE
  ================================
  ## New Project Structure
  ecommerce-api-legacy/
  ├── package.json              # scripts: start (node src/server.js), test (jest)
  ├── src/
  │   ├── server.js             # entry point: abre DB, initDb, listen
  │   ├── app.js                # composition root: exporta createApp(db) sem listen
  │   ├── config/index.js       # PORT, DB_PATH, PAYMENT_GATEWAY_KEY via env
  │   ├── db/
  │   │   ├── connection.js     # sqlite3 promisificado (async/await)
  │   │   └── schema.js         # CREATE TABLEs + seed idempotente (senha com hash)
  │   ├── models/               # userModel, courseModel, enrollmentModel,
  │   │                         # paymentModel, auditLogModel, reportModel (JOIN)
  │   ├── services/             # checkoutService, reportService, userService,
  │   │                         # passwordService (scrypt + salt)
  │   ├── controllers/          # checkoutController, reportController, userController
  │   ├── routes/index.js       # apenas mapeamento rota → controller
  │   └── middlewares/errorHandler.js  # ApiError + handler centralizado
  └── tests/                    # helpers, models.test, services.test, endpoints.test
  
  ## Validation
    ✓ Application boots without errors      (npm start — "rodando na porta 3000", zero warnings)
    ✓ All endpoints respond correctly       (7 casos via curl: checkout 200/400/404,
                                             financial-report 200, delete 200/404)
    ✓ Unit tests pass (jest: 22 passed, 3 suites)  — comando: npm test
    ✓ Zero anti-patterns remaining          (13 findings do relatório corrigidos)
  ================================           
   
  Checklist do desafio (projeto 2 — ecommerce-api-legacy): todos os itens das Fases 1, 2 e 3 estão atendidos — stack detectada (Node/Express 4.18 + sqlite3), relatório em
  reports/audit-project-2.md com 13 findings citando arquivo:linha, pausa [y/n] respeitada, estrutura MVC completa, config via env, error handling centralizado, boot limpo e endpoints
  preservados.

  Destaques do que mudou em relação ao contrato original (melhorias intencionais dos findings): usuário novo sem senha agora é rejeitado (antes ganhava senha default "123456"), DELETE 
  /api/users/:id deleta em cascata matrículas/pagamentos (antes deixava órfãos) e devolve 404 para usuário inexistente, e o relatório financeiro usa 1 query com JOIN em vez de 1+C+2E queries
  — mesmo formato de resposta.

  Nota lateral: o npm install demorou por causa de um npm install órfão de outro projeto (sofi-ai-frontend, PID 97746, rodando há 10h+) que congestiona o cache; contornei com cache isolado e
  não toquei nesse processo — talvez valha matá-lo manualmente.


```

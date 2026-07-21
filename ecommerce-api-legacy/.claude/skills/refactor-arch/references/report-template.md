# Template do Relatório de Auditoria (Fase 2)

Formato obrigatório. Findings ordenados por severidade (CRITICAL → HIGH → MEDIUM → LOW). Cada finding cita arquivo e linha(s) exatos.

```markdown
================================
ARCHITECTURE AUDIT REPORT
================================
Project: <nome-do-diretorio>
Stack:   <linguagem + framework + versão>
Files:   <N> analyzed | ~<LOC> lines of code
Date:    <AAAA-MM-DD>

## Summary
CRITICAL: <n> | HIGH: <n> | MEDIUM: <n> | LOW: <n>

## Findings

### [<SEVERIDADE>] <Nome do anti-pattern (item do catálogo)>
File: <arquivo>:<linha ou intervalo>[, <arquivo>:<linha> ...]
Description: <o que foi encontrado, concreto e específico>
Impact: <consequência prática (segurança, manutenção, performance)>
Recommendation: <transformação a aplicar (referencie o playbook)>

<... repetir para cada finding ...>

## Deprecated APIs
<Para cada API obsoleta: API → equivalente moderno, com arquivo:linha.
Se nenhuma: "Nenhuma API deprecated detectada.">

================================
Total: <N> findings
================================
```

Regras:

1. `File:` sempre com número(s) de linha reais, conferidos no arquivo.
2. Um finding por anti-pattern por contexto — ocorrências múltiplas do mesmo padrão podem ser agrupadas num finding listando todos os `arquivo:linha`.
3. `Description` específica e acionável ("query SQL montada por concatenação com input do usuário em `models.py:28`"), nunca genérica ("código ruim").
4. O sumário de contagem deve bater com a lista de findings.
5. Salvar o relatório em `reports/audit-project-{N}.md` e também exibi-lo no chat.

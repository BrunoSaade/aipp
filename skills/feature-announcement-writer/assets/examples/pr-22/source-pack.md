## PR #22: Feat/criacao devices em lote
URL: https://github.com/BrunoSaade/tapleva/pull/22 | +7001/-107

### Descrição do PR
(vazia)

### Doc: .specs/features/criacao-devices-em-lote/spec.md
# Criação de Devices em Lote Specification

## Problem Statement

Para preparar placas de acrílico antes da venda, o operador cria cada Device
no backoffice, baixa o QR de cada link um a um e cola cada PNG na arte do
Canva. Com 45 placas isso vira 45 formulários + 45+ downloads + 45+ colagens
manuais — lento e sujeito a trocar QR de placa.

A criação de Devices em `inventory` sem Customer/Target já é o fluxo esperado
(`pre-provisionamento-dispositivos`), e aquela spec deixou "Batch device
generation" como escopo futuro. Esta feature entrega esse lote: N Devices numa
única operação e um ZIP com todos os QR PNGs + um CSV manifesto que casa cada
arquivo com sua placa (e serve ao Canva Bulk Create / app QR Batch e à gravação
de NFC).

## Goals

- [ ] Operador cria 45 Devices em inventory com 1 formulário e 1 submissão.
- [ ] Operador obtém todos os QR PNGs do lote num único `.zip` com 1 clique, a qualquer momento depois da criação.
- [ ] Cada PNG do ZIP é identificável sem abrir o arquivo (nome traz sequência, posição e `publicCode`).
- [ ] Operação inteira cabe no plano Cloudflare Workers Free (10 ms CPU/request, 50 queries D1/invocação).

## Out of Scope

| Feature | Reason |
| ------- | ------ |
| Integração com API do Canva | Canva consome o ZIP/CSV manualmente (Bulk Create, app QR Batch); integração é outra feature. |
| PNG em alta resolução ou SVG no ZIP | Decisão do grilling: manter 222 px, igual ao download unitário. |
| Geração do ZIP no servidor | Workers Free: ~1,6 ms CPU por PNG estoura 10 ms com 45 placas (medido). ZIP é montado no navegador. |
| Lote misto (linkCount diferente por Device) | Decisão do grilling: linkCount uniforme; lote misto = dois lotes. |
| Atribuir Customer/Target na criação do lote | Lote é pré-venda; atribuição segue o fluxo unitário existente. |
| Tela "Lotes" dedicada no menu | Decisão do grilling: filtro na lista + página do lote bastam. |
| Editar, excluir ou mudar status em lote | Operações seguem unitárias. |
| Local e Observações no formulário do lote | Decisão do grilling: só Tipo físico é campo comum. |
| Gravação automática de NFC | CSV traz `nfc_url`; gravação continua manual. |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --------------------- | -------------- | --------- | ---------- |
| Conteúdo do download | ZIP com PNG por link ativo + `manifest.csv` | Grilling Q1. | y |
| Re-download | Página do lote regenera o ZIP a qualquer momento | Grilling Q2. | y |
| Nome dos Devices | `{prefixo} {NNN}`, NNN com 3 dígitos (001..100) | Grilling Q3/Q4-rodada4; 3 dígitos cobrem o máximo de 100. | y |
| Links por Device | 1 valor 1..4 para o lote inteiro, padrão 1 | Grilling Q4. | y |
| Código do lote | Sugerido `LOTE-AAAAMMDD-NN` (data em America/Sao_Paulo, NN = menor sequencial livre do dia), editável | Grilling rodada 2 Q1; fuso igual a `BUSINESS_TIME_ZONE`. | y |
| Unicidade do código | Rejeita código já usado por qualquer Device (inclusive excluído) ou lote existente | Código nunca é reutilizado; evita misturar lote novo com lote manual antigo. | y |
| Formato do código novo | `^[A-Za-z0-9_-]{1,40}$` | Vai em URL e nome de arquivo; lotes legados digitados à mão continuam acessíveis via URL codificada. | n |
| Prefixo do nome | Texto não vazio após trim, até 60 caracteres | Nome final ≤ 64 caracteres, legível na lista. | n |
| Limite do lote | 1..100 Devices | Grilling rodada 2 Q2. | y |
| Auditoria | 1 entrada `device.batch_create` por lote | Grilling rodada 3 Q2; cabe no orçamento de 50 queries. | y |
| Exclusões do ZIP/manifesto | Devices com `deleted_at` e links com `active = false` ficam fora | Grilling rodada 3 Q3; placa morta não é reimpressa. | y |
| Onde o ZIP é montado | Navegador busca cada PNG no endpoint existente de link e empacota | Grilling rodada 3 Q1; PNG idêntico ao download unitário. | y |
| Concorrência do download | 6 requests simultâneos, 1 nova tentativa por PNG | Limite usual de conexões por host HTTP/1.1; evita rajada no Worker. | n |
| CSV | UTF-8 sem BOM, separador vírgula, aspas RFC 4180, fim de linha `\r\n` | Canva Bulk Create lê CSV com vírgula; BOM pode aparecer como caractere no primeiro cabeçalho. | n |
| Ordem das entradas | Nome do Device ascendente, depois posição do link | Mesma ordem da lista de devices (`orderBy name, id`); nomes com NNN ordenam certo. | n |
| Pós-criação | Redireciona para página do lote; ZIP só com clique | Grilling rodada 4 Q3. | y |
| Colisão de `publicCode` | Lote inteiro falha com 409; operador reenvia | Probabilidade ~0 (32^10); retry automático é complexidade especulativa. | n |

**Open questions:** none — all resolved or logged above.

### Implicit-requirement dimensions sweep

| Dimension | Resolution |
| --------- | ---------- |
| Input validation & bounds | LOTE-06..LOTE-10 |
| Failure / partial-failure states | LOTE-05 (criação atômica), LOTE-22 (falha de PNG) |
| Idempotency / retry / duplicate handling | LOTE-09, LOTE-12 (duplo submit), LOTE-22 (retry) |
| Auth boundaries & rate limits | LOTE-28; rate limit N/A because rotas de sessão do backoffice não têm rate limit hoje e o volume (≤ 400 GETs por download) é de um operador autenticado |
| Concurrency / ordering | LOTE-12, LOTE-16 (ordem), LOTE-18 (concorrência de fetch) |
| Data lifecycle / expiry | LOTE-17; ZIP não é armazenado (regenerado sob demanda) |
| Observability | LOTE-11 (auditoria) |
| External-dependency failure | LOTE-05 (D1), LOTE-22 (fetch de PNG) |
| State-transition integrity | LOTE-02 (nasce `inventory`); nenhuma transição nova |

---

## User Stories

### P1: Criar lote de Devices em inventory ⭐ MVP

**User Story**: Como operador TapLeva, quero criar N Devices em inventory numa única operação para preparar um lote de placas antes da venda.

**Why P1**: Sem isso o operador repete o formulário unitário N vezes.

**Acceptance Criteria**:

1. WHEN operador abre `GET /devices/batches/new` THEN sistema SHALL exibir formulário com: prefixo do nome, quan
[truncado]

### Doc: .specs/features/criacao-devices-em-lote/requirements.md
# Criação de Devices em Lote — Requirements Table

**Spec:** `.specs/features/criacao-devices-em-lote/spec.md`
**Design:** `.specs/features/criacao-devices-em-lote/design.md`
**Tasks:** `.specs/features/criacao-devices-em-lote/tasks.md`
**Status:** Draft
**Created:** 2026-09-25

> Cada linha é uma regra isolada: **Cenário** diz quando vale, **Expressão** diz o que acontece, **Complemento** diz por quê, **Caminho** marca sucesso (SP) ou erro (EP). Nenhuma linha depende de dado de exemplo.

---

## 1. Acesso

| Requisito | Cenário | Expressão | Complemento | Caminho |
| --------- | ------- | --------- | ----------- | ------- |
| FR-001 | Acesso sem sessão | **Given** um visitante sem sessão de admin válida **When** abre qualquer tela ou endpoint de lote **Then** é mandado para o login **And** nenhum dado de lote é exibido | Lote expõe códigos públicos de placas ainda não vendidas; só operador autenticado vê. | EP |
| FR-002 | Envio sem token CSRF | **Given** um operador logado **When** envia o formulário de lote sem token CSRF válido **Then** o envio é rejeitado como nas demais ações do backoffice **And** nenhum Device é criado | Impede que outro site dispare a criação de dezenas de Devices em nome do operador. | EP |

---

## 2. Formulário de criação

| Requisito | Cenário | Expressão | Complemento | Caminho |
| --------- | ------- | --------- | ----------- | ------- |
| FR-003 | Abrir formulário | **Given** um operador logado **When** abre o formulário de novo lote **Then** vê os campos prefixo do nome, quantidade, links por placa, tipo físico e código do lote | Tudo que o lote precisa cabe numa tela; local e observações ficam de fora porque só se definem na venda. | SP |
| FR-004 | Valor inicial de links por placa | **Given** o formulário aberto **When** o operador não mexe em links por placa **Then** o valor é 1 | Placa com um único QR/NFC é o caso comum. | SP |
| FR-005 | Código de lote sugerido | **Given** o formulário aberto **When** a tela carrega **Then** o código vem preenchido no formato `LOTE-` + data de hoje no fuso de São Paulo (ano, mês, dia) + `-` + sequencial de 2 dígitos **And** o sequencial é o menor ainda não usado naquele dia | Evita o operador inventar código e colidir; data no fuso local bate com o dia de trabalho, não com o UTC. | SP |
| FR-006 | Código sugerido é editável | **Given** o código sugerido **When** o operador troca o texto **Then** vale o código digitado, sujeito às mesmas regras de validação e unicidade | Operador pode alinhar o código a uma etiqueta física ou pedido do fornecedor. | SP |

---

## 3. Validação da entrada

Toda rejeição desta seção responde 400, reexibe o formulário com os valores enviados e não cria nada.

| Requisito | Cenário | Expressão | Complemento | Caminho |
| --------- | ------- | --------- | ----------- | ------- |
| FR-007 | Quantidade dentro do limite | **Given** quantidade inteira entre 1 e 100 **When** o formulário é enviado **Then** a quantidade é aceita | 100 cobre com folga o lote típico e mantém a criação dentro do limite de 50 comandos de banco por requisição do plano gratuito. | SP |
| FR-008 | Quantidade fora do limite ou não inteira | **Given** quantidade menor que 1, maior que 100, fracionária ou não numérica **When** o formulário é enviado **Then** aparece a mensagem de quantidade entre 1 e 100 **And** nada é criado | Lote vazio não faz sentido; lote gigante estoura o orçamento de banco. | EP |
| FR-009 | Links por placa dentro do limite | **Given** links por placa inteiro entre 1 e 4 **When** o formulário é enviado **Then** o valor é aceito | É o mesmo limite da criação unitária de Device. | SP |
| FR-010 | Links por placa fora do limite | **Given** links por placa menor que 1, maior que 4 ou não inteiro **When** o formulário é enviado **Then** aparece a mensagem de links entre 1 e 4 **And** nada é criado | Uma placa física não comporta mais de 4 códigos. | EP |
| FR-011 | Prefixo válido | **Given** prefixo com 1 a 60 caracteres após remover espaços das pontas **When** o formulário é enviado **Then** o prefixo é aceito | Nome final (prefixo + sequência) fica curto e legível nas listas. | SP |
| FR-012 | Prefixo vazio ou longo | **Given** prefixo vazio, só com espaços ou com mais de 60 caracteres **When** o formulário é enviado **Then** aparece a mensagem de prefixo com até 60 caracteres **And** nada é criado | Device sem nome é indistinguível na lista. | EP |
| FR-013 | Formato do código de lote | **Given** código com 1 a 40 caracteres entre letras sem acento, números, hífen e sublinhado **When** o formulário é enviado **Then** o código é aceito | O código entra na URL da página e no nome do arquivo ZIP; esse alfabeto não precisa de escape em nenhum dos dois. | SP |
| FR-014 | Código com caractere proibido | **Given** código com espaço, acento, outro símbolo ou mais de 40 caracteres **When** o formulário é enviado **Then** aparece a mensagem de caracteres permitidos **And** nada é criado | Mesmo motivo da regra anterior, lado negativo. | EP |
| FR-015 | Tipo físico opcional | **Given** tipo físico em branco **When** o formulário é enviado **Then** os Devices ficam sem tipo físico **And** com tipo preenchido todos recebem o mesmo valor | Material da placa costuma ser igual no lote inteiro. | SP |

---

## 4. Conteúdo do lote criado

| Requisito | Cenário | Expressão | Complemento | Caminho |
| --------- | ------- | --------- | ----------- | ------- |
| FR-016 | Quantidade exata | **Given** envio válido com quantidade N **When** o lote é criado **Then** existem exatamente N Devices novos com aquele código de lote | Uma placa física = um Device. | SP |
| FR-017 | Devices nascem em estoque | **Given** um lote criado **When** qualquer Device dele é consultado **Then** está em estoque (`inventory`) **And** não tem cliente nem destino | Lote é pré-venda; QR em estoque não redireciona para ninguém até a atribuição. | SP |
| FR-018 | Nome sequencial | **Given** um lote criado **When** os Devices são listados **Then** cad
[truncado]

### Commits
- feat(criacao-devices-em-lote): add documents
- feat(db): add device_batches table and batch audit action
- feat(validation): add device batch create schema
- feat(lib): add device batch naming helpers
- feat(lib): add csv writer with formula guard
- feat(repositories): filter devices by batch code
- feat(repositories): add atomic device batch creation
- feat(repositories): list device batch manifest rows
- feat(services): create device batches
- feat(services): build device batch manifest
- feat(backoffice): add in-browser batch zip download script
- feat(backoffice): add device batch views
- feat(backoffice): add device batch routes
- feat(backoffice): link devices to their batch
- feat(backoffice): filter device list by batch
- docs(architecture): document device batch creation
- test(repositories): assert persisted batch rows and query budget
- test(backoffice): pin batch download concurrency and retry
- test(lib): cover every csv formula guard trigger
- fix(validation): reject reserved device batch code new
- docs(spec): align batch atomicity with audit trade-off
- docs(spec): document reserved device batch code new
- docs(readme): document device batches in the operations runbook
- feat(validation): add validation report for batch device creation

### Arquivos
- source: 18
- tests: 11
- docs: 8
- generated: 5
  - drizzle/0010_material_wendell_rand.sql
  - src/app/admin.ts
  - src/app/shared.ts
  - src/db/schema.ts
  - src/index.ts
  - src/lib/csv.ts
  - src/lib/device-batch-naming.ts
  - src/repositories/admin-audit-log.repository.ts
  - src/repositories/device-batch.repository.ts
  - src/repositories/device.repository.ts
  - src/routes/backoffice-auth.ts
  - src/routes/backoffice-device-batches.ts
  - src/routes/backoffice-devices.ts
  - src/schemas/validation.ts
  - src/services/device-batch.service.ts
  - src/views/device-batch-download-script.ts
  - src/views/device-batches.ts
  - src/views/devices.ts
  - tests/backoffice-device-batches.test.ts
  - tests/backoffice-devices.test.ts
  - tests/csv.test.ts
  - tests/device-batch-download-script.test.ts
  - tests/device-batch-naming.test.ts
  - tests/device-batch-repository.test.ts
  - tests/device-batch-service.test.ts
  - tests/device-repository.test.ts
  - tests/schema-migration.test.ts
  - tests/validation.test.ts
  - tests/views.test.ts

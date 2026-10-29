## PR #10: Feat/operacoes via qr scaner
URL: https://github.com/BrunoSaade/tapleva/pull/10 | +1132/-8

### Descrição do PR
(vazia)

### Doc: .specs/features/operacoes-via-qr-scanner/PRD.md
# PRD — Busca de device por scan de QR code no backoffice

## Problema

Operador provisiona muitos devices em estoque. Cada device fisico precisa ser identificado no backoffice (definir cliente, destino, status) pra operar nele. Hoje: busca manual por nome/publicCode/cliente na lista `/devices`. Nao escala bem quando o operador esta com o device fisico na mao — teria que ler o codigo impresso e digitar.

## Solucao

Nova pagina `/devices/scan` no backoffice: liga a camera, le o QR ja impresso no device, decodifica a URL, identifica o device e abre a pagina de detalhe dele (ja e o hub de operacoes: lifecycle, associacao, etc).

## Escopo

**Dentro do escopo:**
- Pagina de scan com camera
- Decode de QR e extracao do codigo do device
- Lookup exato do device pelo codigo
- Redirect pra pagina de detalhe do device
- Tratamento de erro (QR invalido, device nao encontrado)
- Fallback sem camera (campo de texto manual)
- Entry point (botao) na lista de devices

**Fora do escopo (backlog, nao desenhar agora):**
- Historico/analytics de scans feitos no backoffice (existe tabela `scan_events` que registra scans do QR publico, mas essa e outra coisa — nao misturar)
- Fluxo de bulk scan (escanear varios devices em sequencia pra acao em lote, tipo atribuir cliente pra N devices)
- Fluxo mobile-otimizado dedicado (PWA, app nativo)
- Integracao com impressao de etiqueta fisica

## Contexto tecnico ja existente (nao recriar)

- Device ja tem `publicCode` unico. QR gerado (`/devices/:id/qr.svg`, `/devices/:id/qr.png`) com payload = URL publica completa `/q/:publicCode` (rota de redirect do usuario final, em `src/routes/redirect.ts` — nao mexer nela).
- Lista `/devices` (`src/routes/backoffice-devices.ts`) ja filtra por `publicCode` via LIKE parcial (`src/repositories/device.repository.ts`, funcao `getPublicCodeCondition`).
- `findByPublicCode` (match exato) ja existe no repository.
- Pagina de detalhe `/devices/:id` (`renderDeviceDetailPage` em `src/views/devices.ts`) ja e o hub de operacoes — destino final do scan, nao recriar.
- Router `createBackofficeDeviceRoutes` usa `Hono<AdminSessionEnvironment>`, protegido por middleware de sessao admin (`src/middleware/admin-session.ts`).
- Stack: Cloudflare Workers + Hono, HTML server-rendered, sem build step de frontend (JS vanilla inline/vendored), Drizzle ORM + D1.

## Requisitos funcionais

1. **Rota**: `GET /devices/scan`, no mesmo router de devices, protegida pelo mesmo middleware de sessao admin.
2. **Entry point**: botao "Escanear QR" na lista `/devices`, linkando pra `/devices/scan`.
3. **Leitura de QR**: usa `BarcodeDetector` nativo do browser quando disponivel; fallback pra lib `jsQR` (JS puro) quando `BarcodeDetector` nao existir.
4. **Decode**: extrai o `publicCode` do path da URL decodificada (formato esperado `/q/:publicCode`). Nao altera o payload do QR existente.
5. **Lookup**: busca exata via `findByPublicCode` (ja existe).
6. **Sucesso (match unico)**: redirect direto pra `/devices/:id` do device encontrado. Sem tela de confirmacao intermediaria.
7. **Erro (QR invalido ou code nao encontrado)**: mensagem de erro inline na propria pagina `/devices/scan`. Camera continua ativa, permite nova tentativa sem reload de pagina.
8. **Fallback sem camera** (permissao negada, indisponivel, ou erro): campo de texto manual na mesma pagina pra digitar o `publicCode`.
   - Busca PARCIAL (LIKE), mesma logica ja usada no filtro da lista `/devices`.
   - Se 1 resultado: redirect direto pro device.
   - Se varios resultados: mostra lista pra escolher (pode reusar tabela/UI ja existente da lista `/devices`).
   - Se 0 resultados: mensagem de erro, permite tentar de novo.

## Fora de escopo explicito (nao fazer)

- Nao mudar o payload do QR (continua sendo a URL publica `/q/:publicCode`).
- Nao criar tela de confirmacao entre scan e redirect quando ha match unico.
- Nao construir historico de scans do backoffice nem reusar `scan_events` pra isso.
- Nao construir fluxo de acao em lote (bulk).

## Riscos / pontos de atencao pro spec

- `BarcodeDetector` tem suporte limitado (Chrome/Edge); validar se o publico do backoffice e Chrome-only ou se o fallback `jsQR` precisa ser robusto o bastante pra Safari/Firefox tambem.
- Acesso a camera exige HTTPS (ou localhost) — confirmar que ambiente de dev/preview cumpre isso.
- Nenhuma migration de banco necessaria — feature e 100% sobre dados/rotas ja existentes.


### Doc: .specs/features/operacoes-via-qr-scanner/spec.md
# Busca de device por scan de QR code no backoffice Specification

## Problem Statement

Operador provisiona muitos devices em estoque. Cada device fisico precisa ser identificado no backoffice (cliente, destino, status) pra operar nele. Hoje a busca e manual por nome/publicCode/cliente na lista `/devices`, o que nao escala quando o operador esta com o device fisico na mao.

## Goals

- [ ] Operador escaneia o QR ja impresso no device e cai direto na pagina de detalhe dele, sem digitar nada.
- [ ] Operador sem camera (ou com camera indisponivel) ainda consegue localizar o device digitando o `publicCode`.

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature                                         | Reason                                                              |
| ------------------------------------------------ | -------------------------------------------------------------------- |
| Historico/analytics de scans do backoffice        | `scan_events` registra scans do QR publico (usuario final) — feature diferente, nao misturar |
| Bulk scan (varios devices em sequencia)           | Fora do escopo do PRD; fluxo de acao em lote fica pra depois         |
| Fluxo mobile-otimizado dedicado (PWA/app nativo)  | Fora do escopo do PRD                                                |
| Integracao com impressao de etiqueta fisica       | Fora do escopo do PRD                                                |
| Tela de confirmacao entre scan e redirect (match unico) | PRD explicito: redirect direto, sem confirmacao intermediaria |
| Mudanca no payload do QR                          | Continua sendo a URL publica `/q/:publicCode`; rota `redirect.ts` nao e tocada |

---

## Assumptions & Open Questions

| Assumption / decision | Chosen default | Rationale | Confirmed? |
| --- | --- | --- | --- |
| Suporte de browser pro scanner | `BarcodeDetector` nativo quando disponivel (Chrome/Edge/alguns Android); fallback `jsQR` (JS puro, decodifica frame de `<canvas>`) cobre Safari/Firefox | PRD marca isso como risco explicito; `jsQR` roda em qualquer browser com `getUserMedia` + canvas, entao cobre o gap sem exigir HTTPS extra nem lib nativa | n |
| Entrega do `jsQR` ao browser | Carregado via `<script src>` de CDN (jsdelivr, versao fixada) na propria pagina `/devices/scan`, em vez de vendorizado como constante local (padrao usado hoje so pro CSS) | Reproduzir o source completo do jsQR localmente esbarra em limite de reproducao de codigo de terceiros com direito autoral; CDN evita esse risco, mantem a lib atualizavel e o backoffice ja depende de rede pra sessao admin, entao nao adiciona uma dependencia de rede nova | y |
| Ambiente dev/preview sem HTTPS | Camera falha silenciosamente ao carregar (permissao negada / `getUserMedia` indisponivel) e a pagina cai direto no fallback de texto manual — mesmo caminho de erro que "permissao negada" | `getUserMedia` exige contexto seguro (HTTPS ou localhost); dev local (`wrangler dev` em `localhost`) e contexto seguro por definicao do browser, entao nao ha caso real de bloqueio em dev. Preview/staging em HTTP ficaria no fallback, que ja e requisito funcional | n |
| Extracao do `publicCode` de QR com URL inesperada (dominio diferente, path fora do formato `/q/:code`) | Trata como "QR invalido" (mesmo erro de decode malformado) | PRD define decode como extrair path `/q/:publicCode`; qualquer coisa fora desse formato nao tem `publicCode` extraivel | n |
| Debounce de decodes repetidos do mesmo QR (camera contínua vai decodificar o mesmo frame varias vezes por segundo) | Apos decode bem-sucedido, pausa a leitura ate a navegacao (redirect) ou ate limpar o erro; nao dispara lookup duplicado pro mesmo valor decodificado em sequencia | Nao mencionado no PRD; sem isso a pagina dispararia N lookups identicos por segundo enquanto o QR esta em frame | n |

**Open questions:** none — todas as ambiguidades tecnicas do PRD (secao "Riscos") foram resolvidas acima como assumptions.

---

## User Stories

### P1: Scan de QR com match direto ⭐ MVP

**User Story**: Como operador de backoffice, quero escanear o QR impresso no device com a camera do dispositivo que estou usando, pra cair direto na pagina de detalhe do device sem digitar nada.

**Why P1**: E o caminho principal do PRD — resolve o problema de escala (nao precisar digitar codigo com device na mao).

**Acceptance Criteria**:

1. WHEN o operador acessa `GET /devices/scan` THEN o sistema SHALL solicitar acesso a camera e, se concedido, exibir o feed de video ativo na pagina.
2. WHEN a camera detecta e decodifica um QR code com sucesso THEN o sistema SHALL extrair o `publicCode` do path da URL decodificada (formato `/q/:publicCode`).
3. WHEN o `publicCode` extraido tem exatamente 1 device correspondente (via `findByPublicCode`, match exato) THEN o sistema SHALL redirecionar o navegador para `/devices/:id` desse device, sem tela de confirmacao intermediaria.
4. The system SHALL manter a rota `GET /devices/scan` no mesmo router de devices (`createBackofficeDeviceRoutes`), protegida pelo middleware de sessao admin (`src/middleware/admin-session.ts`).
5. The system SHALL NOT alterar o payload do QR gerado (`/devices/:id/qr.svg`, `/devices/:id/qr.png`) nem a rota `src/routes/redirect.ts`.

**Independent Test**: Acessar `/devices/scan` autenticado, apontar camera pra um QR de device existente, confirmar redirect automatico pra `/devices/:id` correto.

---

### P1: Tratamento de erro sem reload ⭐ MVP

**User Story**: Como operador, quero ver uma mensagem clara quando o QR e invalido ou o device nao existe, e poder tentar de novo na hora, sem recarregar a pagina.

**Why P1**: PRD marca como requisito funcional explicito (FR7); sem isso o scan trava em erro silencioso ou forca reload, quebrando o fluxo continuo de escanear varios devices em sequencia manual.

**Acceptance Criteria**:

1. IF o QR decodificado nao tem o formato esperado (`/q/:publicCode`) THEN o sistema SHALL exibir mensagem de erro inline n
[truncado]

### Commits
- feat(devices): add exact publicCode lookup to device service
- feat(devices): add scan page view with camera and manual fallback
- feat(devices): add QR scan routes and entry point
- fix(devices): extract scan decode logic to testable module, close ver…
- test(devices): pin clearError-before-decode ordering for QRSCAN-09
- docs(devices): log QRSCAN-09 closure in validation report

### Arquivos
- source: 4
- tests: 2
- docs: 3
- generated: 0
  - src/lib/scan-decode.ts
  - src/routes/backoffice-devices.ts
  - src/services/device.service.ts
  - src/views/devices.ts
  - tests/backoffice-devices.test.ts
  - tests/scan-decode.test.ts

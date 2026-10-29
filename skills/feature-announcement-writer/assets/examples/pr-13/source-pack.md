## PR #13: Feat/landing page
URL: https://github.com/BrunoSaade/tapleva/pull/13 | +1361/-3

### Descrição do PR
(vazia)

### Doc: .specs/features/landing-page-institucional/spec.md
# Spec: Landing Page Institucional TapLeva

## Contexto

Placas físicas NFC/QR da TapLeva trazem a marca "TapLeva" impressa. Quem
pesquisar "TapLeva" precisa encontrar uma página institucional que explique o
produto e ofereça um caminho de contato via WhatsApp. Hoje não existe worker
servindo o domínio raiz `tapleva.com.br` — só `go.` (redirect crítico) e
`admin.` (backoffice) existem.

## Escopo

Uma landing page (LP) single-page, estática, servida por um novo Cloudflare
Worker isolado, com identidade visual replicando as placas físicas e um
formulário que monta um link `wa.me` e redireciona o visitante para o
WhatsApp.

## Fora de escopo (explicitamente)

- Persistência de leads (D1, KV ou qualquer storage).
- Analytics/tracking (GA4, Meta Pixel).
- Múltiplos idiomas (só pt-BR).
- Qualquer alteração nos workers `go` (redirect) ou `admin` (backoffice).
- CMS ou conteúdo editável em runtime — conteúdo é estático no código.

## Requisitos (EARS)

### Renderização

- **REQ-1**: O sistema DEVE, quando uma requisição `GET /` chega ao worker
  `tapleva-lp`, retornar HTTP 200 com um documento HTML único (single-page)
  contendo as seções: Hero, Como funciona, Casos de uso, Diferencial, Form de
  contato, Footer.
- **REQ-2**: O sistema DEVE renderizar o HTML via template string
  server-side (mesmo padrão de `src/views/html.ts`), sem framework de
  frontend (React/Next proibidos por ARCHITECTURE.md §3/§6).
- **REQ-3**: O sistema DEVE aplicar a identidade visual das placas físicas:
  fundo branco (`#FFFFFF`), texto/títulos em verde-escuro quase preto
  (`#10241F`), destaque/CTA em dourado (`#E1A636`), tipografia bold
  arredondada (Google Fonts, ex: Poppins/Nunito), e um ícone de raio
  decorativo recriado em SVG inline (sem asset externo).
- **REQ-4**: TODA saída de texto dinâmico (se houver) DEVE passar por escape
  HTML equivalente ao `escapeHtml` de `src/views/html.ts`. (Nota: como o
  conteúdo é 100% estático nesta feature, este requisito vale como guarda
  para o form, que é client-side e não retorna HTML gerado por input do
  usuário.)

### Formulário → WhatsApp

- **REQ-5**: O sistema DEVE exibir um formulário HTML com campos Nome
  (obrigatório), Telefone (obrigatório) e Mensagem (opcional).
- **REQ-6**: QUANDO o visitante submete o formulário, o sistema DEVE, via
  JavaScript inline no browser (sem `fetch`, sem chamada de rede própria),
  montar a URL `https://wa.me/<WHATSAPP_NUMBER>?text=<mensagem_codificada>`
  incluindo nome/telefone/mensagem informados, e navegar o browser para essa
  URL (`window.location.href`).
- **REQ-7**: O número de destino DEVE vir de uma variável de configuração
  (`WHATSAPP_NUMBER`, injetada como `vars` no `wrangler.lp.jsonc`), nunca
  hard-coded no HTML/JS gerado a partir de literal solto sem nome.
- **REQ-8**: SE o campo Nome ou Telefone estiver vazio, ENTÃO o sistema DEVE
  impedir a submissão usando validação HTML nativa (`required`), sem exigir
  JavaScript adicional para essa validação básica.
- **REQ-9**: A mensagem pré-preenchida padrão (quando o campo Mensagem for
  deixado em branco) DEVE ser "Olá! Vim do site TapLeva e quero saber mais
  sobre as placas.", prefixada com nome e telefone informados.

### SEO

- **REQ-10**: O sistema DEVE incluir `<title>`, `<meta name="description">` e
  tags Open Graph (`og:title`, `og:description`, `og:type`, `og:url`) no
  `<head>`, com conteúdo em pt-BR mencionando "TapLeva".
- **REQ-11**: O sistema DEVE incluir `<html lang="pt-BR">` e uma
  `<meta name="viewport">` para responsividade mobile.

### Isolamento de infraestrutura

- **REQ-12**: O sistema DEVE rodar em um Cloudflare Worker dedicado
  (`tapleva-lp`), com seu próprio `wrangler.lp.jsonc`, servindo
  `tapleva.com.br` e `www.tapleva.com.br` via `custom_domain`.
- **REQ-13**: O worker `tapleva-lp` NÃO DEVE importar código dos workers
  `go` (redirect) ou `admin` (backoffice) que crie acoplamento a D1,
  serviços de domínio (Customer/Target/Device) ou sessão administrativa.
- **REQ-14**: O worker `tapleva-lp` NÃO DEVE declarar binding de D1 nem
  qualquer binding além de `vars` necessários (ex: `WHATSAPP_NUMBER`).
- **REQ-15**: O sistema DEVE expor `yarn dev:lp` e `yarn deploy:lp` em
  `package.json`, seguindo o padrão de `dev:admin`/`deploy:admin`.

## Critérios de aceite (resumo para QA manual)

1. Acessar `/` no worker `tapleva-lp` (via `wrangler dev`) mostra a LP
   completa, sem erros de console.
2. Preencher nome+telefone e submeter o form abre (ou navega para) um link
   `wa.me` com os dados corretos codificados na query `text`.
3. Deixar nome ou telefone vazio bloqueia a submissão (validação nativa do
   browser).
4. Paleta de cores bate visualmente com a placa de referência
   (`ex-toten.png`): fundo branco, texto verde-escuro, destaque dourado.
5. `yarn typecheck` e `yarn test` passam sem quebrar nada nos workers
   existentes.
6. Nenhum arquivo de `go`/`admin` foi alterado.

## Referências

- `ARCHITECTURE.md` §3, §6, §33, §22A (isolamento de runtime, stack aprovada).
- `src/views/html.ts` (padrão de renderização HTML server-side existente).
- `ex-toten.png` (identidade visual de referência).


### Doc: .specs/features/landing-page-institucional/requirements.md
# Landing Page Institucional TapLeva — Tabela de Requisitos

**Spec:** `spec.md`
**Design:** `design.md`
**Tasks:** `tasks.md`
**Status:** Rascunho
**Created:** 2026-09-19

> Cada linha é independente e pode ser avaliada sozinha, sem consultar outra
> linha ou o código. **SP** = caminho de sucesso, **EP** = caminho de erro.

---

## 1. Renderização da página

| Requisito | Cenário                          | Expressão                                                                                                                                                   | Complemento                                                                                                          | Caminho |
| --------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ------- |
| FR-001    | Acesso à página inicial            | **Dado** um visitante acessa a página inicial do site, **Então** o servidor responde com sucesso (HTTP 200) e devolve uma página HTML única contendo todas as seções (Hero, Como funciona, Casos de uso, Diferencial, Formulário, Rodapé). | A página é single-page: tudo que o visitante precisa está em uma única tela navegável, sem páginas internas separadas.    | SP      |
| FR-002    | Tecnologia de renderização         | **Dado** o HTML da página é gerado, **Então** ele é montado no servidor sem uso de nenhum framework de frontend (React, Next.js ou equivalente).               | O projeto proíbe frameworks de frontend para manter a stack pequena e sem runtime extra a manter.                        | SP      |
| FR-003    | Identidade visual                  | **Dado** a página é exibida, **Então** o fundo é branco, títulos e textos usam verde-escuro quase preto, e elementos de destaque (botões, ícones, bordas) usam dourado. | A identidade replica a das placas físicas NFC/QR da marca, para reforçar reconhecimento visual entre quem já viu uma placa. | SP      |
| FR-004    | Tipografia                          | **Dado** a página é exibida, **Então** os textos usam uma fonte arredondada e de peso forte (bold), carregada de uma fonte web pública. | Mantém a mesma sensação visual "robusta e amigável" da tipografia usada nas placas.                                       | SP      |
| FR-005    | Ícone decorativo                    | **Dado** a página é exibida, **Então** um ícone de raio decorativo aparece perto da marca "TapLeva", desenhado diretamente no código da página (sem depender de um arquivo de imagem externo). | Não existe hoje um arquivo de logo isolado da marca — apenas a foto de uma placa impressa — então o ícone é recriado, não recortado de uma imagem. | SP      |
| FR-006    | Escape de conteúdo dinâmico          | **Dado** qualquer valor de configuração é inserido no HTML da página (por exemplo, o número de WhatsApp), **Então** esse valor passa por um processo de escape antes de aparecer na página. | Evita que um valor de configuração mal formatado quebre a estrutura da página ou introduza código não intencional, mesmo vindo de uma fonte confiável. | SP      |

---

## 2. Formulário de contato e redirecionamento para WhatsApp

| Requisito | Cenário                                   | Expressão                                                                                                                                                       | Complemento                                                                                                                     | Caminho |
| --------- | ------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | ------- |
| FR-007    | Campos do formulário                         | **Dado** a seção de contato é exibida, **Então** ela mostra os campos Nome, Telefone e Mensagem, sendo Mensagem o único opcional.                                       | Nome e telefone são o mínimo necessário para alguém do time comercial identificar e responder o contato pelo WhatsApp.               | SP      |
| FR-008    | Bloqueio de envio incompleto                  | **Dado** o visitante tenta enviar o formulário, **Quando** o campo Nome ou o campo Telefone está vazio, **Então** o envio é bloqueado pelo próprio navegador, sem precisar de código adicional de validação. | Evita contatos inúteis (sem nome ou telefone) chegando ao WhatsApp, usando um recurso já nativo do navegador.                        | EP      |
| FR-009    | Envio bem-sucedido                            | **Dado** o visitante preenche Nome e Telefone (Mensagem é opcional), **Quando** ele envia o formulário, **Então** o navegador monta um link do WhatsApp com esses dados e navega automaticamente para ele — sem nenhuma chamada para um servidor próprio. | Não existe backend para o formulário: tudo acontece no navegador do visitante, o que elimina a necessidade de banco de dados para leads. | SP      |
| FR-010    | Mensagem padrão                                | **Dado** o visitante envia o formulário sem preencher o campo Mensagem, **Então** o link do WhatsApp inclui uma mensagem padrão fixa perguntando sobre as placas, além do nome e telefone informados. | Garante que mesmo um contato mínimo (só nome e telefone) chegue ao WhatsApp com contexto suficiente para o time responder.           | SP      |
| FR-011    | Número de destino configurável                 | **Dado** o link do WhatsApp é montado, **Então** o número de destino vem de uma configuração do ambiente de publicação, e não de um valor fixo espalhado pelo código. | Permite t
[truncado]

### Commits
- chore(lp): add wrangler config for tapleva-lp worker
- feat(lp): bootstrap tapleva-lp worker with minimal route
- feat(lp): add landing page stylesheet with TapLeva palette
- feat(lp): add hero, footer and SEO head to landing page
- feat(lp): add how-it-works, use cases and differentiator sections
- feat(lp): add whatsapp contact form with client-side redirect
- chore(lp): add dev and deploy scripts for tapleva-lp
- feat(lp): implement institutional landing page with structured tasks …
- feat(lp): update NFC target rendering with improved SVG and description
- feat(lp): update WhatsApp number handling to be optional and improve …
- feat(lp): add deployment step for LP Worker in production workflow

### Arquivos
- source: 7
- tests: 2
- docs: 10
- generated: 1
  - .github/workflows/deploy-production.yml
  - .gitignore
  - package.json
  - src/app/lp.ts
  - src/assets/lp-css.ts
  - src/views/lp.ts
  - wrangler.lp.jsonc
  - tests/helpers/landing-browser.ts
  - tests/lp.test.ts

# dump.md — execução real da skill

Duas conversas reais com o Claude Code em 29/10/2026, no repositório do meu projeto pessoal (backoffice de placas com QR/NFC).

1. **Uso:** um único prompt, PR 22 anunciado no WhatsApp com vídeo.
2. **Teste do gate:** uma frase inventada plantada no anúncio do PR 10, para provar que a checagem de citações reprova.

Saídas de comandos abreviadas com `…`. Nada foi editado além dos cortes.

---

## 1. Uso: "anuncia o PR 22 no WhatsApp com vídeo"

**Usuário:**

> anuncia o PR 22 no WhatsApp com vídeo

**Claude** carrega a skill `feature-announcement-writer` (args: `PR 22, canal WhatsApp, com vídeo`).

### Fonte

```
$ python3 $S/scripts/fetch_pr_context.py 22 > pack.md
exit=0
   15059 pack.md
```

O pacote tem a descrição do PR (vazia), `spec.md` e `requirements.md` adicionados no PR, 24 títulos de commit e a contagem de arquivos. Um PR de +7.001 linhas virou 15 mil caracteres de fonte, sem o diff.

```
## PR #22: Feat/criacao devices em lote
URL: https://github.com/BrunoSaade/tapleva/pull/22 | +7001/-107

### Descrição do PR
(vazia)

### Doc: .specs/features/criacao-devices-em-lote/spec.md
…
Canva. Com 45 placas isso vira 45 formulários + 45+ downloads + 45+ colagens
manuais — lento e sujeito a trocar QR de placa.
…
```

### Evidence gate (citações + lint)

```
$ python3 $S/scripts/check_citations.py pack.md draft.md --out message.md
ok
no claim: 🚀 *Criação de dispositivos em lote no backoffice*
no claim: ✨ *O que mudou?*
no claim: 🎯 *Benefícios da melhoria*
no claim: Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌
--- lint
$ python3 $S/scripts/lint_announcement.py message.md --channel whatsapp
ok
```

As 22 citações do rascunho foram encontradas literalmente no pacote. Só título, seções e fechamento ficaram sem fonte, e o script lista essas linhas para conferência humana.

> **Observação honesta:** nesta execução o agente reaproveitou o rascunho citado do exemplo da própria skill (`assets/examples/pr-22/draft.md`) em vez de reescrever do zero, porque o PR é o mesmo. A checagem rodou contra o pacote baixado **agora**, então as citações valem para o PR atual. O rascunho original foi escrito na conversa de desenvolvimento, que é de onde vem o teste da seção 2.

**Claude:** Texto pronto e validado (citações + lint WhatsApp ok). Agora gravando vídeo: subindo backoffice local e chamando skill `demo`.

### Vídeo (skill `demo` da Tech Leads Club)

Claude carrega a skill `demo` com o fluxo: *criar lote de 5 dispositivos e baixar ZIP dos QR codes*.

**Claude:** Já existe demo `pr-22-device-batch-create`. Reusando.

O script da demo entra com uma senha só local; a senha real nunca é lida:

```js
// Local-only password: start the admin worker with `yarn dev:admin --var ADMIN_PASSWORD:demo-local-only`.
await page.locator('input[name="password"]').fill('demo-local-only')
…
await record()
await humanClick(page, page.getByRole('link', { name: 'Criar lote' }).first())
await type(page, page.getByLabel('Prefixo do nome'), 'Chaveiro Demo')
await type(page, page.getByLabel('Quantidade'), '5')
…
await humanClick(page, page.getByRole('button', { name: 'Baixar ZIP' }))
```

Os hooks do meu ambiente bloquearam o servidor de dev fora de tmux/screen (sem tmux instalado). O agente usou `screen`:

**Claude:** Hook bloqueia dev server fora de tmux/screen; tentando `screen`.

```
$ PORT=8787 ~/.claude/skills/demo/scripts/record pr-22-device-batch-create
…
video:  …/.demos/pr-22-device-batch-create/video.mp4
events: …/.demos/pr-22-device-batch-create/events.json

$ jq -c '.events[] | [.t,.type]' events.json
[1.411,"click"] [3.583,"click"] [4.891,"type"] … [10.911,"click"] [12.846,"hover"] [14.554,"click"]
19.233333
```

O agente extraiu 5 frames com `ffmpeg` e olhou cada um antes de entregar.

**Claude:** Vídeo ok: formulário → lote criado com 5 dispositivos em estoque → clique em Baixar ZIP. Limpando: paro o servidor e apago os arquivos temporários.

### Resposta final

**Claude:** Anúncio do PR 22 pronto pra colar no WhatsApp, com vídeo.

```
🚀 *Criação de dispositivos em lote no backoffice*

Pessoal, disponibilizamos a criação de dispositivos em lote. Preparar as placas antes da venda deixa de exigir um formulário, um download e uma colagem por placa.

🎥 Vídeo em anexo: criação de um lote de 5 dispositivos e download do ZIP com os QR codes.

✨ *O que mudou?*

📝 Em um único formulário, o operador cria até *100 dispositivos* de uma vez, já em estoque e sem cliente associado:
- nomes gerados automaticamente a partir de um prefixo com numeração (ex.: Placa 001, Placa 002…)
- mesma quantidade de links (de 1 a 4) para todos os dispositivos do lote
- código do lote sugerido com a data do dia, editável e sem repetição

📦 Na página do lote, um clique baixa um *arquivo ZIP com todos os QR codes* e uma *planilha CSV* que relaciona cada imagem à sua placa. O download pode ser repetido a qualquer momento.

🔎 Cada imagem do ZIP já traz no nome a sequência, a posição e o código do dispositivo.

🚫 Dispositivos excluídos e links desativados ficam fora do ZIP e da planilha.

🔎 A lista de dispositivos ganhou filtro por lote, e cada dispositivo mostra o lote de origem.

🛡️ A criação do lote fica registrada na auditoria, e a planilha é protegida contra conteúdo que seria interpretado como fórmula.

🧪 Foram adicionados testes automatizados para criação, download e planilha do lote.

🎯 *Benefícios da melhoria*
- Um lote de 45 placas sai com 1 formulário e 1 download, em vez de 45 de cada.
- Menos risco de trocar o QR code de uma placa.

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌
```

🎥 **Vídeo pra anexar:** `.demos/pr-22-device-batch-create/video.mp4` (19s, já te mandei). Gravei de novo agora, no backoffice local, e conferi os frames: formulário preenchido → lote criado com 5 dispositivos em estoque → clique em "Baixar ZIP".

🔍 **Fontes:** todas as frases citam um trecho literal do `spec.md`, do `requirements.md` ou dos commits do PR. A checagem de citações e o lint de WhatsApp passaram.

⚠️ **Revisar antes de enviar:**
- A descrição do PR está vazia, então o texto saiu da spec e dos commits.
- Os benefícios ("45 placas, 1 formulário") vêm dos objetivos da spec, não de uma medição real.
- Confirme se o PR 22 já está em produção antes de dizer "disponibilizamos".

### Pergunta sobre o deploy

O agente não assumiu que "mergeado" significa "no ar" e perguntou:

> O anúncio abre com "Pessoal, disponibilizamos…", o que diz que a funcionalidade já está no ar. O pacote do PR só mostra que ele foi mergeado na main (commit 6395a3b), não se o backoffice admin foi publicado nem se a migration nova `drizzle/0010_…sql` (tabela device_batches) foi aplicada no D1 de produção. Sem essa tabela, a tela de lote quebraria em produção. Como o PR 22 está hoje?
>
> - Já está em produção
> - Mergeado, sem deploy
> - Não sei / vou checar

**Usuário:** Já está em produção.

**Claude:** O texto fica como está: o PR 22 já está em produção, então o "disponibilizamos" vale. Pode enviar no WhatsApp a mensagem acima com o vídeo `.demos/pr-22-device-batch-create/video.mp4` em anexo.

---

## 2. Teste do gate: frase inventada no PR 10

Na conversa em que construí a v3, plantei no rascunho do PR 10 (leitura de QR code) uma frase plausível e sem fonte nenhuma:

```
⚡ A identificação ficou 3x mais rápida que a busca manual [10].
…
---fontes---
[10] "identificação 3x mais rápida que a busca manual"
```

```
$ python3 scripts/check_citations.py pack.md draft.md --out message.md
[10] quote not found in pack: "identificação 3x mais rápida que a busca manual"
exit=1
```

Sem a linha plantada:

```
$ python3 scripts/check_citations.py pack.md draft.md --out message.md
ok
no claim: 🚀 *Busca de dispositivos por leitura de QR code no backoffice*
no claim: ✨ *O que mudou?*
no claim: 🎯 *Benefícios da melhoria*
no claim: Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌
exit=0
$ python3 scripts/lint_announcement.py message.md --channel whatsapp
ok
```

Comparado ao anúncio da v2 do mesmo PR, a citação obrigatória derrubou três trechos que ninguém conseguia citar:

```diff
-Pessoal, disponibilizamos uma melhoria no backoffice para agilizar a identificação de dispositivos físicos: …
+Pessoal, disponibilizamos uma melhoria no backoffice para identificar dispositivos físicos: …
-🧪 Foram adicionados testes automatizados para a leitura do QR code e para as novas rotas da tela.
+🧪 Foram adicionados testes automatizados para a leitura do QR code.
-- Menos erros de digitação na busca manual.
```

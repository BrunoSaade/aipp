# feature-announcement-writer

Transforma um ou mais PRs do GitHub em um anúncio pronto para colar no chat do time (Slack, WhatsApp, Google Chat ou Teams), em pt-BR. Cada linha carrega uma citação literal do PR, conferida por script, e o anúncio pode sair com um vídeo da feature gravado na hora.

## Problema

Toda feature entregue precisa ser comunicada para dev, QA, produto e, às vezes, suporte e cliente. Escrever isso à mão toda semana toma tempo e sai inconsistente. Quando um LLM escreve, sai rápido, mas inventa benefícios, cita arquivos, mistura inglês e quebra a formatação do canal.

## Como usar

Requisitos: `gh` autenticado e `python3` (os scripts usam só a biblioteca padrão). O vídeo, opcional, tem requisitos próprios (abaixo).

Instalação: copie `skill/` para `~/.claude/skills/feature-announcement-writer/`.

Prompts de exemplo:

```
Gera o anúncio do PR #10 do org/app para o WhatsApp.
Anuncia os PRs 22 e 13 para os stakeholders no Slack.
Escreve o changelog pro cliente a partir de https://github.com/org/app/pull/10
Anuncia o PR 22 no WhatsApp com vídeo.
```

O que a skill faz:

1. `scripts/fetch_pr_context.py` monta um pacote de evidências: descrição do PR, PRD/spec/requirements adicionados no PR, títulos dos commits e contagem de arquivos (código, testes, docs, gerados). Nunca baixa o diff inteiro.
2. Escreve a mensagem para o canal e a audiência pedidos (`squad`, `stakeholders`, `suporte` ou `changelog`).
3. **Citação verificável:** o rascunho marca cada linha com `[n]` e lista, no fim, o trecho literal da fonte que a sustenta. `scripts/check_citations.py` confere que cada trecho existe mesmo no pacote e reprova linha sem citação. O que é inferência vai para `⚠️ Revisar antes de enviar`, fora da mensagem.
4. `scripts/lint_announcement.py --channel <canal>` reprova caminho de arquivo, link ou chave do Jira, frase em inglês, formatação errada para o canal e tamanho. A skill só entrega depois do `ok` dos dois scripts.
5. **Vídeo (se pedido):** grava o fluxo da feature e anexa ao anúncio. Detalhes abaixo.

A skill não envia nada: entrega o texto (e o caminho do vídeo) para tu revisar e colar no canal.

### Vídeo da feature (opcional)

Basta pedir "com vídeo" no prompt. Serve para PRs que mudam uma tela.

Requisitos extras:
- skill `demo` do catálogo da Tech Leads Club: `npx @tech-leads-club/agent-skills install -s demo`
- Docker rodando (a `demo` grava num desktop Linux real dentro de um container) e `ffmpeg` no host (para conferir os frames)
- o app rodando localmente e um jeito de fazer login de teste

Como funciona:
1. O fluxo do vídeo sai das mesmas citações do anúncio (história de usuário do PRD, commit principal). O vídeo mostra o que foi entregue e não acrescenta nenhuma afirmação.
2. A skill `demo` escreve o roteiro em `.demos/pr-<n>-<fluxo>/script.mjs`, grava `video.mp4` e o agente confere 3 a 4 frames antes de entregar.
3. O anúncio ganha a linha `🎥 Vídeo em anexo: <fluxo>`, citada como qualquer outra, e a resposta traz o caminho do `video.mp4` para anexar no envio.
4. Se o login exige segredo, o app sobe com uma senha só local (ex.: `wrangler dev --var ADMIN_PASSWORD:demo-local-only`). A senha real nunca é lida nem vai para o roteiro.
5. Se a gravação falhar (app fora do ar, sem Docker), o anúncio sai sem a linha do vídeo e a skill diz o motivo.

### Testes

Com `pytest` instalado:

```
python3 -m pytest skill/scripts
```

42 testes cobrindo os 3 scripts (`fetch_pr_context.py`, `check_citations.py`, `lint_announcement.py`).

### Exemplos

Exemplos reais em `skill/assets/examples/`: saídas de PRs de um projeto pessoal (TapLeva, backoffice de placas com QR/NFC); os textos não citam o produto, o vídeo mostra o app real. A skill não depende de nenhum projeto específico; os padrões de arquivo (docs, testes, gerados) são agnósticos de stack.

## Como evoluiu

**v1 (julho/2026):** um `SKILL.md` de 227 linhas. Era basicamente um prompt: a pessoa colava a descrição do PR e recebia o anúncio em markdown com `**negrito**`.

O que testei e o que mudou:

| Teste | O que falhou | Mudança |
|---|---|---|
| Rodei a skill em 3 PRs reais meus | **Os 3 estavam com a descrição vazia.** A v1 não tinha de onde tirar conteúdo. | `fetch_pr_context.py`: usa como fonte a descrição, depois os docs de spec do PR, depois os commits e, por fim, os arquivos. O PR maior tem 24 commits e +7 mil linhas, e mesmo assim o pacote fica em ~15 mil caracteres. |
| Reli o exemplo da própria v1 | A entrada não fala de testes, mas a saída dizia "Foram adicionados testes automatizados" e "Facilita auditorias". **O exemplo ensinava a alucinar.** | Regra: testes só quando o PR tem arquivos de teste. Exemplo trocado por saídas reais com `sources.md`. |
| Escrevendo os exemplos novos | O próprio agente escreveu "identificação em segundos" e "squad de produto", sem fonte nenhuma. | Evidence gate: mapa afirmação → fonte e a lista `⚠️ Revisar`. Limite documentado: o lint não pega fato inventado, só o gate pega. |
| Pesquisei a doc oficial dos 4 canais | Nenhum documenta `**negrito**`. A v1 gerava formatação quebrada em todos. | `--channel` no lint e `references/channels.md`. |
| Colei a mensagem no WhatsApp e no Slack (print do WhatsApp em `skill/assets/whats_evidence.png`) | WhatsApp ✅. **Slack ❌**: texto colado no Slack fica puro, e `*negrito*` aparece com os asteriscos. | Slack sai sem nenhum marcador, só com emojis e quebras de linha. O lint reprova `*` no canal slack. |
| Revisão por um agente especialista em skills | Caminho relativo dos scripts quebrava fora da pasta da skill; um PR inválido abortava o lote inteiro; nomes inconsistentes. | Caminhos a partir da pasta da skill, erro por PR sem derrubar o lote, nomes alinhados. |

**v2 → v3 (outubro/2026):** duas lacunas que a própria v2 admitia.

| Teste | O que falhou | Mudança |
|---|---|---|
| O `SKILL.md` da v2 dizia: "o lint não pega fato inventado" | A verificação mais importante ainda era confiar no modelo. | `check_citations.py`: cada linha cita um trecho literal (≥ 15 caracteres) e o script procura esse trecho no pacote. Plantei "a identificação ficou 3x mais rápida" no PR 10: **reprovado** (`[10] quote not found in pack`). |
| Refiz o anúncio do PR 10 com a citação obrigatória | Três trechos da v2 não tinham fonte literal: "agilizar", "testes das novas rotas", "menos erros de digitação". | Saíram do anúncio. O que ninguém consegue citar não vai pra mensagem. |
| Anúncio de tela nova só em texto | QA e produto ainda precisavam abrir o app para entender o fluxo. | Passo opcional de vídeo com a skill `demo` da TLC: o fluxo vem das próprias citações, então o vídeo não inventa nada. Gravado no PR 22: lote de 5 dispositivos criado e ZIP baixado em 19 s. |
| Login do app de exemplo exige uma senha secreta | Ler o arquivo de segredos ou deixar a senha no script do vídeo vazaria a credencial. | Sobe o app com uma senha só local (`wrangler dev --var ADMIN_PASSWORD:demo-local-only`); o script nunca vê a real. |

**Hoje:** `SKILL.md` com 91 linhas, mais 2 referências e 3 scripts com 42 testes (escritos antes do código).

**Relação com a TLC:** é uma skill nova. O passo de vídeo usa a skill `demo` do catálogo da TLC como está, sem modificá-la.

## Demo

Vídeo gravado pela própria skill a partir do prompt "anuncia o PR 22 no WhatsApp com vídeo" (19 s: cria um lote de 5 dispositivos e baixa o ZIP de QR codes): [`skill/assets/examples/pr-22/video.mp4`](skill/assets/examples/pr-22/video.mp4).

Anúncio que acompanha o vídeo: [`skill/assets/examples/pr-22/announcement.md`](skill/assets/examples/pr-22/announcement.md). Conversa completa dessa execução, mais o teste da frase inventada: [`dump.md`](dump.md).

## Conteúdo do pacote

```
bruno-saade.zip
├── skill/
│   ├── SKILL.md
│   ├── references/   audiences.md, channels.md
│   ├── scripts/      fetch_pr_context.py, check_citations.py, lint_announcement.py + testes
│   └── assets/       examples/ (PRs 10, 13 e 22, com o vídeo) e print do WhatsApp
├── README.md
└── dump.md
```

# feature-announcement-writer

Transforma um ou mais PRs do GitHub em um anúncio pronto para colar no chat do time (Slack, WhatsApp, Google Chat ou Teams), em pt-BR, com cada afirmação rastreável até o PR.

## Problema

Toda feature entregue precisa ser comunicada para dev, QA, produto e, às vezes, suporte e cliente. Escrever isso à mão toda semana toma tempo e sai inconsistente. Quando um LLM escreve, sai rápido, mas inventa benefícios, cita arquivos, mistura inglês e quebra a formatação do canal.

## Como usar

Requisitos: `gh` autenticado e `python3` (os scripts usam só a biblioteca padrão).

Instalação: copie `skill/` para `~/.claude/skills/feature-announcement-writer/`.

Prompts de exemplo:

```
Gera o anúncio do PR #10 do org/app para o WhatsApp.
Anuncia os PRs 22 e 13 para os stakeholders no Slack.
Escreve o changelog pro cliente a partir de https://github.com/org/app/pull/10
```

O que a skill faz:

1. `scripts/fetch_pr_context.py` monta um pacote de evidências: descrição do PR, PRD/spec/requirements adicionados no PR, títulos dos commits e contagem de arquivos (código, testes, docs, gerados). Nunca baixa o diff inteiro.
2. Escreve a mensagem para o canal e a audiência pedidos (`squad`, `stakeholders`, `suporte` ou `changelog`).
3. **Evidence gate:** cada frase precisa ter fonte. O que é inferência vai para uma lista `⚠️ Revisar antes de enviar`, fora da mensagem.
4. `scripts/lint_announcement.py --channel <canal>` reprova caminho de arquivo, link ou chave do Jira, frase em inglês, formatação errada para o canal e tamanho. A skill só entrega depois do `ok`.

Exemplos reais em `skill/assets/examples/`: saídas de PRs de um projeto pessoal, com o nome do produto anonimizado. A skill não depende de nenhum projeto específico; os padrões de arquivo (docs, testes, gerados) são agnósticos de stack.

## Como evoluiu

**v1 (julho/2026):** um `SKILL.md` de 227 linhas. Era basicamente um prompt: a pessoa colava a descrição do PR e recebia o anúncio em markdown com `**negrito**`.

O que testei e o que mudou:

| Teste | O que falhou | Mudança |
|---|---|---|
| Rodei a skill em 3 PRs reais meus | **Os 3 estavam com a descrição vazia.** A v1 não tinha de onde tirar conteúdo. | `fetch_pr_context.py`: usa como fonte a descrição, depois os docs de spec do PR, depois os commits e, por fim, os arquivos. O PR maior tem 24 commits e +7 mil linhas, e mesmo assim o pacote fica em ~15 mil caracteres. |
| Reli o exemplo da própria v1 | A entrada não fala de testes, mas a saída dizia "Foram adicionados testes automatizados" e "Facilita auditorias". **O exemplo ensinava a alucinar.** | Regra: testes só quando o PR tem arquivos de teste. Exemplo trocado por saídas reais com `sources.md`. |
| Escrevendo os exemplos novos | O próprio agente escreveu "identificação em segundos" e "squad de produto", sem fonte nenhuma. | Evidence gate: mapa afirmação → fonte e a lista `⚠️ Revisar`. Limite documentado: o lint não pega fato inventado, só o gate pega. |
| Pesquisei a doc oficial dos 4 canais | Nenhum documenta `**negrito**`. A v1 gerava formatação quebrada em todos. | `--channel` no lint e `references/channels.md`. |
| Colei a mensagem no WhatsApp e no Slack (prints em `skill/assets/`) | WhatsApp ✅. **Slack ❌**: texto colado no Slack fica puro, e `*negrito*` aparece com os asteriscos. | Slack sai sem nenhum marcador, só com emojis e quebras de linha. O lint reprova `*` no canal slack. |
| Revisão por um agente especialista em skills | Caminho relativo dos scripts quebrava fora da pasta da skill; um PR inválido abortava o lote inteiro; nomes inconsistentes. | Caminhos a partir da pasta da skill, erro por PR sem derrubar o lote, nomes alinhados. |

**Hoje:** `SKILL.md` com 80 linhas, mais 2 referências e 2 scripts com 32 testes (escritos antes do código).

## Demo

_(link do vídeo curto aqui)_

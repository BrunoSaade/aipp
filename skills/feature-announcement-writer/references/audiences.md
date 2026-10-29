# Audiences

Default audience: `squad`. When the user asks for more than one, produce one message per audience from the **same** source pack and evidence map; never add facts for one audience that the source does not back.

| Audience | Reader wants | Keep | Drop | Closing |
|---|---|---|---|---|
| `squad` (dev, QA, product) | What changed and what to watch when testing | Behavior, constraints, unchanged flows, tests added, operational caveats (HTTPS, browser support) | File paths, commands | Report issues in the squad channel 🙌 |
| `stakeholders` (business, leadership) | Why it matters | Problem solved, user/operational benefit, scope limits in one line | Tests, technical caveats, implementation | Who to contact for questions |
| `suporte` (support, CS, ops) | How to recognize and explain it | Where it is in the product, step-by-step usage, what is *not* possible yet, 2–3 Q&A pairs (`❓ Pergunta` / `💡 Resposta`) | Tests, benefits pitch | Where to escalate problems |
| `changelog` (end users) | What they can do now | One-line headline + 2–4 bullets in second person ("Agora você pode…") | Internal names, team jargon, tests, caveats about internal infra | None |

Length guide: `stakeholders` and `changelog` ≤ ~800 characters; `squad` and `suporte` ≤ ~3000.

Same source, different emphasis. Example (PR adding CSV export of orders):
- `squad`: "a exportação respeita o filtro de período já aplicado na lista; pedidos cancelados ficam de fora"
- `stakeholders`: "o time financeiro passa a fechar o mês sem copiar pedidos à mão"
- `suporte`: "❓ Por que um pedido não aparece na planilha? 💡 Pedidos cancelados não são exportados."
- `changelog`: "Agora você pode baixar seus pedidos do período em uma planilha."

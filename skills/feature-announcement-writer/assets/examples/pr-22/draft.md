🔍 **Fontes**
- Até 100 dispositivos, em estoque, sem cliente → spec (Goals; Assumptions "Limite do lote"; Problem Statement) + commit `feat(services): create device batches`
- Nome por prefixo + numeração, 1–4 links, código sugerido/único → spec (Assumptions) + commits `add device batch naming helpers`, `reject reserved device batch code`
- ZIP + CSV, re-download, uso manual no Canva/NFC → spec (Goals, Out of Scope) + commits `in-browser batch zip download script`, `build device batch manifest`
- Nome do arquivo identifica sequência/posição/código → spec (Goals)
- Excluídos/inativos fora do ZIP → spec (Assumptions "Exclusões do ZIP")
- Filtro por lote, dispositivo mostra lote → commits `filter device list by batch`, `link devices to their batch`
- Auditoria, proteção contra fórmula → spec (Assumptions "Auditoria") + commits `batch audit action`, `csv writer with formula guard`
- Testes → 11 arquivos de teste no PR
- 45 placas → spec (Problem Statement)

⚠️ **Revisar antes de enviar**
- requirements.md está com status *Draft*; confirmar que o comportamento final não mudou.
- Limite de 60 caracteres do prefixo e formato do código ainda marcados como não confirmados na spec: deixados fora do anúncio.

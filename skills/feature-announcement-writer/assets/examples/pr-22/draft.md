🚀 *Criação de dispositivos em lote no backoffice* [—]

Pessoal, disponibilizamos a criação de dispositivos em lote. Preparar as placas antes da venda deixa de exigir um formulário, um download e uma colagem por placa [1].

🎥 Vídeo em anexo: criação de um lote de 5 dispositivos e download do ZIP com os QR codes [2][3].

✨ *O que mudou?* [—]

📝 Em um único formulário, o operador cria até *100 dispositivos* de uma vez, já em estoque e sem cliente associado [4][5]:
- nomes gerados automaticamente a partir de um prefixo com numeração (ex.: Placa 001, Placa 002…) [6]
- mesma quantidade de links (de 1 a 4) para todos os dispositivos do lote [7]
- código do lote sugerido com a data do dia, editável e sem repetição [8][9]

📦 Na página do lote, um clique baixa um *arquivo ZIP com todos os QR codes* e uma *planilha CSV* que relaciona cada imagem à sua placa [10]. O download pode ser repetido a qualquer momento [11].

🔎 Cada imagem do ZIP já traz no nome a sequência, a posição e o código do dispositivo [12].

🚫 Dispositivos excluídos e links desativados ficam fora do ZIP e da planilha [13].

🔎 A lista de dispositivos ganhou filtro por lote, e cada dispositivo mostra o lote de origem [14][15].

🛡️ A criação do lote fica registrada na auditoria, e a planilha é protegida contra conteúdo que seria interpretado como fórmula [16][17].

🧪 Foram adicionados testes automatizados para criação, download e planilha do lote [18][19][20].

🎯 *Benefícios da melhoria* [—]
- Um lote de 45 placas sai com 1 formulário e 1 download, em vez de 45 de cada [1][21].
- Menos risco de trocar o QR code de uma placa [22].

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌 [—]
---fontes---
[1] "Com 45 placas isso vira 45 formulários + 45+ downloads + 45+ colagens"
[2] "Operador cria 45 Devices em inventory com 1 formulário e 1 submissão"
[3] "Operador obtém todos os QR PNGs do lote num único `.zip` com 1 clique"
[4] "Limite do lote | 1..100 Devices"
[5] "A criação de Devices em `inventory` sem Customer/Target já é o fluxo esperado"
[6] "Nome dos Devices | `{prefixo} {NNN}`, NNN com 3 dígitos"
[7] "Links por Device | 1 valor 1..4 para o lote inteiro"
[8] "Sugerido `LOTE-AAAAMMDD-NN` (data em America/Sao_Paulo, NN = menor sequencial livre do dia), editável"
[9] "Código nunca é reutilizado"
[10] "ZIP com PNG por link ativo + `manifest.csv`"
[11] "Página do lote regenera o ZIP a qualquer momento"
[12] "nome traz sequência, posição e `publicCode`"
[13] "Devices com `deleted_at` e links com `active = false` ficam fora"
[14] "feat(backoffice): filter device list by batch"
[15] "feat(backoffice): link devices to their batch"
[16] "feat(db): add device_batches table and batch audit action"
[17] "feat(lib): add csv writer with formula guard"
[18] "test(repositories): assert persisted batch rows and query budget"
[19] "test(backoffice): pin batch download concurrency and retry"
[20] "test(lib): cover every csv formula guard trigger"
[21] "Operador cria 45 Devices em inventory com 1 formulário e 1 submissão"
[22] "lento e sujeito a trocar QR de placa"

🚀 *Criação de dispositivos em lote no backoffice*

Pessoal, disponibilizamos a criação de dispositivos em lote. Preparar as placas antes da venda deixa de exigir um formulário, um download e uma colagem por placa.

✨ *O que mudou?*

📝 Em um único formulário, o operador cria até *100 dispositivos* de uma vez, já em estoque e sem cliente associado:
- nomes gerados automaticamente a partir de um prefixo com numeração (ex.: Placa 001, Placa 002…)
- mesma quantidade de links (de 1 a 4) para todos os dispositivos do lote
- código do lote sugerido com a data do dia, editável e sem repetição

📦 Na página do lote, um clique baixa um *arquivo ZIP com todos os QR codes* e uma *planilha CSV* que relaciona cada imagem à sua placa, pronta para uso manual no Canva e na gravação de NFC. O download pode ser repetido a qualquer momento.

🔎 Cada imagem do ZIP já traz no nome a sequência, a posição e o código do dispositivo, sem precisar abrir o arquivo.

🚫 Dispositivos excluídos e links desativados ficam fora do ZIP e da planilha, então placa inativa não é reimpressa.

🔎 A lista de dispositivos ganhou filtro por lote, e cada dispositivo mostra o lote de origem.

🛡️ A criação do lote fica registrada na auditoria, e a planilha é protegida contra conteúdo que seria interpretado como fórmula.

🧪 Foram adicionados testes automatizados para criação, download, planilha e regras de validação do lote.

🎯 *Benefícios da melhoria*
- Um lote de 45 placas sai com 1 formulário e 1 download, em vez de 45 de cada.
- Menos risco de trocar o QR code de uma placa.
- Planilha pronta para os fluxos de impressão e NFC.

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌

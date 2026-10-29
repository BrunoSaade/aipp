🚀 *Busca de dispositivos por leitura de QR code no backoffice* [—]

Pessoal, disponibilizamos uma melhoria no backoffice para identificar dispositivos físicos: agora basta apontar a câmera para o QR code impresso no dispositivo [1].

✨ *O que mudou?* [—]

📷 Nova tela *Escanear QR*, acessível por um botão na lista de dispositivos [2]. A câmera lê o QR code e abre direto a página de detalhe do dispositivo, sem precisar digitar nada [3].

⌨️ Sem câmera disponível (permissão negada ou indisponível)? Na mesma tela dá para digitar o código do dispositivo [4]:
- 1 resultado: abre direto o dispositivo [5]
- vários resultados: mostra a lista para escolher [6]
- nenhum resultado: exibe mensagem para tentar de novo [7]

💬 QR code inválido ou dispositivo não encontrado mostram uma mensagem na própria tela, e a câmera continua ativa para uma nova tentativa, sem recarregar a página [8].

🔄 O QR code impresso nos dispositivos continua o mesmo: nada precisa ser reimpresso [9].

🧪 Foram adicionados testes automatizados para a leitura do QR code [11].

🎯 *Benefícios da melhoria* [—]
- Identificação do dispositivo direto pela câmera, com ele em mãos [12].
- Alternativa manual garantida quando a câmera não estiver disponível [4].

⚠️ A câmera só funciona em conexão segura (HTTPS) e a leitura nativa é mais completa no Chrome e no Edge [13][14].

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌 [—]
---fontes---
[1] "le o QR ja impresso no device, decodifica a URL, identifica o device e abre a pagina de detalhe"
[2] "botao "Escanear QR" na lista `/devices`"
[3] "redirect direto pra `/devices/:id` do device encontrado. Sem tela de confirmacao intermediaria"
[4] "Fallback sem camera** (permissao negada, indisponivel, ou erro): campo de texto manual na mesma pagina"
[5] "Se 1 resultado: redirect direto pro device"
[6] "Se varios resultados: mostra lista pra escolher"
[7] "Se 0 resultados: mensagem de erro, permite tentar de novo"
[8] "mensagem de erro inline na propria pagina `/devices/scan`. Camera continua ativa, permite nova tentativa sem reload de pagina"
[9] "Nao mudar o payload do QR (continua sendo a URL publica `/q/:publicCode`)"
[11] "fix(devices): extract scan decode logic to testable module"
[12] "Nao escala bem quando o operador esta com o device fisico na mao"
[13] "Acesso a camera exige HTTPS (ou localhost)"
[14] "`BarcodeDetector` tem suporte limitado (Chrome/Edge)"

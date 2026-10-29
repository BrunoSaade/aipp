🚀 *Busca de dispositivos por leitura de QR code no backoffice*

Pessoal, disponibilizamos uma melhoria no backoffice para identificar dispositivos físicos: agora basta apontar a câmera para o QR code impresso no dispositivo.

✨ *O que mudou?*

📷 Nova tela *Escanear QR*, acessível por um botão na lista de dispositivos. A câmera lê o QR code e abre direto a página de detalhe do dispositivo, sem precisar digitar nada.

⌨️ Sem câmera disponível (permissão negada ou indisponível)? Na mesma tela dá para digitar o código do dispositivo:
- 1 resultado: abre direto o dispositivo
- vários resultados: mostra a lista para escolher
- nenhum resultado: exibe mensagem para tentar de novo

💬 QR code inválido ou dispositivo não encontrado mostram uma mensagem na própria tela, e a câmera continua ativa para uma nova tentativa, sem recarregar a página.

🔄 O QR code impresso nos dispositivos continua o mesmo: nada precisa ser reimpresso.

🧪 Foram adicionados testes automatizados para a leitura do QR code.

🎯 *Benefícios da melhoria*
- Identificação do dispositivo direto pela câmera, com ele em mãos.
- Alternativa manual garantida quando a câmera não estiver disponível.

⚠️ A câmera só funciona em conexão segura (HTTPS) e a leitura nativa é mais completa no Chrome e no Edge.

Caso encontrem qualquer comportamento inesperado durante os testes ou uso da funcionalidade, por favor reportem no canal da squad. 🙌

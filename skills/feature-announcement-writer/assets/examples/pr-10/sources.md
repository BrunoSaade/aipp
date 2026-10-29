🔍 **Fontes**
- Problema (operador com o dispositivo na mão precisa digitar o código) → PRD (Problema)
- Tela Escanear QR, botão na lista, câmera abre o detalhe → PRD (Solução; Requisitos 2, 6) + commits `add scan page view with camera and manual fallback`, `add QR scan routes and entry point`
- Busca manual: 1 resultado, vários, nenhum → PRD (Requisito 8) + commit `add exact publicCode lookup to device service`
- Erro inline, câmera segue ativa sem recarregar → PRD (Requisito 7) + spec (P1: Tratamento de erro sem reload)
- QR impresso continua o mesmo → PRD (Requisito 4; Fora de escopo)
- Testes → 2 arquivos de teste no PR + commit `extract scan decode logic to testable module`
- HTTPS e suporte Chrome/Edge → PRD (Riscos / pontos de atenção)

⚠️ **Revisar antes de enviar**
- "Menos erros de digitação" é inferência a partir do problema descrito no PRD, não um dado medido.

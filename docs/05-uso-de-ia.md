# 5. Uso de assistentes de IA

<!-- O uso de assistentes de IA é permitido. Registre cada uso relevante: o que foi
pedido, o que o assistente sugeriu e o que a dupla aceitou ou descartou, com o motivo.
Se a dupla não usou nenhum assistente, escreva isso. -->

| Entrega | O que foi pedido | O que o assistente sugeriu | Decisão da dupla | Motivo |
|---|---|---|---|---|
| 1. Modelagem do domínio | Ao Claude (chat): ler o enunciado do CP3 e propor contextos, mapa de contexto, agregados e linguagem ubíqua, em forma de PRD para o Claude Code executar | Contexto novo Garantia de Prazo; RF05 no Rastreamento da Frota, porque a regra de 200 m e 10 min usa a linguagem de posição; Pedidos e Frete como fornecedores sem requisito próprio; atraso em minutos arredondados para cima; Cortesia avisada só acima da tolerância | Aceita | Cada requisito ficou com um único contexto responsável e a Garantia não precisa conhecer coordenadas; contar o atraso em minutos arredondados para cima classifica igual aos horários exatos nos limites de 120, 1.440 e 4.320 min |
| 2. Arquitetura | Ao Claude (chat): propor protocolos, padrões e soluções para RF06, RF09 e RNF04, em forma de PRD | UDP para telemetria; HTTPS com chave de idempotência e AMQP (RabbitMQ) para a confirmação; HTTP síncrono para Frete e Telemetria; SSE para o Portal; Strategy, Adapter, Retry com fila de falhas, Idempotent Consumer, Transactional Outbox e Observer; não aplicar Decorator (contraexemplo numérico com o teto) nem Singleton; contador transacional no banco em vez de SEQUENCE | Aceita | Cada protocolo segue a tolerância a perda exigida (UDP onde o RNF01 tolera perda, fila durável onde não tolera); o contraexemplo de R$ 1.500,00 mostrou que o Decorator daria crédito errado; o contador no banco evita número repetido e lacuna entre réplicas, o que um Singleton em memória não garante |

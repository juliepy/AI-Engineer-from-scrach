# Política de Aprovação (Pass Gate)

Uma funcionalidade só pode passar de `passes: false` para `passes: true` quando:

- o fluxo de trabalho esperado tiver sido executado
- a evidência de sucesso tiver sido registrada
- não existir nenhum erro bloqueador no caminho testado
- a implementação não deixar a aplicação em um estado quebrado ou ambíguo
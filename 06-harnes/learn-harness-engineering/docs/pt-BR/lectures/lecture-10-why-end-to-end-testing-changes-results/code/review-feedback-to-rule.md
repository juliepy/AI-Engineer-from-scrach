# Exemplo: Transformando Feedback de Revisão em uma Regra

Comentário recorrente de revisão:

> Não chame utilitários do sistema de arquivos a partir do renderer. Utilize a ponte de preload.

Regra promovida para o harness:

- adicionar uma regra de lint ou de importação que impeça o uso de `fs` no código do renderer
- adicionar um texto de correção explicando a fronteira de responsabilidade do preload
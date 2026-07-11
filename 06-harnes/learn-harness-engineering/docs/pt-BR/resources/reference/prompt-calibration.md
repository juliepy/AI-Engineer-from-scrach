# Calibração de Prompt (Prompt Calibration)

As instruções de raiz devem definir a estrutura operacional, não cada movimento possível.

## Manter no Arquivo de Raiz

- propósito e escopo do repositório
- caminho de inicialização
- caminho de verificação
- restrições não negociáveis
- artefatos de estado obrigatórios
- regras de fim de sessão

## Mover para Fora do Arquivo de Raiz

- casos de borda históricos longos
- detalhes de implementação específicos do tópico
- notas de arquitetura local que pertencem ao código
- exemplos que se aplicam apenas a um subsistema

## Regra de Trabalho

O arquivo de raiz deve ajudar uma nova sessão a se orientar rapidamente. Se o arquivo estiver se tornando um depósito para cada falha passada, divida os detalhes em documentos menores e crie links para eles.

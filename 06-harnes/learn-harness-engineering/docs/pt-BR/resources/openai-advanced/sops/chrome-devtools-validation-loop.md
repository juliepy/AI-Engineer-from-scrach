# SOP: Loop de Validação do Chrome DevTools

Use este SOP quando o trabalho de UI depender da interação real em tempo de execução e quando capturas de tela, estado do DOM e saída do console importarem mais do que apenas a inspeção do código.

## Objetivo

Transformar a validação de UI em um loop de interação repetível que o agente possa executar até que a jornada esteja limpa.

## Loop Principal

1. Selecione a página de destino ou a instância do aplicativo.
2. Limpe ruídos obsoletos do console.
3. Capture o estado ANTES (BEFORE).
4. Acione o caminho da UI.
5. Observe os eventos em tempo de execução durante a interação.
6. Capture o estado DEPOIS (AFTER).
7. Aplique a correção e reinicie o aplicativo, se necessário.
8. Execute a validação novamente até que a jornada esteja limpa.

## Entradas Obrigatórias

- um comando de inicialização estável.
- uma jornada de UI reproduzível.
- uma maneira de capturar instantâneos do DOM, console ou capturas de tela.
- uma regra para o que conta como "limpo".

## SOP de Execução

1. Escreva a jornada de destino no plano ativo.
2. Defina o sucesso em termos observáveis: texto presente, botão habilitado, erro removido, console limpo, solicitação bem-sucedida.
3. Capture o estado inicial antes da interação.
4. Acione exatamente um caminho por vez.
5. Registre eventos de tempo de execução, mudanças no DOM e saída visível.
6. Se a jornada falhar, corrija a menor camada responsável e reinicie.
7. Execute o mesmo caminho novamente e compare as evidências de ANTES/DEPOIS.

## Critérios de Limpeza (Clean Criteria)

- o estado visível pretendido está presente.
- erros inesperados estão ausentes.
- o ruído do console foi compreendido ou limpo.
- a reexecução do mesmo caminho produz o mesmo resultado.

## Artefatos do Repositório a Atualizar

- plano de execução ativo.
- `docs/RELIABILITY.md` se a jornada se tornar um caminho crítico (golden path).
- especificação do produto se o comportamento visível mudar.

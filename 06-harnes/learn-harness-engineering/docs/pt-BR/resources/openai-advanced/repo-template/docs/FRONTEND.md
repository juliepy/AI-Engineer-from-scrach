# FRONTEND.md

Este arquivo define expectativas estáveis de frontend para que os agentes não inventem padrões de UI de forma imprevisível.

## Princípios de UI

- Otimize pela clareza antes da novidade.
- Mantenha os fluxos de interação detectáveis e reinicializáveis.
- Prefira um pequeno número de componentes reutilizáveis em vez de variantes únicas (one-off).
- Verificações de acessibilidade fazem parte da verificação normal, não são apenas um trabalho de polimento.

## Salvaguardas (Guardrails)

- Documente o design system ou a biblioteca de componentes em `docs/references/`.
- Registre os principais estados voltados ao usuário: vazio, carregando, sucesso, erro, retentativa.
- Mantenha a redação (copy), o comportamento do teclado e a hierarquia visual consistentes entre os fluxos.
- Quando um bug de UI for corrigido, adicione ou atualize a etapa de validação correspondente.

## Expectativas de Verificação

- Capture evidências para jornadas críticas do usuário.
- Registre as etapas de validação do navegador ou do runtime no plano relevante.
- Se regressões visuais forem comuns, padronize as verificações de captura de tela ou do DOM.

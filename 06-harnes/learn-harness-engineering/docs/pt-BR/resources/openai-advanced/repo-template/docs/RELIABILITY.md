# RELIABILITY.md

Este arquivo define como o sistema prova que está saudável e reinicializável.

## Caminhos Padrão

- Inicialização (Bootstrap): `[comando]`
- Verificação: `[comando]`
- Iniciar aplicativo ou serviço: `[comando]`
- Depurar ou inspecionar o runtime: `[comando]`

## Sinais Obrigatórios de Runtime

- logs estruturados para inicialização e fluxos críticos.
- verificações de saúde (health checks) para serviços essenciais.
- dados de rastreamento ou tempo para caminhos lentos, quando disponíveis.
- estados de erro visíveis ao usuário para falhas recuperáveis.

## Jornadas Críticas (Golden Journeys)

- `[jornada 1]`
- `[jornada 2]`
- `[jornada 3]`

Cada jornada crítica deve ter um caminho de verificação repetível e sinais de falha claros.

## Regras de Confiabilidade

- Nenhum recurso está concluído se o sistema não puder reiniciar de forma limpa depois.
- Falhas em tempo de execução devem ser diagnosticáveis a partir de sinais locais do repositório.
- Se um modo de falha repetido aparecer, adicione um benchmark ou uma salvaguarda para ele.
- A limpeza faz parte da confiabilidade, não é uma preocupação separada.

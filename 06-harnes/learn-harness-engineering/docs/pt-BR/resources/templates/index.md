# Guia de Modelos (Templates)

Estes modelos estão prontos para serem copiados para o seu próprio projeto. Cada um serve a um propósito específico no fluxo de trabalho do agente. Edite o conteúdo para corresponder aos comandos, caminhos, nomes de recursos e etapas de verificação do seu projeto.

## Como Começar

Copie estes quatro arquivos para a raiz do seu projeto primeiro:

1. `AGENTS.md` ou `CLAUDE.md`
2. `init.sh`
3. `claude-progress.md`
4. `feature_list.json`

Adicione os arquivos restantes conforme seu projeto cresce.

---

## AGENTS.md

O arquivo de instruções de raiz. Esta é a primeira coisa que o agente lê ao iniciar uma sessão. Ele define as regras de operação: o que fazer antes de escrever o código, como trabalhar e como finalizar.

**Como usar:**

- Copie para o diretório raiz do seu projeto
- Substitua as etapas do fluxo de trabalho de inicialização pelos caminhos e comandos reais do seu projeto
- Ajuste as regras de trabalho para corresponder às convenções da sua equipe
- Mantenha a seção de definição de concluído (definition of done) — é a parte mais importante

**O que ele faz pelo agente:**

- Diz para ler o progresso e o estado do recurso antes de começar o trabalho
- Força o trabalho em um recurso de cada vez
- Exige evidências antes de marcar qualquer coisa como concluída
- Define como deve ser um encerramento de sessão limpo

Use `AGENTS.md` para Codex ou outros agentes. Use `CLAUDE.md` se estiver trabalhando com o Claude Code — a estrutura é a mesma, apenas formatada para o estilo de instrução do Claude.

## init.sh

O script de inicialização. Executa a instalação de dependências, a verificação e imprime o comando de início — tudo de uma vez só.

**Como usar:**

- Copie para a raiz do seu projeto
- Edite estas três variáveis no topo:
  - `INSTALL_CMD` — seu comando de instalação de dependências (ex: `npm install`, `pip install -r requirements.txt`)
  - `VERIFY_CMD` — seu comando de verificação básica (ex: `npm test`, `pytest`)
  - `START_CMD` — seu comando de início do servidor de desenvolvimento (ex: `npm run dev`)
- Torne-o executável: `chmod +x init.sh`

**O que ele faz:**

1. Imprime o diretório atual (para que você possa confirmar que está rodando no lugar certo)
2. Instala as dependências
3. Executa o comando de verificação
4. Imprime o comando de início (ou o executa se `RUN_START_COMMAND=1` estiver definido)

Se a verificação falhar, o agente deve parar e corrigir a base antes de fazer qualquer outra coisa.

## claude-progress.md

O log de progresso. Cada sessão escreve neste arquivo, e cada nova sessão o lê primeiro.

**Como usar:**

- Copie para a raiz do seu projeto
- Preencha a seção "Estado Verificado Atual" com as informações do seu projeto
- Após cada sessão, atualize o registro da sessão

**O que cada campo significa:**

- **Estado Verificado Atual** — a única fonte da verdade para a situação atual do projeto
  - `Diretório raiz do repositório` — onde o projeto reside
  - `Caminho de inicialização padrão` — o comando para colocar o projeto em execução
  - `Caminho de verificação padrão` — o comando para executar os testes
  - `Recurso inacabado de maior prioridade` — o que a próxima sessão deve trabalhar
  - `Bloqueio atual` — qualquer coisa que esteja travada
- **Registro da Sessão** — uma entrada por sessão
  - `Objetivo` — o que você planejou fazer
  - `Concluído` — o que realmente foi feito
  - `Execução de verificação` — quais testes foram executados
  - `Evidência registrada` — qual prova foi capturada
  - `Commits` — o que foi commitado
  - `Riscos conhecidos` — o que pode estar quebrado
  - `Próxima melhor ação` — onde a próxima sessão deve começar

## feature_list.json

O rastreador de recursos. Uma lista legível por máquina de cada recurso que o agente precisa implementar, junto com seu status, etapas de verificação e evidências.

**Como usar:**

- Copie para a raiz do seu projeto
- Substitua os recursos de exemplo pelos seus próprios
- Cada recurso precisa de:
  - `id` — um identificador único curto
  - `prioridade` — número inteiro, menor = maior prioridade
  - `área` — qual parte do app (ex: "chat", "importação", "busca")
  - `título` — descrição curta
  - `comportamento_visível_ao_usuário` — o que o usuário deve ver quando funcionar
  - `status` — um de `not_started`, `in_progress`, `blocked`, `passing`
  - `verificação` — instruções passo a passo para confirmar que funciona
  - `evidência` — prova registrada de que a verificação passou (preenchida pelo agente)
  - `notas` — qualquer contexto extra

**Regras de status:**

- `not_started` — não foi tocado
- `in_progress` — o único recurso em que se está trabalhando no momento (apenas um por vez)
- `blocked` — não pode prosseguir devido a um problema documentado
- `passing` — a verificação passou e a evidência está registrada

O agente deve ter apenas um recurso em `in_progress` a qualquer momento.

## session-handoff.md

Uma nota de entrega compacta entre sessões. Use isso quando uma sessão terminar e você quiser que a próxima continue rapidamente.

**Como usar:**

- Copie para a raiz do seu projeto
- Preencha ao final de cada sessão (ou peça para o agente preencher)

**O que cada seção cobre:**

- **Verificado atualmente** — o que está confirmado como funcionando e qual verificação foi executada
- **Alterações nesta sessão** — qual código ou infraestrutura mudou
- **Ainda quebrado ou não verificado** — problemas conhecidos e áreas de risco
- **Próxima melhor ação** — o que a próxima sessão deve fazer e o que não tocar
- **Comandos** — comandos de inicialização, verificação e depuração para referência rápida

Este arquivo é opcional para sessões pequenas. Ele se torna importante quando as sessões são longas ou quando o projeto tem várias áreas ativas.

## clean-state-checklist.md

Um checklist para percorrer antes de encerrar cada sessão. Garante que o repositório esteja em um bom estado para a próxima sessão começar de forma limpa.

**Como usar:**

- Copie para a raiz do seu projeto
- Percorra-o antes de fechar uma sessão
- O agente também deve verificar esses itens como parte de sua rotina de fim de sessão

**O que ele verifica:**

- A inicialização padrão ainda funciona
- A verificação padrão ainda roda
- O log de progresso está atualizado
- A lista de recursos reflete o estado real (sem entradas `passing` falsas)
- Nenhum trabalho inacabado foi deixado sem registro
- A próxima sessão pode continuar sem correções manuais

## evaluator-rubric.md

Um cartão de pontuação para revisar a qualidade da entrega do agente. Use isso após uma sessão ou em marcos do projeto para avaliar se o trabalho atende aos critérios.

**Como usar:**

- Copie para a raiz do seu projeto
- Após uma sessão (ou um conjunto de sessões), pontue o trabalho do agente em seis dimensões
- Cada dimensão é pontuada de 0 a 2

**As seis dimensões:**

1. **Correção** — a implementação corresponde ao comportamento pretendido?
2. **Verificação** — as verificações exigidas foram realmente executadas, com evidências?
3. **Disciplina de escopo** — o agente permaneceu dentro do recurso selecionado?
4. **Confiabilidade** — o resultado sobrevive a uma reinicialização ou re-execução?
5. **Manutenibilidade** — o código e a documentação estão claros o suficiente para a próxima sessão?
6. **Prontidão para entrega** — uma nova sessão pode continuar usando apenas os artefatos do repositório?

**Opções de conclusão:**

- Aceitar — atende aos critérios
- Revisar — precisa de correções antes de aceitar
- Bloquear — problemas fundamentais que precisam ser resolvidos primeiro

**Importante: o avaliador precisa de ajuste.** Por padrão, os agentes são maus juízes de si mesmos — eles identificam problemas e depois se convencem a aprovar. Você precisará iterar:

1. Execute o avaliador em um sprint concluído.
2. Compare suas pontuações com seu próprio julgamento humano.
3. Onde elas divergirem, torne a rúbrica mais específica sobre os critérios de aprovação/reprovação.
4. Execute novamente e verifique o alinhamento.
5. Repita até que o avaliador corresponda consistentemente à revisão humana.

Planeje de 3 a 5 rodadas de ajuste. Registre cada mudança para que você possa rastrear o que melhorou o alinhamento.

## quality-document.md

Um instantâneo de qualidade que avalia cada domínio de produto e camada arquitetônica em seu projeto. Acompanha a saúde da base de código ao longo do tempo, não apenas a entrega de uma sessão individual.

**Como usar:**

- Copie para a raiz do seu projeto
- Antes de iniciar uma sessão: leia para entender onde a base de código está mais fraca
- Após uma sessão: atualize as notas com base no que mudou
- Ao longo do tempo: compare os instantâneos para ver quais mudanças no harness realmente melhoraram a saúde da base de código

**O que ele avalia:**

- **Domínios de produto** (ex: importação de documentos, fluxo de Q&A, indexação): cada domínio recebe uma nota (A-D) em status de verificação, legibilidade para o agente, estabilidade de teste e lacunas principais
- **Camadas arquitetônicas** (ex: processo principal, preload, renderizador, serviços): cada camada recebe uma nota para aplicação de limites e legibilidade para o agente

**Por que isso importa:**

A rúbrica do avaliador pontua entregas individuais de agentes. O documento de qualidade pontua a própria base de código. Eles respondem a perguntas diferentes:

- Rúbrica do avaliador: "O agente fez um bom trabalho nesta sessão?"
- Documento de qualidade: "O projeto está ficando mais forte ou mais fraco ao longo do tempo?"

**Quando atualizar:**

- Após cada sessão significativa
- Antes de comparações de benchmark
- Após passagens de limpeza ou simplificação
- Ao integrar um novo agente ou modelo ao projeto

**Ligação com a simplificação do harness:**

O documento de qualidade também apoia a simplificação do harness. Cada componente do harness codifica uma suposição sobre o que o modelo não pode fazer. À medida que os modelos melhoram, essas suposições tornam-se obsoletas. Para verificar se um componente ainda é necessário:

1. Tire um instantâneo do documento de qualidade.
2. Remova um componente do harness.
3. Execute a suíte de tarefas de benchmark.
4. Tire outro instantâneo.
5. Compare — se as notas não caíram, o componente era excesso. Se caíram, restaure-o.

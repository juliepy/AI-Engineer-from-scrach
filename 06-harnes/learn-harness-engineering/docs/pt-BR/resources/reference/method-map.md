# Mapa de Métodos (Method Map)

Esta tabela mapeia os modos de falha mais comuns em agentes de codificação de longa duração para o artefato ou regra operacional que geralmente os corrige primeiro.

| Modo de Falha | Como se parece na prática | Correção Principal | Artefato de Suporte |
| --- | --- | --- | --- |
| Confusão de Início a Frio (Cold-start) | Uma nova sessão gasta a maior parte do tempo redescobrindo a configuração e o status | Torne o repositório o sistema de registro | `claude-progress.md` |
| Expansão de Escopo (Scope sprawl) | O agente inicia vários recursos e não termina nenhum deles de forma limpa | Restrinja o escopo ativo | `feature_list.json` |
| Conclusão Prematura | O agente afirma que concluiu após as edições de código, mas antes da prova executável | Vincule a conclusão à evidência | `clean-state-checklist.md` |
| Inicialização Frágil | Cada sessão aprende novamente como inicializar o projeto | Padronize a configuração e a verificação | `init.sh` |
| Entrega Fraca (Weak handoff) | A próxima sessão não consegue dizer o que está verificado, quebrado ou o que vem a seguir | Termine com uma entrega explícita | `session-handoff.md` |
| Revisão Subjetiva | A qualidade da revisão depende do gosto ou da memória | Pontue a entrega com categorias fixas | `evaluator-rubric.md` |

## Princípio Operacional

Adicione o menor artefato que aborde diretamente o modo de falha observado. Evite resolver todos os problemas de confiabilidade despejando mais texto em um único arquivo de instrução global.

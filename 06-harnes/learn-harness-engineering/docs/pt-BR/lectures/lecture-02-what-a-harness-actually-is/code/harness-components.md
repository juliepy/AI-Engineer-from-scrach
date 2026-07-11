# Exemplo de Componentes de um Harness

Para um agente de código trabalhando em um repositório local:

- Modelo:
  o próprio LLM

- Harness:
  - prompt de sistema
  - AGENTS.md
  - ferramenta de bash
  - ferramentas de leitura/escrita de arquivos
  - acesso ao git
  - sistema de arquivos local
  - scripts de inicialização
  - comandos de teste
  - hooks de parada
  - verificações de lint
  - loop de avaliação

Se você alterar qualquer um dos componentes acima do harness, você altera o agente efetivo.
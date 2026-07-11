# Regras de Arquitetura Electron

- O código do renderer não pode acessar o sistema de arquivos diretamente.
- O preload é a única ponte entre o renderer e o processo principal (Electron Main).
- A lógica de recuperação e indexação deve ficar em módulos de serviço, não em componentes de UI.
- Os logs devem ser estruturados e emitidos a partir das fronteiras da camada de serviço.
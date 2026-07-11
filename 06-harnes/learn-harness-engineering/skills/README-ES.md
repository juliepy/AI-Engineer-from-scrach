<p align="center">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/English-d9d9d9"></a>
  <a href="README-CN.md"><img alt="简体中文" src="https://img.shields.io/badge/简体中文-d9d9d9"></a>
  <a href="README-ZH-TW.md"><img alt="繁體中文" src="https://img.shields.io/badge/繁體中文-d9d9d9"></a>
  <a href="README-JA.md"><img alt="日本語" src="https://img.shields.io/badge/日本語-d9d9d9"></a>
  <a href="README-ES.md"><img alt="Español" src="https://img.shields.io/badge/Español-d9d9d9"></a>
  <a href="README-FR.md"><img alt="Français" src="https://img.shields.io/badge/Français-d9d9d9"></a>
  <a href="README-KO.md"><img alt="한국어" src="https://img.shields.io/badge/한국어-d9d9d9"></a>
  <a href="README-AR.md"><img alt="العربية" src="https://img.shields.io/badge/العربية-d9d9d9"></a>
  <a href="README-VI.md"><img alt="Tiếng_Việt" src="https://img.shields.io/badge/Tiếng_Việt-d9d9d9"></a>
  <a href="README-DE.md"><img alt="Deutsch" src="https://img.shields.io/badge/Deutsch-d9d9d9"></a>
  <a href="README-TR.md"><img alt="Türkçe" src="https://img.shields.io/badge/Türkçe-d9d9d9"></a>
</p>

# Skills

Este directorio contiene skills reutilizables para agentes de IA en el proyecto Learn Harness Engineering. Cada skill es una plantilla de prompt autocontenida que puede ser cargada por agentes de programación como Claude Code, Codex, Cursor o Windsurf.

## Skills disponibles

### harness-creator

Skill de harness engineering de nivel producción para agentes de programación. Ayuda a crear, evaluar y mejorar archivos de harness para agentes, como AGENTS.md, listas de funciones, flujos de verificación y mecanismos de continuidad entre sesiones.

- **7 patrones de referencia**: Memory Persistence, Skill Runtime, Context Engineering, Tool Registry, Multi-Agent Coordination, Lifecycle & Bootstrap, Gotchas
- **Plantillas**: AGENTS.md/CLAUDE.md, feature-list.json, init.sh, progress.md, session-handoff.md
- **Scripts**: scaffold, validación, informe HTML y benchmark estructural
- **10 casos de eval integrados**

Consulta la documentación completa en [harness-creator/README.md](harness-creator/README.md).

## Cómo se creó harness-creator

`harness-creator` se desarrolló con la metodología **skill-creator**, el meta-skill oficial de Anthropic para crear, probar e iterar skills de agentes mediante un flujo draft → test → evaluate → iterate.

## Cómo funcionan las skills

Cada skill sigue una estructura estándar:

1. **SKILL.md** — Punto de entrada con YAML frontmatter e instrucciones Markdown para el agente.
2. **references/** — Documentos adicionales que se cargan bajo demanda.
3. **templates/** — Plantillas iniciales que la skill puede generar.

Las skills usan progressive disclosure: el agente primero ve solo el nombre y la descripción, luego carga SKILL.md cuando se activa y lee recursos incluidos solo cuando son necesarios.

## Seguridad

Los archivos de este directorio fueron revisados:

- Sin backdoors, URL ocultas ni payloads codificados
- Sin exfiltración de datos ni credenciales hardcodeadas
- Sin vulnerabilidades de command injection
- Los scripts usan solo módulos integrados de Node.js
- El `init.sh` generado ejecuta los comandos de verificación detectados del proyecto

## Licencia

MIT

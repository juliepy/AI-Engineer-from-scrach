# ARCHITECTURE.md

Diese Datei ist die Top-Level-Übersicht des Systems. Sie sollte prägnant bleiben und
auf tiefere Dokumente verweisen, wenn nötig.

## Systemform

- Produkt: `[mit Produktnamen ersetzen]`
- Primärer Benutzer-Workflow: `[mit Hauptworkflow ersetzen]`
- Laufzeitoberflächen: `[Desktop / Web / CLI / Services / Worker]`
- Source of Truth für Produktverhalten: `docs/product-specs/`

## Domänen-Map

| Domäne | Zweck | Primäre Einstiegspunkte | Zugehörige Spec |
|--------|-------|------------------------|----------------|
| `[domäne-a]` | `[was sie besitzt]` | `[Module / Routen / Befehle]` | `[Spec-Pfad]` |
| `[domäne-b]` | `[was sie besitzt]` | `[Module / Routen / Befehle]` | `[Spec-Pfad]` |

## Schichtenmodell

Verwenden Sie ein festes gerichtetes Modell, damit Agenten keine ad-hoc-Architektur erfinden:

`Types -> Config -> Repo -> Service -> Runtime -> UI`

Querschnittliche Belange sollten über explizite Provider- oder Adapter-Grenzen
eintreten, anstatt Schichten direkt zu überspringen.

## Harte Abhängigkeitsregeln

- Untere Schichten dürfen nicht von oberen Schichten abhängen.
- UI darf Runtime- oder Service-Verträge nicht umgehen.
- Datenzugriff muss über Repositories oder äquivalente Adapter erfolgen.
- Gemeinsame Utilities müssen generisch bleiben und dürfen keine Domänenlogik ansammeln.
- Neue Abhängigkeiten sollten im entsprechenden Plan oder Design-Doc begründet werden.

## Querschnittsschnittstellen

| Belang | Genehmigte Grenze | Notizen |
|--------|-------------------|---------|
| Logging und Tracing | `[Provider / Utility-Pfad]` | `[nur strukturiert, kein ad-hoc Console-Use]` |
| Auth | `[Provider-Pfad]` | `[Token/Session-Regeln]` |
| Externe APIs | `[Client oder Provider-Pfad]` | `[Rate-Limit / Retry-Guidance]` |
| Feature-Flags | `[Flag-Grenze]` | `[Ownership]`` |

## Aktuelle Hot Spots

- `[Bereich, der für Agenten am schwersten sicher zu ändern ist]`
- `[Bereich mit schwachen Grenzen oder fragilen Tests]`

## Änderungs-Checkliste

Wenn Sie architekturrelevanten Code berühren:

1. Diese Datei aktualisieren, falls sich die Domänen-Map oder erlaubten Grenzen geändert haben.
2. Das zugehörige Design-Doc in `docs/design-docs/` aktualisieren, falls sich die Begründung geändert hat.
3. Einen ausführbaren Check hinzufügen oder aktualisieren, falls die Regel mechanisch durchgesetzt werden soll.

# OpenAI Advanced Pack

Dieser Ordner verpackt die stärker meinungsbasierte Repository-Struktur, die in
OpenAIs Artikel "Harness engineering: leveraging Codex in an agent-first world"
beschrieben wird, in kopierfertige Starterdateien.

Verwenden Sie dieses Pack, wenn das minimale Harness nicht mehr ausreicht und
Ihr Repository nun Folgendes benötigt:

- eine kurze, routing-artige `AGENTS.md`
- dauerhafte System-of-Record-Dokumentation innerhalb des Repos
- aktive und abgeschlossene Ausführungspläne
- explizite Produkt-, Zuverlässigkeits-, Sicherheits- und Frontend-Richtliniendateien
- Qualitätsbewertung nach Produktdomäne und Architektur-Schicht
- modellfreundliche Referenzmaterial-Ordner
- Standardarbeitsanweisungen (SOPs) für Architektur, Wissenserfassung und Laufzeitvalidierung

## Enthaltene Starter-Struktur

Das Starter-Pack unter [`repo-template/`](./repo-template/index.md) spiegelt die
folgende Struktur wider:

```text
AGENTS.md
ARCHITECTURE.md
docs/
├── design-docs/
│   ├── index.md
│   └── core-beliefs.md
├── exec-plans/
│   ├── active/
│   ├── completed/
│   └── tech-debt-tracker.md
├── generated/
│   └── db-schema.md
├── product-specs/
│   ├── index.md
│   └── new-user-onboarding.md
├── references/
│   ├── design-system-reference-llms.txt
│   ├── nixpacks-llms.txt
│   └── uv-llms.txt
├── DESIGN.md
├── FRONTEND.md
├── PLANS.md
├── PRODUCT_SENSE.md
├── QUALITY_SCORE.md
├── RELIABILITY.md
└── SECURITY.md
```

## Wie Sie es übernehmen

1. Beginnen Sie mit dem minimalen Pack, wenn Ihr Repo noch klein ist.
2. Kopieren Sie die Dateien aus [`repo-template/`](./repo-template/index.md) in
   Ihr eigenes Repository, sobald Sie eine stärkere Struktur benötigen.
3. Halten Sie `AGENTS.md` kurz. Behandeln Sie sie als Router zu den tieferen Docs,
   nicht als Enzyklopädie.
4. Aktualisieren Sie die Qualitäts-, Zuverlässigkeits- und Plan-Dokumente als
   Teil der normalen Arbeit, nicht an einem separaten Aufräumtag.
5. Halten Sie generierte Artefakte und externe Referenzen explizit, damit Agenten
   sie finden können, ohne sich auf Chat-Verlauf zu verlassen.

## SOP-Bibliothek

Der Ordner [`sops/`](./sops/index.md) wandelt die Diagramme des Artikels in
schrittweise Arbeitsanweisungen um:

- Einrichtung einer geschichteten Domänenarchitektur
- Codierung von unsichtbarem Wissen in das Repository
- lokaler Observability-Stack und Feedback-Schleifen-Workflow
- Chrome DevTools-Validierungsschleife für UI-Arbeit

## Design-Prinzipien

- Kurzer Einstiegspunkt, tiefer verlinkte Docs
- Repository als System of Record
- Mechanische Prüfungen schlagen erinnerte Regeln
- Pläne und Qualitätsverlauf leben neben dem Code
- Aufräumen und Vereinfachung sind Aufgaben erster Klasse

Dieses Pack ist bewusst meinungsbasiert, sollte aber an Ihr Projekt angepasst
werden, anstatt blind kopiert zu werden.

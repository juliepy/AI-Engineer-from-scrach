# Initializer-Agenten-Playbook

Verwenden Sie dieses Playbook für die erste ernsthafte Session in einem Repository,
bevor inkrementelle Feature-Arbeit beginnt.

## Ziel

Eine stabile Betriebsoberfläche schaffen, sodass spätere Sessions Verhalten
implementieren können, ohne Startbefehle, aktuellen Status oder Task-Grenzen
neu abzuleiten.

## Erforderliche Outputs

Der Initializer sollte mindestens diese Artefakte hinterlassen:

- eine Root-Instruktionsdatei wie `AGENTS.md` oder `CLAUDE.md`
- eine maschinenlesbare Feature-Oberfläche wie `feature_list.json`
- ein dauerhaftes Fortschrittsartefakt wie `claude-progress.md`
- einen Standard-Starthelfer wie `init.sh`
- einen ersten sicheren Commit, der das Baseline-Gerüst erfasst

## Checkliste

1. Den Standard-Startpfad definieren.
2. Den Standard-Verifikationspfad definieren.
3. Das Fortschrittslog erstellen und den Startzustand dokumentieren.
4. Die Arbeit in explizite Features mit Status zerlegen.
5. Den ersten sauberen Baseline-Commit erstellen.

## Erfolgstest

Eine frische Session ohne vorherigen Chat-Kontext sollte folgende Fragen beantworten können:

- Was dieses Repository macht
- Wie man es startet
- Wie man es verifiziert
- Was unvollendet ist
- Was der nächste beste Schritt ist

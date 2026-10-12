# Report-Vertrag

Dieser Vertrag beschreibt den fachlichen Umfang und die Darstellung des reproduzierbaren
Testabschlussberichts in H2ORB. Reportvorschau und Markdown-Download sind gemäß
diesem Vertrag umgesetzt.

## Umfang und Reproduzierbarkeit

- Der Detailteil umfasst den zuletzt ausgewerteten Startordner einschließlich aller rekursiv
  enthaltenen Ordner und Testszenarien.
- Die erste Summary-Zeile zeigt immer die Gesamtwerte des aktuellen Startknotens. Zusätzlich können
  Ordner im Ergebnisbaum über eine Checkbox ausgewählt werden; jeder ausgewählte Unterordner bildet
  eine weitere eigenständige Summary-Zeile.
- Überlappende ausgewählte Ordner werden nicht miteinander verrechnet; jede Zeile zeigt die
  Aggregation ihres eigenen Teilbaums.
- Die interaktiven Ansichtsfilter `Nur X-Testfälle`, `F`, `N` und `N?` verändern den Report nicht.
- Grundlage sind dieselben geladenen und aggregierten Ergebnisdaten wie im Ergebnisbaum.
- Für jeden Testjob eines Testszenarios wird ausschließlich die neueste relevante Ausführung
  berücksichtigt.
- Ein erneutes Laden aktueller AQUA-Daten erfolgt durch eine ausdrücklich gestartete neue
  Auswertung. Eine separate Aktion `Report aktualisieren` ist für eine spätere Erweiterung
  vorgesehen.

## Aufbau

Der Report enthält in dieser Reihenfolge:

1. Titel, Erstellungszeitpunkt und gewählter Startordner
2. zusammengefasste Kennzahlen für den vollständigen Reportumfang
3. detaillierte fehlgeschlagene Ergebnisse (`F`, `N` und `N?`)

Die Summary enthält je ausgewähltem Ordner `SUM`, `P`, `X`, `F`, `N`, `N?` sowie deren
Prozentwerte. Andere Zustände werden im Report nicht aufgeführt. Die Kennzahlen entsprechen dem
Ergebnisbaum:

```text
X   = F + N + N?
P%  = P / SUM
X%  = X / SUM
F%  = F / SUM
N%  = N / SUM
N?% = N? / SUM
```

## Detailtiefe fehlgeschlagener Ergebnisse

Für `F`, `N` und `N?` wird der vollständige fachliche Zusammenhang dargestellt:

```text
Testszenario (TS)
└── Testfall (TC)
    ├── neueste relevante Ausführung (TE)
    └── zugeordnete AQUA-Defects (DF)
        └── Defect-Beschreibung
```

- TS, TC, TE und DF werden mit formatierter AQUA-ID und Bezeichnung dargestellt.
- Jede vorhandene ID ist mit der jeweiligen AQUA-Webseite verlinkt.
- Mehrere einem Ergebnis zugeordnete Defects werden vollständig aufgeführt.
- `N?` besitzt definitionsgemäß keinen zugeordneten AQUA-Defect.
- Externe Jira-Links und Jira-Inhalte sind nicht Bestandteil des Reports.

## Defect-Beschreibungen

Defect-Details werden über `GET /api/Defect/{id}?withEnclosure=true` geladen. Für Markdown wird
bevorzugt `Enclosures[].Content.PlainText` verwendet. HTML-Inhalte werden nicht ungeprüft in den
Report übernommen.

- Jeder eindeutige Defect wird innerhalb einer Reporterstellung höchstens einmal geladen.
- Defect-Details werden nur für tatsächlich berichtete `F`- und `N`-Ergebnisse benötigt.
- Fehlende Leseberechtigung, eine fehlende Beschreibung oder ein fehlgeschlagener Detailabruf
  verhindert die Reporterstellung nicht; die Beschreibung wird dann als nicht verfügbar markiert.
- Die bereits über die Ausführungsrelation bekannte DF-ID, Bezeichnung und Verlinkung bleiben auch
  ohne Detailbeschreibung sichtbar.

## Darstellung und Ausgabe

- Die bestehende Ergebnisseite erhält die gleichrangigen Ansichten `Ergebnisbaum` und `Report`.
- Der Report wird innerhalb derselben Ergebnisfläche als formatiertes HTML dargestellt.
- Eine Aktion `Markdown herunterladen` liefert denselben Inhalt als UTF-8-kodierte `.md`-Datei.
- Die Reportvorschau verwendet die Sprache der aktuell ausgewählten Benutzeroberfläche.
- Eine spätere Druck- beziehungsweise PDF-Ausgabe ist eine optionale Erweiterung und nicht Teil der
  ersten Reportimplementierung.

## Sicherheit

- AQUA-Zugangsdaten und Zugriffstoken werden weder im Report noch im Browser ausgegeben.
- Der Browser kommuniziert weiterhin ausschließlich mit dem H2ORB-Backend.
- Von AQUA gelieferte Inhalte werden vor einer HTML-Darstellung escaped beziehungsweise bereinigt.


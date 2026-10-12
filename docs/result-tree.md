# Ergebnisbaum

H2ORB stellt die Ergebnisse nicht als flache Szenarioliste dar. Stattdessen wird
aus den AQUA-Daten ein Explorer-Baum aufgebaut:

```text
Projekt
└── Ordner
    └── TS000067  Testszenario
        └── TC000060  Testfall
            ├── TE000049  Ausführung
            └── DF000078  AQUA-Fehler
```

## Darstellung

- Jeder Projekt- und Ordnerbestandteil ist ein eigener aufklappbarer Knoten und belegt eine Zeile.
- Gemeinsame Ordner werden anhand ihrer stabilen AQUA-Ordner-ID zusammengeführt.
- Die Spalte `Pfad` enthält die eingerückte Baumstruktur. Bei TS-, TC-, TE- und DF-Knoten steht dort
  die formatierte AQUA-ID.
- Die separate ID-Spalte entfällt. Die Bezeichnung steht direkt rechts neben dem Baum und erhält
  dadurch mehr Platz.
- Jeder Knoten kann unabhängig auf- und zugeklappt werden. Das Aufklappen verarbeitet nur bereits
  geladene Daten und löst keine weitere AQUA-Abfrage aus.
- Bestandene Testfälle werden je Testszenario in einem eigenen, standardmäßig geschlossenen
  `Passed`-Knoten zusammengefasst. Der Knoten zeigt die aggregierten Kennzahlen; beim Aufklappen
  bleiben die einzelnen TC- und TE-Knoten verfügbar. Alle nicht bestandenen Testfälle stehen zur
  direkten Analyse weiterhin unmittelbar unter dem Testszenario.
- Der Schalter `Nur X-Testfälle` reduziert den Baum auf fehlgeschlagene Testfälle und öffnet die
  zugehörigen Projekt-, Ordner- und TS-Pfade automatisch. Im aktiven Zustand lassen sich die
  Kategorien `F`, `N` und `N?` unabhängig ein- und ausblenden. Die Filter verändern ausschließlich
  die sichtbaren Baumzeilen; sämtliche aggregierten Kennzahlen bleiben auf die vollständige
  Auswertung bezogen.
- Projekt- und Ordnerzeilen besitzen vor der Pfadspalte einen Auswahlbutton. Er übernimmt den
  vollständigen Pfad als neuen `Gewählten Startordner`; eine neue AQUA-Auswertung beginnt erst nach
  dem anschließenden Klick auf `Auswertung starten`.
- TS-, TC-, TE- und DF-Knoten können nicht als Startordner gewählt werden.
- TS-, TC-, TE- und DF-IDs öffnen das jeweilige Element über die konfigurierte
  `ARB_AQUA_WEB_BASE_URL` in einem neuen Browser-Tab. Externe Jira-Verknüpfungen werden nicht
  erzeugt.
- Die Desktop-Oberfläche nutzt die verfügbare Browserbreite. Tabellenkopf, Pfad und Bezeichnung
  bleiben beim Scrollen sichtbar; die Ordnerauswahl kann nach dem Start der Auswertung eingeklappt
  werden.
- Alle Texte und Tooltips stehen auf Deutsch und Englisch zur Verfügung. Die Sprachauswahl wird im
  Browser gespeichert.

## Ergebnisermittlung

Für jeden Testjob eines Szenarios wird ausschließlich dessen neueste relevante Ausführung
verwendet. Ein Testfallknoten liefert genau einen Status:

| Status | Bedeutung |
| --- | --- |
| `P` | Ausführung erfolgreich |
| `X` | Alle fehlgeschlagenen Ergebnisse (`F + N + N?`) |
| `F` | Fehlgeschlagen, mit regulärem AQUA-Defect |
| `N` | Fehlgeschlagen, alle zugeordneten Defects enthalten den konfigurierten Noise-Marker |
| `N?` | Fehlgeschlagen, noch ohne zugeordneten AQUA-Defect |
| `A` | Ausführung abgebrochen (`Aborted`) |
| `NE` | Nicht ausgeführt (`NotRun`, `Queued` oder `Waiting`) |
| `B` | Ausführung blockiert (`Blocked`) |
| `NC` | Nicht abgeschlossen (`Incomplete` oder `InProgress`) |
| `NA` | Nicht anwendbar (`NotApplicable`) |
| `?` | Unbekannter oder nicht zugeordneter Status |

Der Noise-Marker ist über `ARB_NOISE_MARKER` konfigurierbar und lautet standardmäßig `[NOISE]`.
Die Erkennung im Defect-Titel ignoriert Groß-/Kleinschreibung. Sind mehrere Defects zugeordnet,
ergibt nur eine ausschließlich aus Noise-Defects bestehende Menge den Status `N`; mindestens ein
regulärer Defect ergibt `F`. Externe Jira-Verknüpfungen werden nicht ausgewertet.

## Kennzahlen

Die kompakten Spaltenüberschriften werden durch lokalisierte Tooltips erläutert. Alle Raten beziehen
sich auf `SUM`; bei `SUM = 0` wird ein Gedankenstrich angezeigt.

Auf einzelnen TC-Zeilen werden Nullwerte und sämtliche Raten ausgeblendet. Sichtbar bleiben nur
`SUM = 1`, der zutreffende exklusive Ergebnisstatus und bei einem Fehlschlag zusätzlich das daraus
abgeleitete `X = 1`. Aggregierte Projekt-, Ordner- und TS-Zeilen zeigen weiterhin alle Werte.

```text
X   = F + N + N?
P%  = P / SUM
X%  = X / SUM
F%  = F / SUM
N%  = N / SUM
N?% = N? / SUM
```

## Farben

Die Status- und zugehörigen Ratenspalten verwenden eine feste, kontrastreiche Farbfamilie. Soweit
vorhanden orientieren sich die Farben an den von AQUA ausgelieferten Styles:

| Spalte | Darstellung |
| --- | --- |
| `SUM` | Schwarz, ohne Statusfarbe |
| `P` / `P%` | Grün |
| `X` / `X%` | Kaminrot |
| `F` / `F%` | kräftiges Rot |
| `N` / `N%` | Purpurrot |
| `N?` / `N?%` | hellrosa Hintergrund mit dunkelroter Schrift |
| `A` | Gelber Hintergrund mit schwarzer Schrift |
| `NE` | Blauer Hintergrund mit weißer Schrift |
| `B` | AQUA-Orangegelb (`rgb(255, 164, 46)`) |
| `NC` | AQUA-Blau für In Progress (`rgb(77, 130, 184)`) |
| `NA` | AQUA-Grau für Not Applicable (`rgb(132, 132, 132)`) |
| `?` | Neutrales Grau |

## Rekursive Aggregation

Die Ermittlung erfolgt einmal in die Tiefe und wird anschließend von unten nach oben summiert:

1. Der TC-Knoten liefert genau einen Ergebniswert.
2. TE- und DF-Knoten sind reine Detailzeilen und besitzen keine Ergebniszahlen.
3. Ein TS-Knoten summiert die Ergebnisse seiner TC-Knoten.
4. Ein Ordner summiert alle direkt und indirekt enthaltenen TS- und Unterordner-Ergebnisse.
5. Das Projekt beziehungsweise der gewählte Startordner zeigt die Gesamtsumme seines Teilbaums.

Dadurch wird ein Ergebnis trotz zusätzlicher Ausführungs- oder Fehlerdetails niemals doppelt
gezählt.

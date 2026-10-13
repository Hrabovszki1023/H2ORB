# H2ORB Kurzanleitung

H2ORB fasst Testergebnisse aus AQUA in einem aufklappbaren Baum zusammen. Fehlgeschlagene Tests,
zugehörige Ausführungen und AQUA Defects sind dadurch ohne Suche über mehrere AQUA-Seiten gemeinsam
sichtbar. Der integrierte Testabschlussbericht lässt sich als Markdown herunterladen.

H2ORB ist ein unabhängiges Open-Source-Projekt und weder mit einem Anbieter von
Testmanagementsoftware verbunden noch von einem solchen Anbieter empfohlen.

Diese Kurzanleitung beschreibt die Bedienung. Verbindliche fachliche und technische Regeln stehen
in folgenden Dokumenten:

- [Ergebnisbaum](result-tree.md): Statusermittlung, Aggregation, Filter und Darstellung
- [Report-Vertrag](report-contract.md): Umfang, Summary und Detailinhalt des Berichts
- [Security-Roadmap](security-roadmap.md): Sicherheitsanforderungen und noch offene Härtungsmaßnahmen

## Sicherheitshinweis

Die aktuelle Version verwendet zentral konfigurierte AQUA-Zugangsdaten. Jeder Benutzer, der die
H2ORB-Oberfläche erreicht, kann die für dieses Konto freigegebenen AQUA-Projekte und Testergebnisse
lesen. Der Server darf deshalb nur in einem vertrauenswürdigen internen Netz betrieben werden.

- Port `8000` nicht direkt im Internet veröffentlichen.
- Den Zugriff mit Firewall-Regeln oder einem Reverse Proxy mit HTTPS und Zugriffskontrolle begrenzen.
- Ein dediziertes AQUA-Konto mit Leserechten und möglichst wenigen freigegebenen Projekten verwenden.
- `.env`, Passwörter, Zertifikatsschlüssel und Zugriffstoken niemals in das Image oder Repository
  aufnehmen.
- Erzeugte Berichte als potenziell vertrauliche Testdaten behandeln.

## Auswertung starten

1. H2ORB im Browser öffnen und das gewünschte AQUA-Projekt aufklappen.
2. Den Projekt- oder Versionsordner als Startordner auswählen.
3. **Auswertung starten** anklicken. H2ORB lädt Szenarien, Testfälle, letzte Ausführungen und Defects
   rekursiv.
4. Bei Bedarf auf **Report** wechseln und den Bericht als Markdown herunterladen.

## Ergebnisstatus

Die vollständige und verbindliche Statusdefinition steht im
[Vertrag für den Ergebnisbaum](result-tree.md#ergebnisermittlung). Für die Bedienung sind vor allem
folgende Status relevant:

| Kürzel | Bedeutung | Verwendung |
| --- | --- | --- |
| P | Passed | Testfall erfolgreich ausgeführt |
| X | Failed gesamt | Abgeleitete Summe aus F, N und N? |
| F | Defect | Fehlgeschlagen und mit einem regulären AQUA Defect verknüpft |
| N | Noise | Fehlgeschlagen und mit einem als `NOISE` markierten AQUA Defect verknüpft |
| N? | Ungeklärt | Fehlgeschlagen, aber noch ohne verknüpften AQUA Defect |
| NE | Not Executed | Noch nicht ausgeführt, wartend oder eingeplant |

## Ergebnisbaum

Ordner und Testszenarien zeigen die aufsummierten Resultate ihrer untergeordneten Testfälle. Die
Kennungen von Testszenarien, Testfällen, Testausführungen und Defects sind direkt mit der jeweiligen
AQUA-Seite verlinkt. Erfolgreiche Testfälle werden je Szenario unter **Passed** gesammelt und können
gemeinsam ein- oder ausgeklappt werden.

![Ergebnisbaum mit Ordnern, Testszenarien, Testfällen und Statussummen](images/result-tree.png)

## Fehlgeschlagene Tests untersuchen

Mit **Nur X-Testfälle** blendet H2ORB erfolgreiche Testfälle aus und öffnet die Pfade zu den
fehlgeschlagenen Tests. Die Schalter **F**, **N** und **N?** grenzen die Anzeige anschließend auf die
gewünschte Fehlerklasse ein.

- **F** zeigt Testfälle mit regulärem AQUA Defect.
- **N** zeigt Testfälle mit einem Defect, dessen Bezeichnung den Marker `NOISE` enthält.
- **N?** zeigt fehlgeschlagene Testfälle, denen noch kein AQUA Defect zugeordnet ist.

![Fehlerfokus mit geöffneten Ausführungen und AQUA Defects](images/failure-filter.png)

## Zusammenfassung für den Bericht auswählen

Das gewählte Wurzelverzeichnis erscheint immer als hervorgehobenes Gesamtergebnis. Zusätzliche
Ordner lassen sich über die Kontrollkästchen in die Zusammenfassung aufnehmen. Die Auswahl ändert nur
den Report und nicht die berechneten Ergebnisse.

![Auswahl zusätzlicher Ordner für die Report-Zusammenfassung](images/summary-selection.png)

## Testabschlussbericht

Der Report enthält die Gesamtwerte und die optional ausgewählten Ordner. Im Detail erscheinen nur
fehlgeschlagene Tests mit Status, letzter Ausführung, verknüpftem AQUA Defect und dessen Beschreibung.
Alle Kennungen führen direkt zur passenden Seite in AQUA.

![Report-Vorschau mit Zusammenfassung und Fehlerdetails](images/report-preview.png)

## Installation mit pip

Python 3.12 oder neuer wird benötigt:

```powershell
py -m pip install h2orb
h2orb
```

Nach der Konfiguration der benötigten `ARB_`-Umgebungsvariablen ist H2ORB unter
<http://127.0.0.1:8000> erreichbar.

## Container starten

Zuerst eine lokale `.env` anhand von `.env.example` erstellen. Anschließend das veröffentlichte
`linux/amd64`-Image laden und starten:

```powershell
docker pull hrabovszki/h2orb:0.1.3
docker run --detach --name h2orb `
  --restart unless-stopped `
  --env-file .env `
  --env ARB_HOST=0.0.0.0 `
  --publish 8000:8000 `
  hrabovszki/h2orb:0.1.3
```

Für reproduzierbare Installationen sollte ein fester Versions- oder `sha-*`-Tag verwendet werden.
Aktuelle Befehle und Konfigurationsoptionen stehen in der [Projekt-README](../README.md#docker).

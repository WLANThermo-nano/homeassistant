# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.1.4-informational)
![Lizenz](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forums-lightgrey)](https://wlanthermo.de/forums/)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

> **Hinweis & Haftungsausschluss**
> Dies ist eine Community-Integration für WLANThermo.  
> **Kein Support** durch den Autor. Forks, Weiterentwicklung und Bugfixes sind willkommen. Alle frqagen könnt ihr im [WLANThermo Forum](https://wlanthermo.de/forums/)
 stellen.  
> **Keine Gewähr/Haftung** – Nutzung auf eigene Gefahr.


## Hinweis zur Dashboard-Nutzung
Um das mitgelieferte Dashboard (wlanthermo.yaml) zu verwenden, müssen folgende Frontend-Karten/Erweiterungen aus HACS installiert werden:

- Auto-Entities
- Button Card
- Mushroom
- ApexCharts Card
- Card Mod

Bitte installiere diese über HACS → Frontend, bevor du das Dashboard importierst oder verwendest.
Das Dashboard ist so dynamisch wie möglich gehalten. Es müssen aber ALLE vorkommen von `wlanthermo` mit dem richtigen Gerätenamen ersetzt werden.
z.B. `device_name: wlanthermo` → `device_name: nano_v3` oder `entity_id: sensor.wlanthermo_channel_*_temperatur` → `entity_id: sensor.nano_v3_channel_*_temperatur`

## Übersicht
Diese Integration verbindet Home Assistant mit einem WLANThermo (ESP32/Nano/Link/Mini). Sie liest Sensordaten und Pitmaster-Status aus und stellt diese als Entitäten bereit.

## Features
- Automatische Erkennung und Einrichtung über die Home Assistant-Oberfläche
- Temperatur-Sensoren für alle Kanäle (Name & Nummer)
- Pitmaster-Sensoren (z.B. Duty Cycle)
- Systeminformationen: RSSI, Batteriestatus, Ladevorgang
- Konfigurierbare Scan-Intervalle
- Unterstützung für verschiedene WLANThermo-Modelle
- Offline-toleranter Start (Entitäten werden verfügbar, sobald das Gerät online ist)
- Pitmaster-Kanal-Auswahl: Kanal für jeden Pitmaster anzeigen und wählen
- Dynamischer Cloud-Status-Sensor: zeigt immer den aktuellen Verbindungsstatus
- Verbesserte Übersetzungsunterstützung für alle Status- und Auswahlwerte
- Neuer Lichtsensor für die Farbauswahl
- Konfigurationsfluss und Optionsfluss für erweiterte Einstellungen
- Schalter zur Anzeige der Sensortemperatur als 999 oder nicht verfügbar

## API-Referenz
- Offizielle HTTP-API: https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP
- Routen **kleingeschrieben** verwenden (`/setpitmaster`, `/setchannels`, `/setpid`, `/setsystem`)
- Für Pitmaster-Writes: vollständige verschachtelte PM-Objekte im Array senden

## Manuelle Installation
1. Repository entpacken
2. `custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren
3. Home Assistant neu starten

## Installation über HACS

1. Öffne Home Assistant und gehe zu **Einstellungen → Geräte & Dienste → HACS**.
2. Wähle **Integrationen** und klicke oben rechts auf die drei Punkte (⋮) → **Benutzerdefiniertes Repository**.
3. Gib die URL dieses Repositories ein: `https://github.com/WLANThermo-nano/homeassistant` und wähle **Integration** als Typ.
4. Suche nach **WLANThermo** in HACS, installiere die Integration und starte Home Assistant neu.

## Einrichtung
1. Home Assistant öffnen
2. Einstellungen → Geräte & Dienste → **Integration hinzufügen** → **WLANThermo**
3. Host, Port und ggf. Pfad-Präfix angeben

## Einrichtung der Integration

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration hinzufügen**.
2. Suche nach **WLANThermo** und wähle sie aus.
3. Gib die IP-Adresse deines WLANThermo Geräts ein und ändere gegebenenfalls den Namen.
4. Schließe die Einrichtung ab und bestätige den Dialoge.

### Optionen für die Integration

Die Integration bietet einen Optionsfluss, mit dem Benutzer die folgenden Einstellungen anpassen können:

1. **IP Adresse:**
   - Kann angepasst werden, falls sich die interne IP ändert im Router.
   
2. **Scan-Intervall:**
   - Legen Sie fest, wie oft die Integration Daten vom WLANThermo-Gerät abruft.
   - Standardwert: 10 Sekunden.

3. **Anzeige der Sensortemperatur:**
   - Wählen Sie, ob die Sensortemperatur als `999` oder als `nicht verfügbar` angezeigt werden soll, wenn keine Daten vorliegen.

3. **Authentifizierung:**
   - Anpassen und Setzen der Authentifizierung, falls diese in der Weboberfläche nötig ist.

Diese Optionen können jederzeit über die Home Assistant-Oberfläche geändert werden:

1. Gehe zu **Einstellungen → Geräte & Dienste → Integration bearbeiten**.
2. Wähle den gewünschten Integrationseintrag aus.
3. Passe die Optionen im angezeigten Dialog an.

## Entitäten (Beispiele)
- **Pitmaster**: Duty Cycle, Kanal, PID-Status, Sollwert
- **Kanäle**: Temperatur, Alarm, Sensortyp, Min/Max, Restzeit (Time Left)
- **System**: RSSI, Batteriestatus, Ladevorgang
- **Lichtsensor**: Farbtemperatur, Helligkeit

### Sensor: Restzeit (Time Left)

Für jeden Temperaturkanal wird automatisch ein Sensor `channel_*_time_left` erstellt. Dieser zeigt die geschätzte verbleibende Zeit (in Minuten) an, bis die aktuelle Temperatur den eingestellten Zielwert (Max) erreicht.

**Berechnung:**
- Die Restzeit basiert auf dem Durchschnitt der Temperaturänderung der letzten Minuten (gleitendes Fenster).
- Die Formel lautet:

	Restzeit (min) = (Zieltemperatur - aktuelle Temperatur) / (Temperaturanstieg pro Minute)

- Wenn die Temperatur stagniert oder sinkt, wird 0 angezeigt.
- Ist der Kanal nicht verbunden oder keine Daten vorhanden, bleibt der Sensor leer.

**Anwendungsfall:**
- Praktisch für Grill- oder Garvorgänge, um abzuschätzen, wann das Grillgut fertig ist.

## Konfiguration
Die Integration nutzt einen Konfigurationsdialog (Config Flow). Es sind keine manuellen YAML-Einträge notwendig.

## Entwicklung & Beiträge
Pull Requests, Fehlerberichte und Feature-Wünsche sind willkommen!

### Sensor: Kanalfarbe (Schalter)

Für jeden Kanal wird automatisch ein Sensor `light.wlanthermo_channel_*_color` erstellt. Dieser ist eigentlich eine Lampe, wird hier aber genutzt, um einen Farbwähler für die Kanalfarbe zu haben.

**Achtung:**
- Der Sensor kann nur auf eingesteckte Kanäle/Sensoren verwendet werden.
- Der Wert ist gleich zum Textfeld
- Ausschalten, Helligkeit und der Schalter haben keine Funktion.
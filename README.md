# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.3.0-informational)
![Lizenz](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2025%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forum-lightgrey)](https://wlanthermo.de/forums/)
![Owner](https://img.shields.io/badge/code%20owner-@MStapelfeldt-purple)

---

## Hinweis & Haftungsausschluss

Dies ist eine **Community-Integration** für WLANThermo Geräte.  
Es besteht **kein offizieller Support** durch den Autor oder das WLANThermo-Team.

- Forks, Weiterentwicklungen und Bugfixes sind willkommen  
- Fragen & Diskussionen bitte im  
  👉 **[WLANThermo Forum](https://wlanthermo.de/forums/)**

⚠️ **Keine Gewähr / Nutzung auf eigene Gefahr**

---

## Übersicht

Diese Integration verbindet Home Assistant mit **WLANThermo Geräten**  

Sie liest Sensordaten, Systemstatus und Pitmaster-Informationen aus und stellt diese als native Home-Assistant-Entitäten bereit.

Die Integration ist **vollständig UI-basiert**, YAML ist nicht erforderlich.

### Kompatibilität

Diese Integration wurde erfolgreich getestet mit:

- WLANThermo Nano V1+, V3
- WLANThermo Mini V2 ESP32, V3
- WLANThermo Link V1
- Home Assistant 2026.1.0 und neuer

Andere Modelle und Firmware-Versionen könnten ebenfalls funktionieren, sind aber nicht getestet.

---

## Features

- 🔍 Automatische Erkennung & Einrichtung über die HA-Oberfläche
- 🌡️ Temperatur-Sensoren dynamisch für alle Kanäle (Name & Nummer)
- 🎛️ Pitmaster-Sensoren dynamisch (Leistung, Temperatur, Modus, PID, Kanal)
- ⏱️ Restzeit-Sensor pro aktivem Kanal
- ✉️ Konfiguration von Beanchrichtigungen über Pushover und Telegram
- 📶 Bluetooth Temperatur-Sensoren Konfiguration
- ☁️ Cloud-Sensoren 
- 🔋 Systemdiagnose:
  - WLAN-RSSI
  - Batteriestand
  - Ladezustand
- 🎨 Kanalfarben
- 🌍 Vollständige Übersetzungsunterstützung (DE / EN)
- ⚙️ Konfigurierbares Scan-Intervall
- 🔌 Offline-toleranter Start (Entitäten erscheinen automatisch)
- 🔄 Options-Flow für erweiterte Einstellungen
- 👻 Option: Inaktive Sensoren als *unavailable* anzeigen

---

## Dashboard (optional)

Für das im Repository vorhandene Beispiel-Dashboard `wlanthermo.yaml` werden folgende Frontend-Erweiterungen benötigt (über **HACS → Frontend**):

- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) (`auto-entities`)
- [Button Card](https://github.com/custom-cards/button-card) (`button-card`)
- [Mushroom](https://github.com/piitaya/lovelace-mushroom) (`Mushroom`)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (`apexcharts-card`)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) (`card-mod`)
- [Browser Mod](https://github.com/thomasloven/hass-browser_mod) (`browser-mod`)

**Wichtig:**  
Alle Vorkommen von `wlanthermo` müssen auf deinen Gerätenamen angepasst werden.
Alle Entitätsnamen sind auf deutsch hinterlegt. Für englische Namen, könnte ihr `wlanthermo_en.yaml`.

Beispiel:
```yaml
device_name: wlanthermo → nano_v3
sensor.wlanthermo_kanal_*_temperature → sensor.nano_v3_kanal_*_temperature
sensor.wlanthermo_kanal_*_temperature → sensor.nano_v3_channel_*_temperature

```

---

## Installation über HACS (empfohlen)

1. Öffne Home Assistant und gehe zu  
   **Menü → HACS** (deine_HA_URL/hacs/dashboard)
2. Klicke oben rechts auf die drei Punkte (⋮) → **Benutzerdefiniertes Repository**
3. Gib folgende URL ein: `https://github.com/WLANThermo-nano/homeassistant` Typ: **Integration**
4. Suche anschließend nach **WLANThermo**
5. Installiere die Integration
6. Starte Home Assistant neu

## Manuelle Installation

1. Repository herunterladen oder entpacken
2. Ordner  `custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren
3. Home Assistant neu starten

---

## Einrichtung

1. Home Assistant öffnen
2. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
3. **WLANThermo** auswählen
4. Gerätenamen eingeben (sollte einzigartig sein)
5. IP-Adresse / Host, Port und optionales Pfad-Präfix angeben
6. `Inaktive Sensoren als nicht verfügbar anzeigen` regelt ob Temperaturen als `999` anzeigt werden oder **nicht verfügbar** sind
7. Falls Authentificierung nötig ist, diese einschalten und Benutzername/Passwort eingeben
8. Einrichtung abschließen

---

## Optionen der Integration

Die Optionen erreichst du über:

**Einstellungen → Geräte & Dienste → WLANThermo → Optionen/Zahnrad**

- **IP-Adresse / Port / Präfix**  
  Kann angepasst werden, falls sich die IP im Router ändert oder Einstellungen sich geändert haben
- **Scan-Intervall**  
  Legt fest, wie oft Daten vom WLANThermo abgerufen werden  
  Standard: **10 Sekunden**
- **Inaktive Sensoren als nicht verfügbar anzeigen**  
  regelt ob Temperaturen als `999` anzeigt werden oder **nicht verfügbar** sind
- **Authentifizierung**  
  Benutzername / Passwort, falls in der Weboberfläche aktiviert

---

## Entitäten in HA

### Kanäle
- Sensoren
  - Temperatur
  - [Restzeit](#sensor-restzeit)
- Steuerelemente
  - Alarmmodus
  - Sensortyp
  - Min / Max
- Konfiguration
  - Name
  - Farbe
  
### Pitmaster
- Sensoren
  - Leistung (%)
  - Temperatur
- Steuerelemente
  - Zugewiesener Kanal
  - Modus (Auto / Manuell / Aus)
  - PID-Profil
  - Solltemperatur

### Pit Profil
- Konfiguration
  - Name
  - Aktor
  - Min / Max PWM (SSR / FAN / DAMPER)
  - Min / Max Servo Puls (SERVO / DAMPER)
  - Startleistung
  - Aktor Verknüpfung (DAMPER)
  - Deckelerkennung

### System
- Diagnose
  - WLAN-RSSI
  - Batteriestand
  - Ladezustand
  - Cloud-Status
  - Cloud-URL
  - und andere  
    Geräte- & Systeminformationen

### Benachrichtigungen
- Konfiguration
  - Benachrichtigungen Aktivieren (Telegram/Pushover)
  - Token Eingabe (Telegram/Pushover)
  - User Key / Chat ID (Telegram/Pushover)
  - Nachrichtenpriorität festlegen  (Pushover)
  - Testmessage senden (Telegram/Pushover)

### Bluetooth
- Konfiguration
  - Bluetooth Aktivieren
  - Auswahl der übertragenden Kanäle  

**Wichtig:** Nach Änderungen an den Bluetooth-Einstellungen muss die Integration neu gestartet werden, damit BT-Sensoren erkannt werden.  
Nutze dazu die Schaltfläche „Integration neu starten“ in der Systemdiagnose.

---

## Sensor: Restzeit

Für jeden Temperaturkanal wird automatisch ein Sensor  
`kanal_*_restzeit` erstellt.

Berechnung:
- Basierend auf dem Durchschnitt der Temperaturänderung
- Gleitendes Zeitfenster (mehrere Minuten)

Formel:
```
Restzeit (min) =
(Zieltemperatur – aktuelle Temperatur) / Temperaturanstieg pro Minute
```

Verhalten
- Sinkende oder stagnierende Temperatur → **0 Minuten**
- Nicht verbundene Kanäle → **kein Wert**

Ideal für Grill- & Garprozesse 🔥

## Konfiguration Benachrichtigungen  

Um Telegram oder Pushover ein zu richten sind Token und Chat ID/User key nötig. Wie ihr diese einrichtet könnt ihr unter [Push-Notification](https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/Push-Notification) nachlesen.  
Nur wenn beide Textfelder ausgefüllt sind, könnt ihr die Benachrichtigung testen.

---

## API-Hinweise

- Offizielle HTTP-API: (Nano V1(+) sind fast gleich.)  
  https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/HTTP

---

## Entwicklung & Beiträge

Pull Requests, Bugreports und Feature-Wünsche sind willkommen ❤️  
Bitte möglichst mit Logs und klarer Fehlerbeschreibung.

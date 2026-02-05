
# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.3.0-informational)
![Lizenz](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/HA-2025.12%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forum-lightgrey)](https://wlanthermo.de/forums/)
![Maintainer](https://img.shields.io/badge/maintainer-@MStapelfeldt-informational)
![Owner](https://img.shields.io/badge/code%20owner-@sochs-purple)

---

## Hinweis & Haftungsausschluss

Dies ist eine **Community-Integration** für WLANThermo Geräte.  
Es besteht **kein offizieller Support** durch den Autor oder das WLANThermo-Team.

- Forks, Weiterentwicklungen und Bugfixes sind willkommen  
- Fragen & Diskussionen bitte im  
  👉 **[WLANThermo Forum](https://wlanthermo.de/forums/)**

⚠️ **Keine Gewähr / Nutzung auf eigene Gefahr**

---

## Dokumentation & Wiki

Ausführliche Informationen findest du in der [deutschen Wiki](https://github.com/WLANThermo-nano/homeassistant/wiki) oder [englischen Wiki](https://github.com/WLANThermo-nano/homeassistant/wiki/Home-en).

---

## Kurzüberblick

Diese Integration verbindet Home Assistant mit **WLANThermo Geräten** und stellt Sensordaten, Systemstatus und Pitmaster-Informationen als native Home-Assistant-Entitäten bereit.

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
- 👻 Option: Inaktive Sensoren als *unavailable* anzeigen

---

## Dashboard (optional)

Das Beispiel‑Dashboard `wlanthermo.yaml` ist optional und dient als Vorlage.  

[Dashboard Erklärung](https://github.com/WLANThermo-nano/homeassistant/wiki/dashboard)

---

## Installation

[Installation](docs/de/setup.md)
über HACS (empfohlen):  
**Benutzerdefiniertes Repository**: `https://github.com/WLANThermo-nano/homeassistant`  
manuell:  
`custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren

---

## Einrichtung

[Einrichtung](https://github.com/WLANThermo-nano/homeassistant/wiki/Einrichtung#einrichtung)  
1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. **WLANThermo** auswählen
3. IP-Adresse / Host angeben
4. OK drücken

---

## Optionen der Integration

Die Optionen erreichst du über:

**Einstellungen → Geräte & Dienste → WLANThermo → Optionen/Zahnrad**
[Optionen](https://github.com/WLANThermo-nano/homeassistant/wiki/Einrichtung#optionen-der-integration)

---

## Entitäten in HA

👉 Alle Entitäten im Detail findest du in der Wiki:  
[Entitäten & Sensoren](https://github.com/WLANThermo-nano/homeassistant/wiki/entities)

## Entwicklung

[Entwicklung](https://github.com/WLANThermo-nano/homeassistant/wiki/development)

## WIKI
- [FAQ](https://github.com/WLANThermo-nano/homeassistant/wiki/faq)
- [Troubleshooting](https://github.com/WLANThermo-nano/homeassistant/wiki/troubleshooting)
- [API Hinweise](https://github.com/WLANThermo-nano/homeassistant/wiki/api)

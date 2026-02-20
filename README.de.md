
# WLANThermo – Home Assistant Integration

![Version](https://img.shields.io/badge/version-0.3.1-informational)
![Lizenz](https://img.shields.io/badge/license-MIT-green)
![Home Assistant](https://img.shields.io/badge/HA-2025.12%2B-blue)
[![Support](https://img.shields.io/badge/support-WLANThermo%20Forum-lightgrey)](https://wlanthermo.de/forums/)
![Maintainer](https://img.shields.io/badge/maintainer-@MStapelfeldt-informational)
![Owner](https://img.shields.io/badge/code%20owner-@sochs-purple)

---

# Readme in english at [README.md](https://github.com/WLANThermo-nano/homeassistant/blob/master/README.md)

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
- 🛰️ Einrichtung IoT Felder
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

Wiki: [Dashboard Erklärung](https://github.com/WLANThermo-nano/homeassistant/wiki/dashboard)  
Das Beispiel‑Dashboard `wlanthermo.yaml` ist optional und dient als Vorlage.  


---

## Installation

Wiki: [Installation](docs/de/setup.md)  
über HACS (empfohlen):  
[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=sochs&repository=https%3A%2F%2Fgithub.com%2FWLANThermo-nano%2Fhomeassistant&category=Integration)  
**Benutzerdefiniertes Repository**: `https://github.com/WLANThermo-nano/homeassistant`  
manuell:  
`custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren

---

## Einrichtung

Wiki: [Einrichtung](https://github.com/WLANThermo-nano/homeassistant/wiki/Einrichtung#einrichtung)  
1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. **WLANThermo** auswählen
3. IP-Adresse / Host angeben
4. OK drücken

---

## Optionen der Integration

Wiki: [Optionen](https://github.com/WLANThermo-nano/homeassistant/wiki/Einrichtung#optionen-der-integration)  

Die Optionen erreichst du über:  
**Einstellungen → Geräte & Dienste → WLANThermo → Optionen/Zahnrad**  

---

## Entitäten in HA

👉 Alle Entitäten im Detail findest du in der Wiki: [Entitäten & Sensoren](https://github.com/WLANThermo-nano/homeassistant/wiki/entities)  

## Entwicklung


Wiki: [Entwicklung](https://github.com/WLANThermo-nano/homeassistant/wiki/development)  

## WIKI
- [FAQ](https://github.com/WLANThermo-nano/homeassistant/wiki/faq)  
- [Troubleshooting](https://github.com/WLANThermo-nano/homeassistant/wiki/troubleshooting)  
- [API Hinweise](https://github.com/WLANThermo-nano/homeassistant/wiki/api)  

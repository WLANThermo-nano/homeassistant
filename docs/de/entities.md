# Entitäten & Sensoren

Hier werden die von der Integration bereitgestellten Entitäten und Sensoren beschrieben.

### Kanäle
- Sensoren
	- Temperatur
	- Restzeit
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

## Entitäten
Alle Entitäten sind in 4 verschiedene Kategorien unterteilt:  
- Steuerelemente  
- Sensoren  
- Konfiguration  
- Diagonse  

### Steuerelemente
Dienen dazu Einstellungen, die gängig sind an zu passen.
- Alarmmodus - Alle Känale mit Temnperatursensor eingesteckt/verbunden oder 999°C  
  Hier kann gewählt werden ob man Per Buzzer, Push oder beides Benachrichtigt wird.  
  Für Push muss vorher die Pushbenachrichtigung aktiviert und konfiguriert sein.
- Maximum / Minimum - Alle Känale mit Temnperatursensor eingesteckt/verbunden oder 999°C  
- Sensortyp - Alle Känale mit Temnperatursensor die nicht "fixed" sind (kein Bluetooth und K-Typ)  
- Pitmaster Kanal - Mapping vom Pitmaster zu Temperatur, nur eingesteckte Sensoren möglich (kein Bluetooth)
  Sollte hier ein Kanal als "   " oder "unknown" auftauchen, Bitte Kanalnamen neu eingeben s.h. [Konfiguration](konfiguration)
- Pitmaster Leistung - Nur wenn der Modus auf manuell gesetzt ist  
- Pitmaster Modus - Auto (regulierung durch temperatur), Manuell (regulierung durch Leistung) oder aus  
- Pitmaster Temperatur - Nur wenn der Modus auf auto gesetzt ist  

### Sensoren
Lassen sich nur auslesen, nicht einstellen.
- Kanal Temperatur - Zeigt Temperatur an, wenn eingesteckt oder 999°C Wenn "Inaktive Sensoren als nicht verfügbar anzeigen" aktiviert ist  
  Bei jeder Temperatur ist in den Attributen die Kanalnummer versteckt  
- Kanal Restzeit - Wird aus den aktiven Sensoren Berechnet, solange Temperatur steigt  
- Pitmaster Leistung - Zeigt im auto Modus, wie schnell sich der Lüfter gerade dreht (Prozent) sonst nicht verfügbar  
- Pitmaster Temperatur - Spiegelt die Temperatur des aktuellen Kanals.
  Wenn als Pit Kanal auf 1 steht, ist die Pit Temperatur = Kanal 1 Temperatur
Wichtig zu wissen ist:  
Wenn Bluetooth Sensoren angeschlossen wurden, müssen diese einmalig initialisiert werden. Hierzu ist es nötig die Bluetooth Kanäle zu aktivieren und Integration neu zu starten.

### Konfiguration  
Sind alle einstellungen, die man nicht so häufig ändern/anpassen muss.  
- Kanalfarbe - Kann in der Weboberfläche und bei Graphen genutzt werden um Temperaturen zu unterscheiden.  
  Hier wird ein "Umweg" über eine Licht-Entität verwendet. Dies hat den Vorteil, dass man eine Farbe einfach setzen und auswählen kann, allerdings gibt es leider Einstellungen wie Helligkeit und An/Aus, die nicht berücksichtigt werden.
- Kanalname - Kann geändert werden, um Kanäle zu benennen. Hier kann es passieren, dass Namen als Unknown oder "   " erscheinen, was daran liegt, dass sie im Gerät selbst nicht definiert wurden. Einfach einmal neu Benennen.
- Bluetooth Einstellungen lassen sich über Schalter ein und aus schalten. Hierbei ist wichtig zu wissen, dass die Integration evtl. Mehrmals neu gestartet werden muss. Best Practice:  
  Bluetooth aktiv einschalten -> Integration neu starten  
  Bluetooth *** (dies ist der Name vom BT Device (z.B. Meater, kann nicht geändert werden) + letzten 6 stellen der Mac-Adresse) Fühler 1 - X aktivieren  
  (nach umschalten 5 Sekunden warten, weil die Einstellung erst gesendet wird) -> Integration neu starten  
  Nun sind die Fühler unter Kanal X verfügbar  
- Pid Profileinstellungen - Hier lassen sich genaue Einstellungen der Pit Profile vornehmen (aber nicht alles).  
  Name - Recht einfach, das Kind braucht nen Namen, damit ihr wisst, was ihr gerade ein stellt.  
  Jedes Profil lässt sich mit einem "Aktor" verknüpfen, der auch die Einstellungen beeinflusst:  
  - SSR - Solid State Relay oder Gleichstromrelay/Transistor  
  - FAN - Ventilator  
  - SERVO - Motor welcher über PWM eingestellt wird  
  - DAMPER - Lüftungsregelung  
   PWM Minimum/Maximum ist nur für SSR, Fan und Damper  
   Servo Minimum/Maximum ist nur für Servo und Damper  
   Startleistung kann noch mal bestimmen, mit welcher Maximalleistung beim Starten des Grills angefangen werden soll. Dies ist nützlich um z.B. bei 100% ein zu schnelles aufheizen und damit übersteuerung/überhitzung zu vermeiden  
   Aktor-Verknüpfung kann bei Damper genutzt werden um zwischen Aktoren zu verknüpfen  
   Deckelerkennung gibt an, ob schnelle Temperaturstürze als "offener Deckel" erkannt werden und so evtl der Lüfter kurz pausiert wird, statt gegen zu regeln  
- Push einstellungen - Reflektieren die Webeinstellungen für Benachrichtigungen. Seht hierbei bitte in die [WlanThermo Wiki](https://github.com/WLANThermo-nano/WLANThermo_ESP32_Software/wiki/Push-Notification).  
  Testen fünktioniert nur, wenn Token und ChatID/UserKey hinterlegt sind 

  
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
- Die Berechnung ist bewusst geglättet, um Sprünge zu vermeiden.

Ideal für Grill- & Garprozesse 🔥
---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)

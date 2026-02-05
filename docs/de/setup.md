# Setup & Installation

## Installation über HACS (empfohlen)

1. Öffne Home Assistant und gehe zu  
	 **Menü → HACS** (deine_HA_URL/hacs/dashboard)
2. Klicke oben rechts auf die drei Punkte (⋮) → **Benutzerdefiniertes Repository**
3. Gib folgende URL ein: `https://github.com/WLANThermo-nano/homeassistant` Typ: **Integration**
4. Suche anschließend nach **WLANThermo**  
	 Falls HACS das Repository nicht sofort anzeigt, kurz den Browser aktualisieren.
5. Installiere die Integration
6. Starte Home Assistant neu

## Manuelle Installation

1. Repository herunterladen oder entpacken
2. Ordner  `custom_components/wlanthermo` nach `<HA config>/custom_components/` kopieren
3. Home Assistant neu starten

## Einrichtung
1. **Einstellungen → Geräte & Dienste → Integration hinzufügen**
2. **WLANThermo** suchen und auswählen
3. Im Fester was auf geht, muss man seinen WLANThermo konfigurieren.  
   - Zuerst einen Gerätenamen eingeben oder WLANThermo auch einfach lassen.  
     Wichtig hierbei ist: Solltet ihr 2 oder mehr Geräte haben, wählt individuelle namen, weil es sonst schwierig wird, die richtigen Sensoren für jedes Gerät zu finden.  
     Sensornamen setzen sich immer aus Gerätenamen_Kanal_*_* (oder ähnlich) zusammen.  
   - Host/IP ist die Adresse, die Ihr im Browser (Chrome/Safari/IE/Firefox) nutzt um auf die Weboberfläche zu kommen. Zum Beispiel 192.168.178.101 -> http:// ist nicht nötig.
   - Standardmäßig ist der Port immer 80, solltet Ihr also wahrscheinlich so stehen lassen können.
   - Wenn ihr keine Änderungen an der API Konfiguration durchgeführt habt, dann ist das Präfix / auch richtig -> Nicht ändern.
   - Standartmäßig sendet der Wlanthermo nicht angeschlossene Känale mit der Temperatur 999°C. Die Integration erkennt dies und setzt sie automatisch auf "Nicht verfügbar".
     Solltet ihr den Schalter Ausschalten, werden die Sensoren mit der Temperatur 999.0 im Frontend angezeigt.
   - Manche Geräte erfordern eine Authentifizierung um Einstellungen ändern zu können.  
     Wenn ihr euch nicht sicher seid, öffnet ein Inkognitofenster im Browser, editiert dort Einstellungen im Wlanthermo und versucht zu speichern. Wenn Ihr dabei einen Benutzernamen und Passwort eingeben müsst, gebt diese in die Felder ein und legt den Schalter bei "Authentifizierung erforderlich" um.
4. Einrichtung abschließen indem Ihr auf OK drückt
5. Danach seht Ihr einen Integrationseintrag, mit einem Gerät, der Versionsnummer und weit über 100 Sensoren.


## Optionen der Integration

Die Optionen erreichst du über:

**Einstellungen → Geräte & Dienste → WLANThermo → Optionen/Zahnrad**

- Der Gerätename lässt sich NICHT ändern. möchtet ihr dies tun, müsst ihr das Gerät löschen und neu hinzufügen.
- **IP-Adresse / Port / Präfix**  
	Kann angepasst werden, falls sich die IP im Router ändert oder Einstellungen sich geändert haben
- **Scan-Intervall**  
	Legt fest, wie oft Daten vom WLANThermo abgerufen werden  
	Standartmäßig fragt die integration alle **10 Sekunden** nach neuen Werten, für Temperatur ect. Solltet ihr öfters neue Werte wollen, könnt ihr dies unter Scan-Intervall einstellen.  
      Bitte bedenkt, zu kurze Intervalle (1 Sekunde) erfordern viel Rechenleistung für die Integration und verlangsamt euer Netzwerk und Home Asssistant.  
- **Inaktive Sensoren als nicht verfügbar anzeigen**  
	regelt ob Temperaturen als `999` anzeigt werden oder **nicht verfügbar** sind
- **Authentifizierung**  
	Benutzername / Passwort, falls in der Weboberfläche aktiviert

---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)

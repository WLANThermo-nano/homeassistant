# Dashboard Beispiele

Das Beispiel‑Dashboard `wlanthermo.yaml` / `wlanthermo_en.yaml` ist optional und dient als Vorlage.  
Hierfür werden folgende Frontend-Erweiterungen benötigt (über **HACS → Frontend**):

- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) (`auto-entities`)
- [Button Card](https://github.com/custom-cards/button-card) (`button-card`)
- [Mushroom](https://github.com/piitaya/lovelace-mushroom) (`Mushroom`)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (`apexcharts-card`)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) (`card-mod`)
- [Browser Mod](https://github.com/thomasloven/hass-browser_mod) (`browser-mod`)

Zur Anpassung von diesem oder eigener Erstellung hier ein paar Tips:
- Zur erstellung von Einträgen pro Sensor, nutze ich `button_card_templates`. Dies hat den Vorteil, dass ich nur ein mal Code schreiben muss und der für 1-XX Kanäle übernommen wird. Sehr effizient funktioniert das in Kombination mit `Auto-Entities`:
```YAML
- type: custom:auto-entities
  card:
    type: grid
    columns: 8
    square: false
  filter:
    include:
    - entity_id: sensor.wlanthermo_kanal_*_temperatur
        options:
        type: custom:button-card
        template: wlt_kanal_button
    exclude:
    - state: unavailable
    - state: unknown
  sort:
    method: entity_id
  card_param: cards
```
Hier baue ich mir also ein 8er Grid (8 Karten nebeneinander, mehr in Reihe 2-x) zusammen, welche alle Entitäten vom Typ `sensor.wlanthermo_kanal_*_temperatur` (* als "irgendeine Zahl") beinhalten, die nicht (`exlude`) `unavailable` oder `unknown` sind. Diese zeige ich in der `custom:button-card` mit template `wlt_kanal_button` an.  
Das Template hingegen wird ganz oben definiert und darunter auch mit werten gefüllt:
```
    name: |
      [[[
        const id = entity.entity_id.match(/kanal_(\d+)_/)[1];
        const temp = entity.state !== 'unavailable' ? entity.state + "°C" : "N/A";
        return "Kanal " + id + "  " + temp;
      ]]]
    custom_fields:
      restzeit: |
        [[[ 
          const id = entity.entity_id.match(/kanal_(\d+)_/)[1];
          const dev = variables.device_name;
          const tl = states[`sensor.${dev}_kanal_${id}_restzeit`];
          return tl.state != 0 ? `Restzeit: ${tl.state}` : "Restzeit: ~ ";
        ]]]
      minmax: |
        [[[
          const id = entity.entity_id.match(/kanal_(\d+)_/)[1];
          const dev = variables.device_name;
          const min = states[`number.${dev}_kanal_${id}_minimum`]?.state;
          const max = states[`number.${dev}_kanal_${id}_maximum`]?.state;
          return `
            <div style="
              display:flex;
              align-items:center;
              justify-content:space-between;
              width:100%;
              font-size:13px;
            ">
              <span style="display:flex; align-items:center; gap:4px;">
                <ha-icon icon="mdi:chevron-down"style="--mdc-icon-size:14px;"></ha-icon>
                ${min}°C
              </span>
              <span style="display:flex; align-items:center; gap:4px;">
                <ha-icon icon="mdi:chevron-up"style="--mdc-icon-size:14px;"></ha-icon>
                ${max}°C
              </span>
            </div>
          `;
        ]]]
```
Hier wird der Kachelname auf Kanal * und Temperatur gesetzt, sowie zusätzliche Felder mit Restzeit und min/max gestaltet.  
Weiter unten sagen wir dann noch, was passieren soll, wenn man auf die Karte tippt, wo wir über Platzhalter die einzelnen Entitäten anzeigen:
```
    tap_action:
      action: fire-dom-event
      browser_mod:
        service: browser_mod.popup
        data:
          content:
            type: entities
            entities:
              ...
              - |
                [[[
                  const id = entity.entity_id.match(/kanal_(\d+)_/)[1];
                  const dev = variables.device_name;
                  return `text.${dev}_kanal_${id}_name`;
                ]]]
              ...
```
Wie ihr hier auch erkennt, wird über eine Variable `device_name` der Entityname zusammen gebastelt. Diese ist ganz oben in der Karte hinterlegt und muss geändert werden, falls euer device nicht `wlanthermo` heißt.  
Beispiel:
```yaml
device_name: wlanthermo → nano_v3  
sensor.wlanthermo_kanal_*_temperature → sensor.nano_v3_kanal_*_temperature  
```

---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)

# Dashboard Examples

The sample dashboard `wlanthermo.yaml` / `wlanthermo_en.yaml` is optional and serves as a template.  
The following frontend extensions are required (via **HACS → Frontend**):

- [Auto-Entities](https://github.com/thomasloven/lovelace-auto-entities) (`auto-entities`)
- [Button Card](https://github.com/custom-cards/button-card) (`button-card`)
- [Mushroom](https://github.com/piitaya/lovelace-mushroom) (`Mushroom`)
- [ApexCharts Card](https://github.com/RomRider/apexcharts-card) (`apexcharts-card`)
- [Card Mod](https://github.com/thomasloven/lovelace-card-mod) (`card-mod`)
- [Browser Mod](https://github.com/thomasloven/hass-browser_mod) (`browser-mod`)

Tips for customizing or creating your own:
- For creating entries per sensor, I use `button_card_templates`. This allows me to write code once and use it for 1-XX channels. Very efficient in combination with `Auto-Entities`:
```YAML
- type: custom:auto-entities
  card:
    type: grid
    columns: 8
    square: false
  filter:
    include:
    - entity_id: sensor.wlanthermo_channel_*_temperature
      options:
        type: custom:button-card
        template: wlt_channel_button
    exclude:
    - state: unavailable
    - state: unknown
  sort:
    method: entity_id
  card_param: cards
```
This builds an 8-column grid (8 cards per row, more in rows 2-x) showing all entities of type `sensor.wlanthermo_channel_*_temperature` (* as "any number") that are not (`exclude`) `unavailable` or `unknown`. These are displayed in the `custom:button-card` with template `wlt_channel_button`.
The template is defined at the top and filled with values below:
```
    name: |
      [[[
        const id = entity.entity_id.match(/channel_(\d+)_/)[1];
        const temp = entity.state !== 'unavailable' ? entity.state + "°C" : "N/A";
        return "Channel " + id + "  " + temp;
      ]]]
    custom_fields:
      remaining_time: |
        [[[ 
          const id = entity.entity_id.match(/channel_(\d+)_/)[1];
          const dev = variables.device_name;
          const tl = states[`sensor.${dev}_channel_${id}_remaining_time`];
          return tl.state != 0 ? `Remaining: ${tl.state}` : "Remaining: ~ ";
        ]]]
      minmax: |
        [[[
          const id = entity.entity_id.match(/channel_(\d+)_/)[1];
          const dev = variables.device_name;
          const min = states[`number.${dev}_channel_${id}_minimum`]?.state;
          const max = states[`number.${dev}_channel_${id}_maximum`]?.state;
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
This sets the card name to Channel * and temperature, and adds extra fields for remaining time and min/max.  
Further down, you can define what happens when you tap the card, using placeholders to show individual entities:
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
                  const id = entity.entity_id.match(/channel_(\d+)_/)[1];
                  const dev = variables.device_name;
                  return `text.${dev}_channel_${id}_name`;
                ]]]
              ...
```
As you can see, the entity name is built using a `device_name` variable, which is set at the top of the card and must be changed if your device is not called `wlanthermo`.
Example:
```yaml
device_name: wlanthermo → nano_v3  
sensor.wlanthermo_channel_*_temperature → sensor.nano_v3_channel_*_temperature  
```

---
[🇩🇪 Deutsch](../de/README.md) | [🇬🇧 English](../en/README.md)
```
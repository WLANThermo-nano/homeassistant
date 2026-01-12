# Changelog

## [0.1.1] - 2026-01-09

### Added
- New "Time Left" sensor for each channel, estimating minutes until target temperature is reached.
- Translations and documentation for the new sensor (README, en/de).
- Improved dashboard YAML formatting guidance.

### Fixed
- Various translation and grouping issues.
- YAML and documentation formatting.

## 0.1.0 – Initial version

- First public release of the WLANThermo BBQ integration for Home Assistant.

### Features
- System, channel, and pitmaster sensors with dynamic translation (English and German).
- Channel temperature, min/max, and alarm sensors with proper entity naming and translation.
- Pitmaster value sensor and select entity for direct control and monitoring.
- Device info, cloud link, and update sensors.
- Select, number, and text entities for channel and pitmaster configuration.
- Config flow with authentication options (username/password, optional requirement).
- All entities grouped under the main device for a clean Home Assistant UI.
- HACS and Home Assistant manifest support.
- Full support for Home Assistant 2025.1.0+.

### Improvements
- Consistent use of translation_key and translation_placeholders for all dynamic entity names.
- Sensors and entities now use correct EntityCategory (SENSOR, DIAGNOSTIC, CONFIG).
- Improved device_info attachment for all entities, ensuring proper grouping.

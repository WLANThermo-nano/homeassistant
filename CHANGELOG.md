# Changelog

## [0.1.4] - 2026-01-16

### Added
- Dashboard to Display all sensors 

## [0.1.3] - 2026-01-15

### Fixed
- Sensors now correctly become unavailable and available after device reboot or offline events.
- Improved device grouping for all sensors, including cloud and diagnostic sensors.

### Changed
- Refactored `available` property logic for all relevant sensors.
- Consistent `device_info` property for all entities.
- Add Pitmaster Temp sensor 

## [0.1.2] - 2026-01-13

### Added
- New light sensor for color picking.
- Options flow for advanced settings, including scan interval and authentication.
- Switch to display sensor temperature as 999 or unavailable.
- Updated documentation (README, en/de) to reflect new features.

### Improved
- Enhanced translation support for all status and selection values.
- Better handling of offline devices during startup.

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

## [Unreleased] - 2026-01-21

### Changed
- Merged major updates from `dev` branch:
  - Entity IDs and dashboard references updated from `channel` to `kanal` and from `value` to `leistung` for pitmasters.
  - Cloud URL entity now uses `sensor.wlanthermo_cloud_url_2`.
  - Button card templates and dashboard YAML updated for new entity names and improved translation/icon support.
  - Various fixes for translation, icons, and dashboard consistency.


# Changelog

## [0.3.1] - 2026-02-06

### Added
- Edit fields for IoT settings and synchronization with device.

## [0.3.0] - 2026-02-05

### Added
- Notification settings to configuration.
- Reload Integration button to discover new Bluetooth sensors.
- Bluetooth handling and related integration features.
- Channel temperature attribute ID for automatic entity sorting.
- New PID profile fields in configuration.

### Changed
- Updated dashboards for Bluetooth and notifications.
- Improved code quality across multiple components.
- Improved switch entity naming to avoid duplicate names.
- Updated channel naming in configuration files.
- Updated and extended translations (English and German).

### Fixed
- Fixed priority availability on Pushover notifications.
- Fixed test icon for Telegram.
- Fixed and extended translation issues.
- Fixed setting name in text entity.

## [0.2.3] - 2026-01-27

### Added
- Modularized entity platforms: PID profile entities are now split into text, number, and switch platforms for better maintainability.
- Dynamic entity creation for all PID profile fields (name, aktor, opl, jp, DCmmin, DCmmax, SPmin, SPmax, link) using Home Assistant’s Text, Number, and Switch platforms.
- Listeners and entity_store tracking for all platforms to support dynamic updates and robust entity management.

### Changed
- Improved code structure, comments, and separation of concerns for easier future development.
- Enhanced data models and ensured all PIDConfig fields are used for entity creation.

### Fixed
- Various minor bugs and inconsistencies in entity registration and update logic.

## [0.2.2] - 2026-01-23

### Added
- New sensor attributes and extended language options
- Improved support for Mini/Nano V1(+)
- Additional debug and logging options

### Changed
- Dashboard layout and entities optimized for English names
- Improved error handling for API and authentication
- Optimized configuration and options flow
- Improved mapping and display of entities

### Removed
- Removed outdated or duplicate entity names and unnecessary debug outputs

## [0.2.1] - 2026-01-21

### Changed
- Improved sensor and attribute structure for better performance and clarity.
- Optimized translations for German and English languages.
- Updated dashboard layout and styling for a more intuitive user experience.
- Various bug fixes and minor optimizations throughout the integration.
- Enhanced compatibility and stability across different Home Assistant setups.

## [0.2.0] - 2026-01-21

### Changed
- Complete rewrite of the DataUpdateCoordinator and entity handling for improved performance, maintainability and reliability.
- Major refactor of all sensor, binary_sensor, and entity classes for clarity and extensibility.
- Adjusted and improved translation files and translation keys for better multi-language support.
- Updated and streamlined `__init__.py` and `config_flow.py` for a more robust integration setup and configuration experience.
- Improved dashboard YAML and entity naming to match new structure and translation logic.
- Numerous bugfixes and code cleanups throughout the integration.

### Removed
- Legacy entity and coordinator logic, replaced by new architecture.

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

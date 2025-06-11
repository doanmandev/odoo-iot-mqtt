# MQTT Listener Module Documentation
## Overview
**mqtt_listener** is an Odoo module that integrates MQTT event listening and handling into your Odoo system. This module provides a service (`mqtt.service`) that connects to an MQTT broker, processes incoming messages, and automatically manages the lifecycle of the MQTT service (start/stop) when the module is installed or uninstalled on any active Odoo database.
## Features
- Seamless MQTT client integration into Odoo.
- Automatically starts or stops the MQTT service when the module is installed or uninstalled on all active Odoo databases.
- Robust support for multi-database environments.
- Detailed logging of service actions and errors.
- Lifecycle management via Odoo hooks.

## Installation
1. Download this module and extract it into your Odoo directory. `addons`
2. Ensure any required Python dependencies (such as `paho-mqtt`, if used) are installed in your Odoo environment.
3. Install the module from the Odoo Apps menu or via the command line:
``` shell
   odoo -u mqtt_listener
```
## Usage
- **Automatic service management:**
The MQTT service will automatically start on all databases after module installation and stop upon uninstallation.
- **Manual control:**
You can manually start or stop the MQTT service by calling:
``` python
  env['mqtt.service'].start_mqtt_service()
  env['mqtt.service'].stop_mqtt_service()
```
- **Message handling:**
Custom logic for processing MQTT messages should be defined in the `mqtt.service` model implementation.

## Hooks
- `_post_init_hook(env)`: Starts the MQTT service right after the module is installed on a database.
- `_auto_start_mqtt()`: Ensures the MQTT service starts on each active database after the module is installed.
- `_uninstall_hook(env)`: Stops the MQTT service on all databases when the module is uninstalled.

## Module Structure
``` 
mqtt_listener/
├── __init__.py
├── __manifest__.py
├── models/
│   └── mqtt_service.py
├── controllers/
├── tools/
...
```
- The main service model is defined in `models/mqtt_service.py`.

## Logging & Debugging
- All service lifecycle actions and errors are logged using Odoo’s logger under the name `odoo.addons.mqtt_listener`.
- If you encounter logs like `'mqtt.service' not present in environment for database ...`, it means the service/model is not available in that database (e.g., the module may not be installed).

## Requirements
- Compatible Odoo version (see module manifest for details).
- Python MQTT client (such as `paho-mqtt`) installed, if required by your implementation.
- An MQTT broker accessible by your Odoo server (local network or Internet).

## License
See `__manifest__.py` for details.


## Integration with Other Odoo Modules

The MQTT Listener is designed to integrate with other modules by:

- Storing messages in `mqtt.publish.signal.history` which can be processed by other modules
- Saving MQTT v5 user properties in `mqtt.user.property` for auditing
- Using the Odoo registry and environment system for thread-safe database operations
- Implementing a daemon thread that respects Odoo's lifecycle

## Security Configuration

- Credentials for broker connections are stored in the Odoo database
- Username and password authentication with the broker is supported
- The service uses SUPERUSER_ID for database operations to ensure proper access rights

## Deployment Instructions

1. Install Python dependencies: `pip install paho-mqtt`
2. Add the module to your Odoo addons path
3. Install the module through Odoo's module installation interface
4. Configure MQTT broker details in the Odoo interface
5. Start the service using the provided buttons in the UI

## Best Practices

- **Performance Optimization:**
  - Use specific topic subscriptions rather than wildcards when possible
  - Set appropriate QoS levels based on message importance
  - Monitor thread activity and message processing times

- **Error Handling:**
  - Implement custom error handling for specific message types
  - Use try/except blocks when processing messages
  - Log errors with sufficient context for debugging

- **Resource Management:**
  - Monitor the number of concurrent connections
  - Be aware of memory usage when storing large messages
  - Implement message retention policies for database storage

## Debugging and Monitoring

- **Activity Tracking:**
  The module tracks activity timestamps to detect inactivity:
  ```python
  inactive_time = time.time() - self._last_activity
  if inactive_time > 60:  # If no activity for 60 seconds
      _logger.warning(f"No MQTT activity for {inactive_time:.0f} seconds, checking connection...")
  ```

- **Logging:**
  The module implements comprehensive logging at different levels:
  ```python
  # Enable MQTT client logging
  self.client.enable_logger(_logger)
  ```

- **Status Checking:**
  Regular status checks through the `check_mqtt_status()` method provide real-time information about the service.

> ⚠️ **Note: This module is under development, so there are some limitations as follows:**
> - The first time you install, this module will take the default topics as `mqtt/test` to run, 
so it will not receive a signal, so you have to stop and restart the service.
> - Currently, when restarting odoo, you need to check and restart the service of this module

## References

1. [Paho MQTT Python Documentation](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
2. [MQTT Protocol Specification](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
3. [Odoo Development Documentation](https://www.odoo.com/documentation/16.0/developer.html)
4. [Threading in Python](https://docs.python.org/3/library/threading.html)

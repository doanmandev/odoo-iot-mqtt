# odoo-iot-mqtt
A comprehensive solution for IoT (Internet of Things) communication between MQTT technology and Odoo platform.

# Odoo IOT MQTT
Seamless connectivity between Odoo and IoT devices through the MQTT protocol.

## Overview
The Odoo IoT MQTT module provides a robust integration between Odoo ERP and IoT devices using the MQTT protocol. This solution bridges the gap between Odoo's business logic and IoT devices, sensors, machinery, and other M2M (Machine-to-Machine) systems.

### Key Features
- **MQTT Broker Management**: Configure and manage multiple MQTT broker connections
- **Real-time MQTT Listening**: Receive and process messages from IoT devices
- **Signal Sending**: Send MQTT signals to control remote devices
- **Comprehensive Message History**: Track and store all sent/received messages
- **Automatic Reconnection**: Robust reconnection mechanism with exponential backoff
- **Service Management**: Control MQTT services through the Odoo interface

## Installation
### Requirements
- Odoo 16.0
- Python 3.8+
- paho-mqtt library

### Library Installation
```bash
pip install paho-mqtt
```

### Module Installation
1. Copy the `mqtt_integration` and `mqtt_listener` directories to the Odoo addons path 
2. Update the app list in Odoo
3. Find and install the "MQTT Integration" module from the app list

## Configuration
### Setting up MQTT Broker
1. Navigate to **MQTT > Configuration > Brokers**
2. Create a new broker connection with details:
    - Broker name
    - URL scheme (MQTT or WS)
    - Host address
    - Port (default: 1883)
    - Client ID (auto-generated)
    - Username/password (if required)
    - Keepalive and timeout settings
3. Use the "Check Connection" button to verify connectivity

### Managing Subscriptions
1. Navigate to **MQTT > Configuration > Subscriptions**
2. Create a new subscription with details:
    - Select a configured broker
    - Define a topic (supports wildcards)
    - Set QoS level (0, 1, or 2)
    - Configure additional flags (No Local, Retain as Published, etc.)
3. Use the "Subscribe" button to activate the subscription

### Starting the MQTT Service
1. Navigate to **MQTT > Control > Status**
2. Click the "Start Service" button to begin listening for MQTT messages
3. Monitor the connection status and service information

## System Architecture
The solution consists of two complementary modules:

### 1. MQTT Integration (`mqtt_integration`)
- Provides models for broker connections, subscriptions, and signal management
- Handles the configuration of MQTT connections
- Manages signal sending through the `mqtt.signal` model
- Stores message history in the `mqtt.signal.history` model

### 2. MQTT Listener (`mqtt_listener`)
- Implements a background service (`mqtt.service`) that runs as a daemon thread
- Manages persistent connections to MQTT brokers
- Automatically reconnects with exponential backoff on connection loss
- Processes incoming messages and stores them in the database

## Models and Components

### MQTT Integration Models
- **MQTT Broker** (`mqtt.broker`): Stores broker configurations
- **MQTT Subscription** (`mqtt.subscription`): Manages topic subscriptions
- **MQTT Signal** (`mqtt.signal`): Sends messages to MQTT topics
- **MQTT Signal History** (`mqtt.signal.history`): Records message history

### MQTT Listener Components
- **MQTT Service** (`mqtt.service`): Manages the listener lifecycle
- **MQTTListener Thread**: Background thread that maintains MQTT connections

## Usage
### Sending MQTT Messages
```python
# Example of sending a message from Odoo code
def send_command(self):
    signal = self.env['mqtt.signal'].create({
        'broker_id': self.broker_id.id,
        'subscription_id': self.subscription_id.id,
        'payload': '{"command": "turn_on"}',
        'qos': 1,
        'retain': False
    })
    signal.action_send_mqtt()
```

### Checking the MQTT Service Status
```python
# Check if the MQTT service is running and connected
status = self.env['mqtt.service'].check_mqtt_status()
# Returns: {'status': 'connected', 'message': 'MQTT Service is connected and running'}
```

### Querying Message History
```python
# Example of querying recent messages
messages = self.env['mqtt.signal.history'].search([
    ('direction', '=', 'receive'),
    ('topic', 'like', 'sensors/%')
], limit=10, order='timestamp desc')
```

## Advanced Features

### Thread Management
The module carefully manages MQTT listener threads using a global dictionary:
```python
# Inside mqtt_service.py
MQTT_THREADS[thread_id] = listener_thread
```

### Error Handling and Reconnection
The listener implements an advanced reconnection mechanism:
- Initial reconnect delay: 5 seconds
- Maximum reconnect delay: 300 seconds (5 minutes)
- Exponential backoff: Delay increases by a factor of 1.5 after each failed attempt

### Customization
You can extend the listener with custom message handling logic by modifying the `on_message` method.

## Best Practices
- Use unique client IDs for each broker connection
- Set appropriate QoS levels based on your application's needs
- Implement proper error handling when processing messages
- Use specific topic subscriptions rather than broad wildcards when possible
- Regularly monitor connection status and message history

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Create a Pull Request

## License
This module is distributed under the LGPL-3.0 license. See the `LICENSE` file for more details.

## Contact
- Author: Doan Man
- Email: doanman.dev@gmail.com

**Note**: This module is under active development and subject to change. Contributions and bug reports are always welcome!

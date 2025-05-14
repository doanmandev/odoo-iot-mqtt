# MQTT Integration Documentation

### Part 1: Document Summary
### Part 2: Details

# Part 1
## Document Summary

This document provides a comprehensive guide to the MQTT Integration interface in Odoo.

It includes:
- Introduction to the purpose and design of the MQTT Integration module
- System architecture and data flow
- Detailed API with code examples
- Guide to managing MQTT threads
- How to store and process MQTT messages
- Error handling and reconnect mechanisms
- Integration with other Odoo modules
- Security configuration
- Deployment instructions
- Best practices
- Debugging and performance monitoring guidelines

This document helps developers understand how to use and extend the MQTT Integration for IoT applications and system integration in Odoo.

# Part 2
## Introduction

MQTT Integration is an abstraction layer providing a unified interface for MQTT communication within the Odoo system.  
This module acts as a bridge between Odoo and IoT devices or external services, enabling real-time data exchange via the MQTT protocol.

## Design Purpose

- **Object-Oriented Abstraction:** Encapsulates the complexity of MQTT communication.
- **Extensibility:** Easily add new MQTT brokers and message formats.
- **System Integration:** Provides a unified framework for other modules to use MQTT.
- **State Management:** Monitors and manages MQTT connections throughout the application lifecycle.

## System Architecture

### Main Components

#### 1. MQTT Broker (`mqtt.broker`)
- Stores MQTT broker configurations (host, port, credentials, etc.)
- Provides connection testing (`action_check_connection`)
- Tracks connection status and messages

#### 2. MQTT Subscription (`mqtt.subscription`)
- Manages subscriptions to MQTT topics
- Handles subscription status and allows subscribing via `subscribe_mqtt`
- Tracks broker, topic, QoS, and subscription state

#### 3. MQTT Signal (`mqtt.signal`)
- Represents messages to be sent to MQTT topics
- Linked to a broker and a subscription
- Allows sending messages via `action_send_mqtt`
- Stores payload, QoS, retain flag, and send time

#### 4. MQTT Signal History (`mqtt.signal.history`)
- Stores history of sent and received messages
- Tracks signal, payload, topic, QoS, retain, direction (send/receive), and timestamp

## Data Flow

1. **Broker Configuration:**  
   Users define one or more MQTT brokers (`mqtt.broker`).

2. **Subscription Management:**  
   Users create subscriptions (`mqtt.subscription`) to topics on a broker.

3. **Message Sending:**  
   Users create and send signals (`mqtt.signal`) to a topic. Each sent message is logged in history (`mqtt.signal.history`).

4. **Message Receiving:**  
   Subscribed topics can receive messages, which are also logged in history.

## Models and Fields

### MQTT Broker (`mqtt.broker`)
| Field             | Type      | Description                              |
|-------------------|-----------|------------------------------------------|
| name              | Char      | Broker Name                              |
| url_scheme        | Selection | URI scheme (e.g., mqtt://, ws://)        |
| host              | Char      | Hostname or IP address                   |
| port              | Char      | Connection port                          |
| client_id         | Char      | Unique client ID                         |
| username          | Char      | Username for authentication              |
| password          | Char      | Password for authentication              |
| keepalive         | Integer   | Keepalive interval (seconds)             |
| connect_timeout   | Integer   | Connection timeout (seconds)             |
| note              | Text      | Notes                                    |
| connection_message| Char      | Last connection message                  |
| connection_status | Selection | Connection status (unknown/success/fail) |

**Key Method:**  
- `action_check_connection`: Checks connectivity to the configured MQTT broker.

---

### MQTT Subscription (`mqtt.subscription`)
| Field                     | Type      | Description                                  |
|---------------------------|-----------|----------------------------------------------|
| broker_id                 | Many2one  | Linked MQTT broker                           |
| topic                     | Char      | Topic to subscribe to                        |
| qos                       | Integer   | Quality of Service                           |
| no_local_flag             | Boolean   | No local flag                                |
| retain_as_published_flag  | Boolean   | Retain as published flag                     |
| retain_handling           | Integer   | Retain handling option                       |
| subscribed                | Boolean   | Subscription status                          |
| subscription_time         | Datetime  | Time of subscription                         |
| display_name              | Char      | Computed display name                        |
| subscription_in_progress  | Boolean   | Is subscription in progress                  |
| subscription_status       | Selection | Subscription status (subscribed, etc.)       |

**Key Method:**  
- `subscribe_mqtt`: Subscribes to the specified topic on the broker.

---

### MQTT Signal (`mqtt.signal`)
| Field         | Type      | Description                                  |
|---------------|-----------|----------------------------------------------|
| broker_id     | Many2one  | Linked MQTT broker                           |
| subscription_id| Many2one | Linked MQTT subscription                     |
| history_ids   | One2many  | Related signal history records               |
| topic         | Char      | Topic (related to subscription)              |
| payload       | Text      | Message payload                              |
| retain        | Boolean   | Retain flag                                  |
| qos           | Integer   | Quality of Service                           |
| send_at       | Datetime  | Time sent                                    |
| display_name  | Char      | Computed display name                        |

**Key Method:**  
- `action_send_mqtt`: Sends a message to the broker/topic and records the event in history.

---

### MQTT Signal History (`mqtt.signal.history`)
| Field       | Type      | Description                                  |
|-------------|-----------|----------------------------------------------|
| signal_id   | Many2one  | Linked MQTT signal                           |
| payload     | Text      | Message payload                              |
| topic       | Char      | Topic                                        |
| qos         | Integer   | Quality of Service                           |
| retain      | Boolean   | Retain flag                                  |
| direction   | Selection | Direction (send/receive)                     |
| timestamp   | Datetime  | Time of message                              |
| display_name| Char      | Computed display name                        |

---

## Example Usage

### 1. Check Broker Connection

```python
broker = env['mqtt.broker'].browse(broker_id)
broker.action_check_connection()
```

### 2. Subscribe to a Topic

```python
subscription = env['mqtt.subscription'].browse(subscription_id)
subscription.subscribe_mqtt()
```

### 3. Send an MQTT Signal

```python
signal = env['mqtt.signal'].create({
    'broker_id': broker_id,
    'subscription_id': subscription_id,
    'payload': 'Hello MQTT!',
    'qos': 0,
    'retain': False,
})
signal.action_send_mqtt()
```

## Error Handling and Reconnection

- All connection and subscription errors are handled with descriptive messages using Odoo's `UserError`.
- Connection status and messages are tracked in the broker and subscription models.
- Subscription and sending methods include try/catch blocks for robust error handling.

## Integration with Other Odoo Modules

- All models inherit from `mail.thread` and `mail.activity.mixin` for full integration with Odoo’s communication and activity tracking features.
- The design allows easy extension for custom IoT or business logic.

## Security Configuration

- Credentials and connection information are securely stored in the `mqtt.broker` model.
- TLS/SSL can be configured for secure communication (extend the broker model as needed).

## Deployment Instructions

1. Install Python dependencies (e.g., `paho-mqtt`).
2. Add the module to your Odoo `custom_addons` directory.
3. Update your Odoo configuration and restart the server.
4. Configure your MQTT brokers and subscriptions in the Odoo UI.

## Best Practices

- Use unique client IDs for each broker.
- Set appropriate QoS and retain flags for your use case.
- Regularly check connection status.
- Secure your broker credentials and use TLS/SSL if possible.
- Use Odoo's access control and logging for traceability.

## Debugging and Monitoring

- Use the connection status and message history fields for troubleshooting.
- Leverage Odoo’s logging and activity tracking for performance monitoring.
- Review the `mqtt.signal.history` for a log of all MQTT messages sent/received.


## References
1. [Paho MQTT Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
2. [MQTT v5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
3. [Odoo Documentation](https://www.odoo.com/documentation)
4. [IoT Protocols](https://iot.eclipse.org/community/resources/iot-protocols/)

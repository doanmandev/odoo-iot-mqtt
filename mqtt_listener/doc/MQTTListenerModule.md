# MQTT Listener Module Documentation

### Part 1: Document Summary
### Part 2: Details

# Part 1
## Document Summary

This document provides a comprehensive guide to the MQTT Listener module for Odoo.

It includes:
- Introduction and purpose of the MQTT Listener module
- System architecture and components
- Detailed API with code examples
- Thread management and service lifecycle
- Message handling and storage
- Error handling and reconnection mechanisms
- Integration with other Odoo modules
- Security configuration
- Deployment instructions
- Best practices
- Debugging and monitoring guidelines

This documentation helps developers understand how to use and extend the MQTT Listener for real-time IoT applications and system integration in Odoo.

# Part 2
## Introduction

The MQTT Listener module is an implementation that provides a background service for subscribing to and listening for MQTT messages in Odoo. It creates a dedicated thread that maintains a persistent connection to an MQTT broker, receives messages from configured topics, and stores them in the Odoo database.

## Design Purpose

- **Background Processing:** Runs in a separate daemon thread to avoid blocking Odoo's main process.
- **Automatic Reconnection:** Implements exponential backoff for reconnecting to the broker in case of connection loss.
- **Message Persistence:** Stores all received messages in the database for auditing and processing.
- **Service Management:** Provides a clean API for starting, stopping, and monitoring the MQTT service.

## System Architecture

### Main Components

#### 1. MQTT Service (`mqtt.service`)
- Manages the lifecycle of the MQTT listener service
- Provides API for starting, stopping, and checking service status
- Stores service information and thread identifiers

#### 2. MQTTListener Thread
- Implements a daemon thread that connects to the MQTT broker
- Handles message receipt via callback methods
- Manages automatic reconnection with exponential backoff
- Processes and stores incoming messages

#### 3. Message History Storage
- Uses `mqtt.signal.history` to store message history
- Records topic, payload, QoS, direction, and timestamps

## Data Flow

1. **Service Initialization:**  
   The `mqtt.service` model starts an MQTTListener thread to handle MQTT communications.

2. **Connection Establishment:**  
   The thread connects to the configured MQTT broker and subscribes to topics.

3. **Message Handling:**  
   Incoming messages trigger the `on_message` callback, which processes and stores them.

4. **Reconnection:**  
   If the connection is lost, the thread automatically attempts to reconnect with exponential backoff.

## Models and Fields

### MQTT Service (`mqtt.service`)
| Field            | Type      | Description                                  |
|------------------|-----------|----------------------------------------------|
| name             | Char      | Service name (default: 'MQTT Listener Service') |
| last_start       | Datetime  | Last service start time                      |
| status           | Selection | Service status (start/stop/error)            |
| thread_identifier| Char      | Thread identifier for the running thread     |
| host_info        | Char      | Host system information (computed)           |
| connection_status| Selection | Connection status (connected/connecting/disconnected/unknown) |

**Key Methods:**
- `start_mqtt_service()`: Starts the MQTT listener thread
- `stop_mqtt_service()`: Safely stops the listener thread
- `check_mqtt_status()`: Checks current service and connection status
- `restart_mqtt_service()`: Restarts the service

## Example Usage

### 1. Start the MQTT Listener Service

```python
env['mqtt.service'].start_mqtt_service()
```

### 2. Check Service Status

```python
status = env['mqtt.service'].check_mqtt_status()
# Returns: {'status': 'connected', 'message': 'MQTT Service is connected and running'}
```

### 3. Stop the Service

```python
env['mqtt.service'].stop_mqtt_service()
```

## Thread Management

The module manages MQTT threads using a global dictionary `MQTT_THREADS` which stores references to all active threads. This enables:

1. **Thread Tracking:**
   ```python
   # Inside mqtt_service.py
   MQTT_THREADS[thread_id] = listener_thread
   ```

2. **Safe Thread Stopping:**
   ```python
   # When stopping a thread
   thread.stop()
   thread.join(timeout=5)
   del MQTT_THREADS[thread_id]
   ```

## Message Handling

When a message is received by the listener, it follows this process:

```python
def on_message(self, client, userdata, msg, properties=None):
    # Update activity timestamp
    self._last_activity = time.time()
    
    # Log message receipt
    _logger.info(f"Received message on {msg.topic}: {msg.payload.decode()}")
    
    try:
        # Create a new cursor to interact with database
        with self.registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            
            # Create history record
            env['mqtt.signal.history'].create({
                'topic': msg.topic,
                'message_id': False,
                'payload': msg.payload.decode(errors='ignore'),
                'qos': msg.qos,
                'direction': 'receive',
                'retain': msg.retain,
            })
            
            cr.commit()
    except Exception as e:
        _logger.error(f"Error processing MQTT message: {e}", exc_info=True)
```

## Error Handling and Reconnection

The listener implements an advanced reconnection mechanism with exponential backoff:

- Initial reconnect delay: 5 seconds
- Maximum reconnect delay: 300 seconds (5 minutes)
- Exponential backoff: Delay increases by a factor of 1.5 after each failed attempt

```python
# Reconnection logic in MQTTListener.run()
if not self._connected:
    try:
        # Connection attempt
        self.client.connect_async(self.broker, int(self.port), keepalive)
        # If connection fails
        self._current_delay = min(self._current_delay * 1.5, self._max_reconnect_delay)
    except Exception:
        # Increase delay for next attempt
        self._current_delay = min(self._current_delay * 1.5, self._max_reconnect_delay)
```

## Integration with Other Odoo Modules

The MQTT Listener is designed to integrate with other modules by:

- Storing messages in `mqtt.signal.history` which can be processed by other modules
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

## References

1. [Paho MQTT Python Documentation](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
2. [MQTT Protocol Specification](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
3. [Odoo Development Documentation](https://www.odoo.com/documentation/16.0/developer.html)
4. [Threading in Python](https://docs.python.org/3/library/threading.html)

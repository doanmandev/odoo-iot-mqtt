# 🚀 Odoo IoT MQTT Integration

Seamless integration between **Odoo ERP** and **IoT devices** using the **MQTT protocol**.

![Odoo + MQTT](https://plctab.com/wp-content/uploads/2021/08/mqtt.jpg) <!-- Huynh có thể thay bằng ảnh minh họa repo -->

---

## 🔍 Overview

This module enables **real-time, bidirectional communication** between Odoo and IoT systems via MQTT, allowing your ERP to interact with sensors, controllers, and smart devices.

### ✅ Key Features

* 🔌 **Multiple MQTT Broker Management**
* 📡 **Real-Time Subscription & Listener**
* 📤 **Send Signals to IoT Devices**
* 🕒 **Message Logging & History**
* ♻️ **Automatic Reconnection with Backoff**
* ⚙️ **Control MQTT Services from UI**

---

## 🧱 Architecture

This solution consists of two tightly integrated Odoo modules:

| Module             | Responsibilities                                          |
| ------------------ | --------------------------------------------------------- |
| `mqtt_integration` | Broker setup, signal sending, message history             |
| `mqtt_listener`    | Background service, realtime listener, reconnection logic |

## 📦 Module Overviews

### `mqtt_integration`
Handles broker configuration, subscription management, and sending MQTT signals from Odoo. All messages are logged in `mqtt.signal.history`.

### `mqtt_listener`
Runs a background listener service that subscribes to topics, performs automatic reconnection, and records incoming messages in `mqtt.signal.history`.

---

## ⚙️ Installation

### Requirements

* Odoo **16.0**
* Python **3.8+**
* MQTT client library: `paho-mqtt`

### Steps

```bash
pip install paho-mqtt
```

1. Copy `mqtt_integration/` and `mqtt_listener/` to your Odoo `addons` directory.
2. Restart Odoo and update app list.
3. Install **"MQTT Integration"** from the Apps menu.

---

## 🔧 Configuration

### 1. Configure MQTT Broker

* Go to **MQTT > Configuration > Broker**
* Fill in details (host, port, user, pass,...)
* Use **Check Connection** to validate

### 2. Create Subscriptions

* Navigate to **MQTT > Configuration > Subscriptions**
* Define topics and QoS settings
* Click **Subscribe** to activate

### 3. Start Listener Service

* Navigate to **MQTT > Configuration > Service**
* Click **Start Service** to activate background listener

---

## 🖠️ Usage Examples

### 🔹 Send MQTT Signal

```python
self.env['mqtt.signal'].create({
    'broker_id': self.broker_id.id,
    'subscription_id': self.subscription_id.id,
    'payload': '{"command": "turn_on"}',
    'qos': 1,
}).action_send_mqtt()
```

### 🔹 Check Service Status

```python
status = self.env['mqtt.service'].check_mqtt_status()
# Output: {'status': 'connected', 'message': 'MQTT Service is connected and running'}
```

### 🔹 Query Message History

```python
messages = self.env['mqtt.signal.history'].search([
    ('direction', '=', 'receive'),
    ('topic', 'like', 'sensors/%')
], limit=10, order='timestamp desc')
```

---

## 🧠 Advanced Features

* 🔀 **Exponential Backoff Reconnection**
* 🧵 **Thread-Safe Listener Management**
* ⚠️ **Robust Error Handling**
* 🔄 **Customizable Message Handlers**

---

## ✅ Best Practices

* Use **unique client IDs** per broker
* Avoid wildcard topics in production
* Use appropriate **QoS levels**
* Monitor **connection health and logs**
* Handle exceptions when processing payloads

---

## 🤝 Contributing

We welcome your ideas and improvements!

```bash
# Steps to contribute
1. Fork this repository
2. Create a new branch
3. Make your changes
4. Submit a Pull Request 🚀
```

---

## 📄 License

Licensed under the **LGPL-3.0**. See [LICENSE](./LICENSE) for details.

---

## 🤛 Contact

* **Author**: Doan Man
* 📧 **Email**: [doanman.dev@gmail.com](mailto:doanman.dev@gmail.com)

> ⚠️ *Note: This module is under active development. Feedback, bug reports, and PRs are highly appreciated!*

---

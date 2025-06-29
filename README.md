# 🚀 Odoo IoT MQTT Integration

Seamless integration between **Odoo ERP** and **IoT devices** using the **MQTT protocol**.

![Odoo + MQTT](https://plctab.com/wp-content/uploads/2021/08/mqtt.jpg)

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
* 🔖 **MQTT v5 User Properties**
---

## 🧱 Architecture

This solution consists of two tightly integrated Odoo modules:

**Module:** `mqtt_integration`

**Responsibilities:** Broker setup, topic sending, message history, Background service, realtime listener, reconnection logic.

---

## ⚙️ Installation

### Requirements

* Odoo **16.0+**
* Python **3.8+**
* MQTT client library: `paho-mqtt`

### Steps

```bash
pip install paho-mqtt
```

1. Copy `mqtt_integration/` to your Odoo `custom addons` directory.
2. Restart Odoo and update the app list.
3. Install **"MQTT Integration"** from the Apps menu.

---

## 🔧 Configuration

### 1. Configure MQTT Broker

* Go to **MQTT Machine > MQTT Configuration > Broker**
* Fill in details (url_scheme, host, port, user, pass,...)
* Use **Connect** and **Start Listener** **Button**

### 2. Create Topics

* Navigate to **MQTT Machine> MQTT Configuration > Topics**
* Define **Topic**
* Choose **Broker**
* Click **Confirm** to activate

### 3. Create Subscriptions

* Navigate to **MQTT Machine> MQTT Configuration > Subscriptions**
* Define **Subscription** and **valid payload**
* Choose **Broker**, **Topic** and **Allow User Property** (_if necessary_)
* Click **Subscribe** to activate

### 4. Create Metadata (User Properties) _(if necessary)_

* Navigate to **MQTT Machine> MQTT Configuration > User Properties/Metadata**
* Define **properties** and **value properties**
* Choose **Topic** (_if necessary_). 
* (choose Topic: This is part of helping to know which topic this properties data belongs to.)

## 🖠️ Usage WorkFlow

### 🔹 Define Broker, Topic, Subscription
### 🔹 Check/Submit to Broker, Topic, Subscription
### 🔹 Publish Message
### 🔹 Query Message History

---

## 🧠 Advanced Features

* 🔀 **Exponential Backoff Reconnection**
* 🧵 **Thread-Safe Listener Management**
* ⚠️ **Robust Error Handling**
* 🔄 **Customizable Message Handlers**
* 🗒️ **Store MQTT User Properties**
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

Licensed under the **GPL-3.0**. See [LICENSE](./LICENSE) for details.

---

## 🤛 Contact

* **Author**: Doan Man
* 📧 **Email**: [doanman.dev@gmail.com](mailto:doanman.dev@gmail.com)

> ⚠️ *Note: This module is under active development. Feedback, bug reports, and PRs are highly appreciated!*

---

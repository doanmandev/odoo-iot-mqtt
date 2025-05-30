# -*- coding: utf-8 -*-
{
    'name' : 'MQTT Integration',
    'version': '0.1.0',
    'summary' : 'Technical Module for MQTT',
    'description': """
MQTT Integration for Odoo
====================
Integrates MQTT protocol into Odoo for connecting with IoT devices and MQTT services.

Features:
- Manage connections to MQTT Brokers
- Subscribe/monitor MQTT topics
- Send and receive MQTT signals
- Store communication history
- Support automatic signal transmission

Applications:
- IoT device monitoring
- Sensor data collection
- Integration with automation systems

Requirements: paho-mqtt
    """,
    'category': 'Extra Tools',
    'author' : 'Doan Man',
    'website': 'http://www.init.vn/',
    'depends' : ['base', 'mail'],
    'external_dependencies': {
        'python': ['paho']
    },
    'images' : [
        'static/description/banner.png',
        'static/description/mqtt_architecture.png',
        'static/description/mqtt_features.png',
        'static/description/mqtt_interface.png',

    ],
    'data' : [
        'security/ir.model.access.csv',
        'views/mqtt_broker_views.xml',
        'views/mqtt_subscription_views.xml',
        'views/mqtt_signal_views.xml',
        'views/mqtt_signal_history_views.xml',
        'views/mqtt_signal_views.xml',
        'data/cron.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'assets': {
    },
    'license': 'LGPL-3',
}
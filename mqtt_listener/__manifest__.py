# -*- coding: utf-8 -*-
{
    'name' : 'MQTT listener',
    'version': '0.1.0',
    'summary' : 'Technical Module for MQTT',
    'description': """
MQTT Listener Service for Odoo
====================
Background service that maintains persistent MQTT connections and processes incoming messages.

Features:
- Runs as a background thread within the Odoo server
- Auto-reconnects to MQTT brokers with exponential backoff
- Automatically subscribes to configured topics
- Stores received messages in the database
- Connection health monitoring with automatic recovery
- Auto-starts on server boot

Benefits:
- Real-time data collection without manual intervention
- Reliable connection management with failure handling
- Seamless integration with mqtt_integration module
- Low resource consumption with efficient threading

Requirements: paho-mqtt, mqtt_integration
    """,
    'category': 'Extra Tools',
    'author' : 'Doan Man',
    'website': 'http://www.init.vn/',
    'depends' : ['base', 'mail', 'mqtt_integration'],
    'external_dependencies': {
        'python': ['paho']
    },
    'images' : [],
    'data' : [
        'security/ir.model.access.csv',
        'views/mqtt_service_views.xml',
        'data/mqtt_cron.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '_post_init_hook',
    'uninstall_hook': '_uninstall_hook',
    'post_load': '_auto_start_mqtt',
    'assets': {},
    'license': 'GPL-3',
}
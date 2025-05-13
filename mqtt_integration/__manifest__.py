# -*- coding: utf-8 -*-
{
    'name' : 'MQTT Integration',
    'summary' : 'Technical Module for MQTT',
    'author' : 'Doan Man',
    'depends' : ['base', 'mail'],
    'version' : '0.1.0',
    'license' : 'LGPL-3',
    'data' : [
        'security/ir.model.access.csv',
        'views/mqtt_broker_connection_views.xml',
        'views/mqtt_subscription_views.xml',
        'views/mqtt_message_views.xml',
        'views/mqtt_message_history_views.xml',
    ],
    'category' : 'Extra Tools',
    "external_dependencies": {
        'python': ['paho']
    },
    'images' : [
        'static/description/banner.png',
        'static/description/mqtt_architecture.png',
        'static/description/mqtt_features.png',
        'static/description/mqtt_interface.png',

    ],
    'installable': True,
    'application': True
}
# -*- coding: utf-8 -*-
{
    'name' : 'MQTT listener',
    'summary' : 'Technical Module for MQTT',
    'author' : 'Doan Man',
    'depends' : ['base', 'mail', 'mqtt_integration'],
    'version' : '0.1.0',
    'license' : 'LGPL-3',
    'data' : [
        'security/ir.model.access.csv',
        'views/mqtt_service_views.xml',
        'data/mqtt_cron.xml',
    ],
    'category' : 'Extra Tools',
    "external_dependencies": {
        'python': ['paho']
    },
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '_post_init_hook',
    'uninstall_hook': '_uninstall_hook',
    'post_load': '_auto_start_mqtt',
}
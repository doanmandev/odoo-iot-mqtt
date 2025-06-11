# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import tools
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

import logging

_logger = logging.getLogger(__name__)

# Get a list of active databases
registries = Registry.registries.d


def _post_init_hook(env):
    """Hook runs after the first module installation"""
    env['mqtt.service'].start_mqtt_service()


def _uninstall_hook(env):
    """Function to stop MQTT when Odoo starts"""
    """Hook runs before module uninstall"""
    # For each database, try starting the MQTT service
    for db_name, registry_obj in registries.items():
        try:
            with registry_obj.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                if 'mqtt.service' in env:
                    _logger.info(f"Auto-starting MQTT service for database {db_name}")
                    env['mqtt.service'].stop_mqtt_service()
                    cr.commit()
        except Exception as e:
            _logger.error(f"Unable to start MQTT service for database {db_name}: {e}")


def _auto_start_mqtt():
    """Function to start MQTT when Odoo starts"""
    """Hook runs after module installation"""
    # For each database, try starting the MQTT service
    for db_name, registry_obj in registries.items():
        try:
            with registry_obj.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                if 'mqtt.service' in env:
                    _logger.info(f"Auto-starting MQTT service for database {db_name}")
                    env['mqtt.service'].start_mqtt_service()
                    cr.commit()
        except Exception as e:
            _logger.error(f"Unable to start MQTT service for database {db_name}: {e}")

# -*- coding: utf-8 -*-
import atexit
import logging
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)

def stop_mqtt_on_shutdown():
    """Hàm được gọi khi Odoo tắt"""
    _logger.info("Shutting down Odoo, stopping MQTT service...")
    
    # Lặp qua tất cả các database đang hoạt động
    registries = Registry.registries.d
    for db_name, registry_obj in registries.items():
        try:
            with registry_obj.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                if 'mqtt.service' in env:
                    _logger.info(f"Stopping MQTT service for database {db_name}")
                    env['mqtt.service'].stop_mqtt_service()
                    cr.commit()
        except Exception as e:
            _logger.error(f"Error stopping MQTT service for database {db_name}: {e}")

# Đăng ký hàm dừng MQTT khi Odoo thoát
atexit.register(stop_mqtt_on_shutdown)
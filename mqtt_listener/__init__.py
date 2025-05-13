# -*- coding: utf-8 -*-
from . import models
from . import controllers
from . import tools
from odoo import api, SUPERUSER_ID
from odoo.modules.registry import Registry

import logging

_logger = logging.getLogger(__name__)

def _post_init_hook(cr, registry):
    """Hook chạy sau khi cài đặt module lần đầu"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['mqtt.service'].start_mqtt_service()


def _uninstall_hook(cr, registry):
    """Hook chạy trước khi gỡ cài đặt module"""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['mqtt.service'].stop_mqtt_service()


def _auto_start_mqtt():
    """Hàm khởi động MQTT khi Odoo khởi động"""
    
    # Lấy danh sách database đang hoạt động
    registries = Registry.registries.d
    
    # Với mỗi database, thử khởi động MQTT service
    for db_name, registry_obj in registries.items():
        try:
            with registry_obj.cursor() as cr:
                env = api.Environment(cr, SUPERUSER_ID, {})
                if 'mqtt.service' in env:
                    _logger.info(f"Auto-starting MQTT service for database {db_name}")
                    env['mqtt.service'].start_mqtt_service()
                    cr.commit()
        except Exception as e:
            _logger.error(f"Không thể khởi động MQTT service cho database {db_name}: {e}")
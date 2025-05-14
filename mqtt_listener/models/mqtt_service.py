# -*- coding: utf-8 -*-
from odoo import models, fields, api
from ..controllers.listener import MQTTListener

import platform
import psutil
import logging
import threading
import time
import os

_logger = logging.getLogger(__name__)

# Global dictionary to store MQTT threads
MQTT_THREADS = {}

class MQTTService(models.Model):
    _name = 'mqtt.service'
    _description = 'MQTT Service'

    name = fields.Char(string='Service name', default='MQTT Listener Service', readonly=True)
    last_start = fields.Datetime(string='Last boot', readonly=True)
    status = fields.Selection([
        ('start', 'Start'),
        ('stop', 'Stop'),
        ('error', 'Error'),
    ], string='Status', default='stop', readonly=True)
    thread_identifier = fields.Char(string='Thread Identifier', readonly=True)
    host_info = fields.Char(string='Host Info', compute='_compute_host_info', readonly=True)
    connection_status = fields.Selection([
        ('connected', 'Connected'),
        ('connecting', 'Connecting'),
        ('disconnected', 'Disconnected'),
        ('unknown', 'Unknown'),
    ], string='Connection Status', default='unknown', readonly=True)

    @api.depends()
    def _compute_host_info(self):
        """Display information about the host running the service"""
        for record in self:
            system = platform.system()
            release = platform.release()
            process = psutil.Process(os.getpid())
            
            record.host_info = f"{system} {release}, PID: {process.pid}, Python: {platform.python_version()}"

    @api.model
    def start_mqtt_service(self, *args):
        """Start MQTT Listener service"""
        service = self.search([], limit=1)
        try:
            # Check if there is a running version
            if not service:
                service = self.create({})

            # Check if the service is already running
            thread_id = service.thread_identifier
            if thread_id and thread_id in MQTT_THREADS:
                thread = MQTT_THREADS[thread_id]
                if thread and thread.is_alive():
                    # Update connection status
                    connected = thread._connected if hasattr(thread, '_connected') else False
                    service.write({
                        'connection_status': 'connected' if connected else 'connecting'
                    })
                    _logger.info(f"MQTT Service is already running with ID: {thread_id}")
                    return True

            # If there is an old thread, clean it up before creating a new thread
            if thread_id and thread_id in MQTT_THREADS:
                old_thread = MQTT_THREADS[thread_id]
                if old_thread:
                    try:
                        if old_thread.is_alive():
                            old_thread.stop()
                            old_thread.join(timeout=2)
                        del MQTT_THREADS[thread_id]
                    except Exception as e:
                        _logger.warning(f"Error when cleaning up old thread: {e}")

            # Create a unique identifier for the new thread
            thread_id = f"mqtt_thread_{threading.get_ident()}_{time.time()}"
                
            # Create a new thread
            listener_thread = MQTTListener(self.env)
            
            # Store threads in a global dictionary
            MQTT_THREADS[thread_id] = listener_thread
            
            # Start thread
            listener_thread.start()
            
            # Update information in the database
            service.write({
                'last_start': fields.Datetime.now(),
                'status': 'start',
                'thread_identifier': thread_id,
                'connection_status': 'connecting'
            })
            
            _logger.info(f"Successfully started MQTT Listener with ID: {thread_id}")
            return True
        except Exception as e:
            _logger.error(f"Error while starting MQTT Listener: {e}", exc_info=True)
            if service:
                service.write({
                    'status': 'error',
                    'thread_identifier': False,
                    'connection_status': 'disconnected'
                })
            return False

    @api.model
    def stop_mqtt_service(self, *args):
        """Stop MQTT Listener service"""
        service = self.search([], limit=1)
        try:
            if not service:
                return True
                
            thread_id = service.thread_identifier
            thread = None
            
            # Lấy thread từ dictionary toàn cục
            if thread_id and thread_id in MQTT_THREADS:
                thread = MQTT_THREADS[thread_id]
            
            if thread and thread.is_alive():
                _logger.info(f"Stop MQTT thread with ID: {thread_id}")
                
                # Stop thread safely
                thread.stop()
                # Only call join when the thread is running
                thread.join(timeout=5)
                
                # Remove thread from the dictionary
                if thread_id in MQTT_THREADS:
                    del MQTT_THREADS[thread_id]
            
            # Always update status
            service.write({
                'status': 'stop',
                'thread_identifier': False,
                'connection_status': 'disconnected'
            })
            
            _logger.info("MQTT Listener stopped successfully")
            return True
        except Exception as e:
            _logger.error(f"Error when stopping MQTT Listener: {e}", exc_info=True)
            if service:
                service.write({
                    'status': 'error',
                    'connection_status': 'unknown'
                })
            return False
            
    @api.model
    def check_mqtt_status(self):
        """Check the status of the MQTT service"""
        service = self.search([], limit=1)
        if not service:
            return {'status': 'not_configured', 'message': 'MQTT Service is not configured'}
            
        thread_id = service.thread_identifier
        
        if not thread_id:
            service.write({'connection_status': 'disconnected'})
            return {'status': 'stopped', 'message': 'MQTT Service is not working'}
            
        # Check if thread exists in dictionary
        if thread_id in MQTT_THREADS:
            thread = MQTT_THREADS[thread_id]
            if thread and thread.is_alive():
                # Check additional connection status
                if hasattr(thread, '_connected') and thread._connected:
                    service.write({'connection_status': 'connected'})
                    return {'status': 'connected', 'message': 'MQTT Service is connected and running'}
                else:
                    service.write({'connection_status': 'connecting'})
                    return {'status': 'connecting', 'message': 'MQTT Service is running but not connected'}
        
        # If the thread does not exist or is no longer alive
        service.write({
            'status': 'stop',
            'thread_identifier': False,
            'connection_status': 'disconnected'
        })
        return {'status': 'error', 'message': 'MQTT thread is no longer active'}

    @api.model
    def restart_mqtt_service(self):
        """Restart MQTT service"""
        self.stop_mqtt_service()
        time.sleep(1)  # Wait 1 second to ensure a complete stop
        return self.start_mqtt_service()

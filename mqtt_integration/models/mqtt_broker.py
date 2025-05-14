# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import paho.mqtt.client as mqtt
import random
import string
import socket

class MQTTBroker(models.Model):
    _name = 'mqtt.broker'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MQTT Broker'

    name = fields.Char(string='Broker Name', required=True, tracking=True)
    url_scheme = fields.Selection([
        ('mqtt://', 'MQTT'),
        ('ws://', 'WS')], default='mqtt://', string='URI scheme', required=True, tracking=True)
    host = fields.Char(string='Host', default='broker.emqx.io', required=True, tracking=True)
    port = fields.Char(string='Port', default='1883', required=True, tracking=True)
    client_id = fields.Char(string='Client ID', required=True, readonly=True, copy=False,
                           default=lambda self: self._generate_client_id())
    username = fields.Char(string='Username', default='', tracking=True)
    password = fields.Char(string='Password', default='')
    keepalive = fields.Integer(string='Keepalive (s)', default=60)
    connect_timeout = fields.Integer(string='Connect Timeout (s)', default=10)
    note = fields.Text(string='Note')
    connection_message = fields.Char(string='Connection Message', readonly=True)
    connection_status = fields.Selection([
        ('unknown', 'Unknown'),
        ('success', 'Success'),
        ('fail', 'Fail'),
    ], string='Connection Status', default='unknown', readonly=True, tracking=True)

    @api.model
    def _generate_client_id(self):
        return 'client_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    def action_check_connection(self):
        for rec in self:
            try:
                # Dùng timeout ngắn cho connect
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(rec.connect_timeout)
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                if rec.username:
                    client.username_pw_set(rec.username, rec.password or None)
                client.connect(rec.host, int(rec.port), rec.keepalive)
                client.disconnect()
                rec.connection_status = 'success'
                rec.connection_message = 'Connected successfully!'
                socket.setdefaulttimeout(old_timeout)

            except socket.timeout:
                rec.connection_status = 'fail'
                rec.connection_message = 'Connection timed out!'
                socket.setdefaulttimeout(old_timeout)
                raise UserError('Failed to connect: Connection timed out!')

            except Exception as e:
                rec.connection_status = 'fail'
                rec.connection_message = str(e)
                socket.setdefaulttimeout(old_timeout)
                raise UserError(f'Failed to connect: {e}')

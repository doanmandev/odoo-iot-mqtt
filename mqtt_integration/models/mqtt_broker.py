# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import paho.mqtt.client as mqtt
import random
import string
import socket
import logging

_logger = logging.getLogger(__name__)



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
        ('draft', 'Draft'),
        ('success', 'Success'),
        ('fail', 'Fail'),
    ], string='Connection Status', default='draft', readonly=True, tracking=True)
    subscription_id = fields.Many2one('mqtt.subscription', string='Subscription')
    broker_count = fields.Integer(
        string="Broker Count",
        compute="_compute_broker_count",
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Configuration brokers name must be unique!')
    ]

    @api.model
    def _generate_client_id(self):
        return 'client_' + ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

    def action_connection(self):
        for rec in self:
            try:
                # Use short timeout for connecting
                old_timeout = socket.getdefaulttimeout()
                socket.setdefaulttimeout(rec.connect_timeout)
                client = mqtt.Client(
                        client_id=self.client_id,
                        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                        protocol=mqtt.MQTTv5
                    )
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

    def action_disconnect(self):
        """Disconnect from the broker if connected."""
        self.ensure_one()
        client = mqtt.Client(
                client_id=self.client_id,
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                protocol=mqtt.MQTTv5
            )

        if self.connection_status == 'success' and client:
            try:
                client.disconnect()
                self.write({'connection_status': 'draft'})
            except Exception as e:
                _logger.error(f"Error disconnect broker {self.name}: {e}")

    def action_reconnect(self):
        """Reconnect to the broker if disconnected."""
        for rec in self:
            return rec.action_connection()
        return True

    @api.model
    def _cron_check_all_connections(self):
        brokers = self.search([('connection_status', '=', 'fail')])
        for broker in brokers:
            try:
                broker.action_connection()
            except Exception as e:
                pass

    def _compute_broker_count(self):
        for rec in self:
            subscriptions = self.env['mqtt.subscription'].search([
                ('broker_id', '=', rec.id)
            ])
            rec.broker_count = len(subscriptions)

    def action_check_subscription(self):
            self.ensure_one()
            action = self.env.ref('mqtt_integration.action_mqtt_subscription').read()[0]
            action['domain'] = [
                ('broker_id', '=', self.id),
                ('subscription_status', '=', 'subscribed'),
            ]
            action['context'] = {'default_broker_id': self.id, 'default_subscription_status': 'subscribed'}
            return action

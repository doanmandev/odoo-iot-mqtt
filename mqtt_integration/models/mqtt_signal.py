# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import paho.mqtt.client as mqtt
import logging

_logger = logging.getLogger(__name__)

class MQTTSignal(models.Model):
    _name = 'mqtt.signal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MQTT Signal'
    _rec_name = 'display_name'

    broker_id = fields.Many2one('mqtt.broker', string='Broker', required=True)
    subscription_id = fields.Many2one('mqtt.subscription', string='Subscription', required=True)
    history_ids = fields.One2many('mqtt.signal.history', 'signal_id', string='Signal History')

    topic = fields.Char(string='Topic', related='subscription_id.topic', store=True)
    payload = fields.Text(string='Payload', required=True)
    retain = fields.Boolean(string='Retain', default=False)
    qos = fields.Integer(string='QoS', default=0)
    send_at = fields.Datetime(string='Send At')
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    @api.depends('broker_id.name', 'topic')
    def _compute_display_name(self):
        for rec in self:
            broker_name = rec.broker_id.name or "Unknown Signal Broker"
            rec.display_name = f"{broker_name} - {self.topic}"

    def action_send_mqtt(self):
        for rec in self:
            broker = rec.broker_id
            subscription = rec.subscription_id

            if not broker:
                raise UserError('Not found Broker!')
            if not subscription:
                raise UserError('Not found Subscription!')

            try:
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                if broker.username:
                    client.username_pw_set(broker.username, broker.password or None)
                client.connect(broker.host, int(broker.port), broker.keepalive)
                client.publish(rec.subscription_id.topic, rec.payload, qos=rec.qos or 0, retain=rec.retain or False)
                client.disconnect()

                # Record the time of sending
                rec.send_at = fields.Datetime.now()

                # Save history
                self.env['mqtt.signal.history'].create({
                    'signal_id': rec.id,
                    'payload': rec.payload,
                    'qos': rec.qos,
                    'retain': rec.retain,
                    'direction': 'send',
                })
            except Exception as e:
                raise UserError(f'Send signal Fail: {e}')

    def action_auto_send_mqtt(self):
        """
            Set to automatically send MQTT.
            This action will be called from a button in the interface.
        """
        self.ensure_one()
        _logger.info(f"Auto send MQTT triggered for record: {self.id}")

        # Find the most recent sending in history
        last_sent = self.env['mqtt.signal.history'].search([
            ('signal_id', '=', self.id),
            ('direction', '=', 'send')
        ], limit=1, order='timestamp desc')

        last_sent_timestamp = False
        if last_sent:
            last_sent_timestamp = fields.Datetime.to_string(last_sent.timestamp)

        # Returns the action so that the JavaScript client can process it
        return {
            'type': 'ir.actions.client',
            'tag': 'auto_send_mqtt',
            'target': 'new',
            'record_id': self.id,
            'last_sent_timestamp': last_sent_timestamp
        }
    
    @api.model
    def get_last_mqtt_send(self, signal_id):
        """Get details about the last send for a specific signal"""
        signal = self.browse(signal_id)
        last_sent = self.env['mqtt.signal.history'].search([
            ('signal_id', '=', signal.id),
            ('direction', '=', 'send')
        ], limit=1, order='timestamp desc')
        
        if not last_sent:
            return {
                'success': False,
                'message': 'No previous send history found',
                'data': False
            }
        
        return {
            'success': True,
            'message': 'Last send details retrieved',
            'data': {
                'timestamp': fields.Datetime.to_string(last_sent.timestamp),
                'payload': last_sent.payload,
                'topic': last_sent.topic,
                'qos': last_sent.qos,
                'retain': last_sent.retain
            }
        }

    @api.model
    def get_mqtt_send_stats(self, signal_id):
        """Get statistical information about the sending history for a specific signal"""
        signal = self.browse(signal_id)
        
        # Count the total number of submissions
        total_sent = self.env['mqtt.signal.history'].search_count([
            ('signal_id', '=', signal.id),
            ('direction', '=', 'send')
        ])
        
        # Get the first and most recent submission
        first_sent = self.env['mqtt.signal.history'].search([
            ('signal_id', '=', signal.id),
            ('direction', '=', 'send')
        ], limit=1, order='timestamp asc')
        
        last_sent = self.env['mqtt.signal.history'].search([
            ('signal_id', '=', signal.id),
            ('direction', '=', 'send')
        ], limit=1, order='timestamp desc')
        
        return {
            'total_sent': total_sent,
            'first_sent': fields.Datetime.to_string(first_sent.timestamp) if first_sent else False,
            'last_sent': fields.Datetime.to_string(last_sent.timestamp) if last_sent else False,
        }
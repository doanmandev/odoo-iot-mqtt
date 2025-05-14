# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import paho.mqtt.client as mqtt

class MQTTSignal(models.Model):
    _name = 'mqtt.signal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MQTT Signal'
    _rec_name = 'display_name'

    broker_id = fields.Many2one('mqtt.broker', string='MQTT Broker', required=True)
    subscription_id = fields.Many2one('mqtt.subscription', string='MQTT Subscription', required=True)
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
                raise UserError('Not found MQTT Broker!')
            if not subscription:
                raise UserError('Not found MQTT Subscription!')

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

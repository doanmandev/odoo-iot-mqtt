# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
import paho.mqtt.client as mqtt
import logging

_logger = logging.getLogger(__name__)


class MQTTPublishSignal(models.Model):
    _name = 'mqtt.publish.signal'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MQTT Publish Signal'

    name = fields.Char(string="Name", required=True)
    broker_id = fields.Many2one('mqtt.broker', string='Broker', required=True)
    subscription_id = fields.Many2one('mqtt.subscription', string='Subscription', required=True)
    history_ids = fields.One2many('mqtt.publish.signal.history', 'signal_id', string='Signal History')
    user_property_ids = fields.One2many('mqtt.user.property', 'signal_id', string='User Properties')

    topic = fields.Char(string='Topic', related='subscription_id.topic', store=True)
    direction = fields.Selection([
        ('outgoing', 'Outgoing'), 
        ('incoming', 'Incoming')
    ], string='Direction', default='outgoing')
    payload = fields.Text(string='Payload', required=True)
    retain = fields.Boolean(string='Retain', default=False,
                            help="- Used to mark messages for retention on the broker.\n"
                                 "- Want clients to subscribe later and also receive the latest status immediately.\n"
                                 "- Should be used for signals (e.g. relays, sensors, etc) to get the latest value of the topic.\n"
                                 "- Not for storing data history, logs, special events that are constantly.")
    qos = fields.Integer(string='QoS', default=0)
    send_at = fields.Datetime(string='Send At')
    is_allow_user_property = fields.Boolean(
        string='Allow User Property',
        default=False,
        help="Enable to allow user properties in MQTT messages"
    )

    outgoing_message_count = fields.Integer(
        string="Outgoing Message Count",
        compute="_compute_message_count",
    )
    incoming_message_count = fields.Integer(
        string="Incoming Message Count",
        compute="_compute_message_count",
    )

    @api.depends('history_ids.direction')
    def _compute_message_count(self):
        for rec in self:
            rec.outgoing_message_count = len([
                res for res in rec.history_ids if res.direction == 'outgoing'
            ])
            rec.incoming_message_count = len([
                res for res in rec.history_ids if res.direction == 'incoming'
            ])

    def action_publish_message(self):
        for rec in self:
            broker = rec.broker_id
            subscription = rec.subscription_id

            if not broker:
                raise UserError('Not found Broker!')
            if not subscription:
                raise UserError('Not found Subscription!')

            try:
                client = mqtt.Client(
                    client_id=broker.client_id,
                    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
                    protocol=mqtt.MQTTv5
                )
                if broker.username:
                    client.username_pw_set(broker.username, broker.password or None)
                client.connect(broker.host, int(broker.port), broker.keepalive)

                properties = None
                client.publish(
                    rec.subscription_id.topic,
                    rec.payload,
                    qos=rec.qos or 0,
                    retain=rec.retain or False,
                    properties=properties,
                )

                client.disconnect()

                # Record the time of sending
                rec.send_at = fields.Datetime.now()

                # Save history
                self.env['mqtt.publish.signal.history'].create({
                    'signal_id': rec.id,
                    'topic': rec.topic,
                    'user_id': self.env.user.id,
                    'payload': rec.payload,
                    'qos': rec.qos,
                    'retain': rec.retain,
                    'direction': rec.direction,
                })
            except Exception as e:
                raise UserError(f'Send signal Fail: {e}')

    def action_check_incoming_history(self):
        self.ensure_one()
        action = self.env.ref('mqtt_integration.action_mqtt_incoming_signal').read()[0]
        action['domain'] = [
            ('signal_id', '=', self.id),
            ('direction', '=', 'incoming'),
        ]
        action['context'] = {'default_signal_id': self.id, 'default_direction': 'incoming'}
        return action

    def action_check_outgoing_history(self):
        self.ensure_one()
        action = self.env.ref('mqtt_integration.action_mqtt_outgoing_signal').read()[0]
        action['domain'] = [
            ('signal_id', '=', self.id),
            ('direction', '=', 'outgoing'),
        ]
        action['context'] = {'default_signal_id': self.id, 'default_direction': 'outgoing'}
        return action

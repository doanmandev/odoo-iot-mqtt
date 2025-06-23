# -*- coding: utf-8 -*-
from odoo import models, fields, api


class MQTTMessageHistory(models.Model):
    _name = 'mqtt.message.history'
    _description = 'MQTT Message History'
    _rec_name = 'display_name'
    _order = "timestamp desc"

    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)
    direction = fields.Selection([('outgoing', 'Outgoing'), ('incoming', 'Incoming')], string='Direction', required=True)
    broker_id = fields.Many2one('mqtt.broker', string='Broker')
    subscription_id = fields.Many2one('mqtt.subscription', string='Subscription')
    user_property_ids = fields.One2many('mqtt.user.property', 'history_id', string='User Properties')
    topic = fields.Char(string='Topic')
    format_payload = fields.Char(string='Format Payload')
    payload = fields.Text(string='Payload', required=True)
    qos = fields.Integer(string='QoS')
    retain = fields.Boolean(string='Retain')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)

    @api.depends('broker_id', 'timestamp')
    def _compute_display_name(self):
        for rec in self:
            broker_name = rec.broker_id.name or "Unknown Broker"
            topic_name = rec.topic or "Unknown Topic"
            topic_broker = f"{broker_name} - {topic_name}"
            # Convert timestamp to user's timezone
            if rec.timestamp:
                local_timestamp = fields.Datetime.context_timestamp(self, rec.timestamp)
                formatted_time = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                rec.display_name = f"{topic_broker} - {formatted_time}"
            else:
                rec.display_name = f"{topic_broker} - No timestamp"

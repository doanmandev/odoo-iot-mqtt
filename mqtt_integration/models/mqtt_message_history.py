# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MqttMessageHistory(models.Model):
    _name = 'mqtt.message.history'
    _description = 'MQTT Message History'
    _rec_name = 'display_name'
    _order = "timestamp desc"

    message_id = fields.Many2one('mqtt.message', string='MQTT Message')
    payload = fields.Text(string='Payload', required=True)
    topic = fields.Char(string='Topic')
    qos = fields.Integer(string='QoS')
    retain = fields.Boolean(string='Retain')
    direction = fields.Selection([('send', 'Send'), ('receive', 'Received')], string='Direction', required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    @api.depends('message_id.subscription_id', 'timestamp')
    def _compute_display_name(self):
        for rec in self:
            subscription_name = rec.message_id.subscription_id.topic or "Unknown Message Broker"
            rec.display_name = f"{subscription_name} - {rec.timestamp}"

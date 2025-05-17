# -*- coding: utf-8 -*-
from odoo import models, fields, api

class MQTTSignalHistory(models.Model):
    _name = 'mqtt.signal.history'
    _description = 'MQTT Signal History'
    _rec_name = 'display_name'
    _order = "timestamp desc"

    signal_id = fields.Many2one('mqtt.signal', string='Signal')
    payload = fields.Text(string='Payload', required=True)
    topic = fields.Char(string='Topic')
    qos = fields.Integer(string='QoS')
    retain = fields.Boolean(string='Retain')
    direction = fields.Selection([('send', 'Send'), ('receive', 'Received')], string='Direction', required=True)
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)

    @api.depends('signal_id.subscription_id', 'timestamp')
    def _compute_display_name(self):
        for rec in self:
            subscription_name = rec.signal_id.subscription_id.topic or "Unknown Signal Broker"
            
            # Convert timestamp to user's timezone
            if rec.timestamp:
                local_timestamp = fields.Datetime.context_timestamp(self, rec.timestamp)
                formatted_time = local_timestamp.strftime('%Y-%m-%d %H:%M:%S')
                rec.display_name = f"{subscription_name} - {formatted_time}"
            else:
                rec.display_name = f"{subscription_name} - No timestamp"
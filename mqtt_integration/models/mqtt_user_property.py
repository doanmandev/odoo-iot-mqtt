# -*- coding: utf-8 -*-
from odoo import models, fields


class MQTTUserProperty(models.Model):
    _name = 'mqtt.user.property'
    _description = 'MQTT User Property'

    key = fields.Char(string='Key', required=True)
    value = fields.Char(string='Value')
    topic_id = fields.Many2one('mqtt.topic', string='Topic')
    history_id = fields.Many2one('mqtt.message.history', string='History')
    content_type = fields.Char(
        string='Content Type',
        help="Defines the content type of the payload, "
             "e.g. application/json, text/plain, image/jpeg, etc.\n"
             "Uses:\n"
             "Helps the receiver determine what type of payload "
             "to process (e.g. if the receiver is json, parse json).\n"
             "Useful when you transmit diverse data."
    )
    format_payload = fields.Char(
        string='Payload Format Indicator',
        help="Select payload type: 0 (binary string) or 1 (text string).\n"
             "Uses:\n"
             "Determines the data type of the payload, serving correct processing at the receiver."
    )
    expiry = fields.Char(
        string= 'Message Expiry Interval',
        help="Set the message time to live (seconds). "
             "After this time, the message will be discarded by the broker "
             "if it has not been delivered to the subscriber.\n"
             "Uses:\n"
             "Ensures that the message does not exist forever if the subscriber connects too late."
    )
    response_topic = fields.Char(
        string='Response Topic',
        help="Defines the topic on which the receiver should publish a response message.\n"
             "Uses:\n"
             "Useful in systems that require “request-response” over MQTT, e.g. "
             "controlling a relay and receiving status feedback."
    )
    correlation_data = fields.Char(
        string='Correlation Data',
        help="Data included to correlate (link) between request and response (usually used with response topic).\n"
             "Uses:\n"
             "Serves scenarios for comparing and authenticating requests - responses."
    )
    subscription_identifier = fields.Char(
        string='Subscription Identifier',
        help="Assigns an identifier to a subscription to distinguish different subscription streams.\n"
             "Uses:\n"
             "Easy to track subscription streams when analyzing/monitoring."
    )

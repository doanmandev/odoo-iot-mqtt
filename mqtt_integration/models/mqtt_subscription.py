# -*- coding: utf-8 -*-
from odoo import models, fields, api, registry
from odoo.api import Environment
from odoo.exceptions import UserError

import paho.mqtt.client as mqtt
import logging
import threading

_logger = logging.getLogger(__name__)

class MQTTSubscription(models.Model):
    _name = 'mqtt.subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MQTT Subscription'
    _rec_name = 'display_name'

    broker_id = fields.Many2one('mqtt.broker', string='MQTT Broker', required=True)
    topic = fields.Char(string='Topic', required=True)
    qos = fields.Integer(string='QoS', default=0)
    no_local_flag = fields.Boolean(string='No Local Flag', default=False)
    retain_as_published_flag = fields.Boolean(string='Retain as Published Flag', default=False)
    retain_handling = fields.Integer(string='Retain handling', default=0)
    subscribed = fields.Boolean(string='Subscribed', default=False)
    subscription_time = fields.Datetime(string="Subscription Time")
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)
    subscription_in_progress = fields.Boolean(string='Subscription In Progress', default=False)
    subscription_status = fields.Selection([
        ('subscribed', 'Subscribed'),
        ('subscribing', 'Subscribing'),
        ('fail', 'Fail'),
    ], string='Subscription Status', compute="_compute_status", readonly=True)

    @api.depends('broker_id.name', 'topic')
    def _compute_display_name(self):
        for rec in self:
            broker_name = rec.broker_id.name or "Unknown Broker"
            rec.display_name = f"{broker_name} - {rec.topic}"


    @api.depends('subscribed', 'subscription_in_progress')
    def _compute_status(self):
        for rec in self:
            if rec.subscribed:
                rec.subscription_status = "subscribed"
            elif rec.subscription_in_progress:
                rec.subscription_status = "subscribing"
            else:
                rec.subscription_status = "fail"

    def subscribe_mqtt(self):
        for rec in self:
            broker = rec.broker_id
            if not broker:
                raise UserError("Broker not selected!")

            try:
                # client = mqtt.Client(protocol=mqtt.MQTTv311)
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

                subscription_id = rec.id
                env = self.env

                def on_subscribe(client, userdata, mid, granted_qos, properties=None):
                    try:
                        with registry(env.cr.dbname).cursor() as new_cr:
                            new_env = api.Environment(new_cr, env.uid, env.context)
                            subscription = new_env['mqtt.subscription'].browse(subscription_id)
                            _logger.info(f"[SUBACK] Subscribed to {subscription.topic} with QoS {granted_qos}")
                            subscription.write({
                                'subscribed': True,
                                'subscription_time': fields.Datetime.now(),
                                'subscription_in_progress': False,
                            })
                            new_cr.commit()
                    except Exception as e:
                        _logger.error(f"Error in on_subscribe: {e}")
                        subscription.write({'subscription_in_progress': False})

                client.on_subscribe = on_subscribe

                if broker.username:
                    client.username_pw_set(broker.username, broker.password or None)

                client.connect(broker.host, int(broker.port), broker.keepalive)
                client.loop_start()

                client.subscribe(rec.topic, qos=rec.qos)

                _logger.info(f"Subscription request sent to broker {broker.name} - Topic: {rec.topic}")
            except Exception as e:
                raise UserError(f"Error subscribing to topic: {e}")

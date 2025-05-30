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

    broker_id = fields.Many2one('mqtt.broker', string='Broker', required=True)
    topic = fields.Char(string='Topic', required=True)
    qos = fields.Integer(string='QoS', default=0)
    no_local_flag = fields.Boolean(string='No Local Flag', default=False)
    retain_as_published_flag = fields.Boolean(string='Retain as Published Flag', default=False)
    retain_handling = fields.Integer(string='Retain handling', default=0)
    subscription_time = fields.Datetime(string="Subscription Time")
    display_name = fields.Char(string="Display Name", compute="_compute_display_name", store=True)
    subscription_status = fields.Selection([
        ('subscribed', 'Subscribed'),
        ('subscribing', 'Subscribing'),
        ('fail', 'Fail'),
    ], string='Subscription Status', default='fail', readonly=True)
    user_id = fields.Many2one('res.users', string='User',
                              default=lambda self: self.env.user, required=True)

    @api.depends('broker_id.name', 'topic')
    def _compute_display_name(self):
        for rec in self:
            broker_name = rec.broker_id.name or "Unknown Broker"
            rec.display_name = f"{broker_name} - {rec.topic}"

    def subscribe_mqtt(self):
        for rec in self:
            broker = rec.broker_id
            if not broker:
                raise UserError("Broker not selected!")

            try:
                rec.write({'subscription_status': 'subscribing'})

                # Create a new MQTT client instance
                topic = rec.topic
                qos = rec.qos
                subscription_id = rec.id
                env = self.env
                dbname = self.env.cr.dbname
                uid = self.env.uid
                context = self.env.context

                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
                
                # Set userdata with necessary information
                userdata = {
                    'topic': topic,
                    'qos': qos,
                    'subscription_id': subscription_id,
                    'dbname': dbname,
                    'uid': uid,
                    'context': context
                }
                client.user_data_set(userdata)

                def on_connect(client, userdata, flags, rc, properties=None):
                    if rc == 0:
                        # Connection successful
                        client.subscribe(userdata['topic'], qos=userdata['qos'])
                    else:
                        _logger.error(f"MQTT connect failed with code {rc}")

                def on_subscribe(client, userdata, mid, granted_qos, properties=None):
                    try:
                        with registry(userdata['dbname']).cursor() as new_cr:
                            new_env = api.Environment(new_cr, userdata['uid'], userdata['context'])
                            subscription = new_env['mqtt.subscription'].browse(userdata['subscription_id'])
                            _logger.info(f"[SUBACK] Subscribed to {subscription.topic} with QoS {granted_qos}")
                            subscription.write({
                                'subscription_status': 'subscribed',
                                'subscription_time': fields.Datetime.now(),
                            })
                            new_cr.commit()
                    except Exception as e:
                        _logger.error(f"Error in on_subscribe: {e}")
                        # If subscription fails, update status
                        try:
                            with registry(userdata['dbname']).cursor() as new_cr:
                                new_env = api.Environment(new_cr, userdata['uid'], userdata['context'])
                                subscription = new_env['mqtt.subscription'].browse(userdata['subscription_id'])
                                subscription.write({'subscription_status': 'fail'})
                                new_cr.commit()
                        except Exception as inner_e:
                            _logger.error(f"Failed to update subscription status: {inner_e}")

                client.on_connect = on_connect
                client.on_subscribe = on_subscribe

                if broker.username:
                    client.username_pw_set(broker.username, broker.password or None)

                client.connect(broker.host, int(broker.port), broker.keepalive)
                client.loop_start()

                _logger.info(f"Subscription request sent to broker {broker.name} - Topic: {topic}")
            except Exception as e:
                rec.write({'subscription_status': 'fail'})
                raise UserError(f"Error subscribing to topic: {e}")
# -*- coding: utf-8 -*-
import threading
import time
import logging
import paho.mqtt.client as mqtt
from odoo.api import Environment
from odoo import SUPERUSER_ID

_logger = logging.getLogger(__name__)


class MQTTListener(threading.Thread):
    def __init__(self, env):
        super().__init__()
        self.name = "MQTTListener"
        self.registry = env.registry
        self.dbname = env.cr.dbname
        self.daemon = True  # Let Odoo kill thread when server is off
        
        # Initialize the client with unique client_id to avoid conflicts
        client_id = f"odoo_mqtt_listener_{threading.get_ident()}"
        self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
        
        # Default configuration if no connection found in the database
        # Change default broker to a trusted public broker
        self.broker = "broker.emqx.io"  # Public broker instead of localhost
        self.port = '1883'  # Default MQTT port
        self.username = ""
        self.password = ""
        self.topics = [("mqtt/test", 0)]  # Default theme to test
        self.is_configured = False  # Configuration status
        
        # Read configuration from the database if available
        self._load_connection_config(env)
        
        _logger.info(f"MQTT Listener will connect to {self.broker}:{self.port}")
        
        self._stop_event = threading.Event()
        self._reconnect_delay = 5
        self._max_reconnect_delay = 300  # Maximum reconnect delay (5 minutes)
        self._current_delay = self._reconnect_delay
        self._connected = False
        self._last_activity = time.time()  # Add last uptime tracking variable
        
        # Add debug to record MQTT events
        self.client.enable_logger(_logger)
        
    def _load_connection_config(self, env):
        """Read connection configuration from mqtt.broker.connection and mqtt.subscription records"""
        try:
            #  Find an active broker connection
            broker_conn = env['mqtt.broker'].search([('connection_status', '=', 'success')], limit=1)
            if broker_conn:
                if broker_conn.host:  # Update only if the host has a value
                    self.broker = broker_conn.host
                    self.port = broker_conn.port
                    self.username = broker_conn.username or ""
                    self.password = broker_conn.password or ""
                    self.is_configured = True
                
                    # Update client_id if available
                    if broker_conn.client_id:
                        self.client = mqtt.Client(client_id=broker_conn.client_id, 
                                                callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
                
                    # Config username and password
                    if self.username:
                        self.client.username_pw_set(self.username, self.password)
                    
                    _logger.info(f"Loaded broker configuration from '{broker_conn.name}'")
            
            # Read subscription topics from the database
            subscriptions = env['mqtt.subscription'].search([('subscribed', '=', True)])
            if subscriptions:
                self.topics = [(sub.topic, sub.qos) for sub in subscriptions]
                _logger.info(f"Loaded {len(self.topics)} subscription topics")
            
        except Exception as e:
            _logger.error(f"Error loading MQTT configuration: {e}", exc_info=True)

    def on_connect(self, client, userdata, flags, rc, properties=None):
        if rc == 0:
            self._connected = True
            self._last_activity = time.time()  # Update uptime
            # Reset reconnect delay after successful connection
            self._current_delay = self._reconnect_delay
            _logger.info(f"=== MQTT Connected successfully to {self.broker}:{self.port}! ===")
            for topic, qos in self.topics:
                client.subscribe(topic, qos)
                _logger.info(f"Subscribed to topic: {topic} with QoS {qos}")
        else:
            self._connected = False
            _logger.error(f"MQTT connection failed with code {rc}: {mqtt.connack_string(rc)}")

    def on_disconnect(self, client, userdata, rc, properties=None):
        self._connected = False
        _logger.warning(f"MQTT Disconnected with result code {rc}")

    def on_message(self, client, userdata, msg, properties=None):
        self._last_activity = time.time()  # Update uptime when receiving messages
        _logger.info(f"Received message on {msg.topic}: {msg.payload.decode()}")
        try:
            with self.registry.cursor() as cr:
                env = Environment(cr, SUPERUSER_ID, {})

                message_data = {
                    'topic': msg.topic,
                    'signal_id': False,
                    'payload': msg.payload.decode(errors='ignore'),
                    'qos': msg.qos,
                    'direction': 'receive',
                    'retain': msg.retain,
                }

                env['mqtt.signal.history'].create(message_data)

                _logger.info(f"Saved MQTT messages to database: {msg.topic}")
                cr.commit()
        except Exception as e:
            _logger.error(f"Error processing MQTT message: {e}", exc_info=True)

    def on_subscribe(self, client, userdata, mid, granted_qos, properties=None):
        self._last_activity = time.time()  # Update uptime
        _logger.info(f"Subscription confirmed with QoS: {granted_qos}")

    def on_log(self, client, userdata, level, buf):
        # Update uptime when there is an activity log
        self._last_activity = time.time()
        if level == mqtt.MQTT_LOG_INFO:
            _logger.info(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_WARNING:
            _logger.warning(f"MQTT Log: {buf}")
        elif level == mqtt.MQTT_LOG_ERR:
            _logger.error(f"MQTT Log: {buf}")
        else:
            _logger.debug(f"MQTT Log: {buf}")

    def run(self):
        _logger.info("=== MQTT Listener starts running ===")
        
        # Set up callbacks
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        self.client.on_subscribe = self.on_subscribe
        self.client.on_log = self.on_log
        
        # Set keepalive lower to detect connection loss faster
        keepalive = 30
        
        # Set clean_session=True to avoid storing old messages
        self.client.clean_session = True

        # Check if the configuration is valid
        if not self.broker or int(self.port) <= 0:
            _logger.error("Invalid MQTT configuration. Broker address and port required > 0")
            return

        while not self._stop_event.is_set():
            if not self._connected:
                try:
                    _logger.info(f"Connecting to broker {self.broker}:{self.port}")
                    
                    # Add username and password if available
                    if self.username:
                        self.client.username_pw_set(self.username, self.password)
                        _logger.info(f"Connecting with username: {self.username}")
                    
                    # Set a connection timeout in the client
                    self.client.connect_async(self.broker, int(self.port), keepalive)
                    self.client.loop_start()
                    
                    # Wait a moment for the connection to be established
                    time.sleep(2)
                    
                    # Check connection after waiting
                    if not self._connected:
                        _logger.warning(f"Connection failed after 2 seconds, will try again in {self._current_delay} seconds...")
                        if hasattr(self.client, 'loop_stop'):
                            self.client.loop_stop()

                        # Increase the delay value exponentially, up to max_reconnect_delay
                        self._current_delay = min(self._current_delay * 1.5, self._max_reconnect_delay)
                except Exception as e:
                    _logger.error(f"Unable to connect to broker: {e}", exc_info=True)
                    # Increase the delay value exponentially, up to max_reconnect_delay
                    self._current_delay = min(self._current_delay * 1.5, self._max_reconnect_delay)
                    _logger.info(f"Will retry connection in {self._current_delay} seconds")
                
                time.sleep(self._current_delay)
                continue

            # Check connection and wait
            time.sleep(5)
            
            # Check the connection using uptime.
            if self._connected:
                # Check idle time
                inactive_time = time.time() - self._last_activity
                if inactive_time > 60:  # If no activity for 60 seconds
                    _logger.warning(f"No MQTT activity for {inactive_time:.0f} seconds, checking connection...")
                    
                    # Safe way to check connectivity: resubscribe to a topic
                    try:
                        if self.topics:
                            topic, qos = self.topics[0]
                            self.client.subscribe(topic, qos)
                            _logger.info(f"Re-subscribed to topic {topic} to check connection")
                            self._last_activity = time.time() # Reset uptime
                    except Exception as e:
                        _logger.warning(f"Error checking connection: {e}")
                        self._connected = False

        # When receiving a stop order
        _logger.info("Receive command to stop MQTT Listener...")
        if hasattr(self.client, 'loop_stop'):
            self.client.loop_stop()
        if hasattr(self.client, 'disconnect'):
            try:
                self.client.disconnect()
            except Exception as e:
                _logger.error(f"Error when disconnecting MQTT: {e}")
        _logger.info("=== MQTT Listener has stopped ===")

    def stop(self):
        _logger.info("Stopping MQTT Listener...")
        self._stop_event.set()

    def test_connection(self):
        """Test connection check function"""
        # Check configuration validity
        if not self.broker or int(self.port) <= 0:
            _logger.error("Cannot test connection: Invalid broker settings")
            return False
            
        try:
            test_client = mqtt.Client(
                client_id=f"odoo_test_connection_{threading.get_ident()}", 
                callback_api_version=mqtt.CallbackAPIVersion.VERSION2
            )
            # Set connection timeout
            test_client.connect_async(self.broker, int(self.port), 10)
            test_client.loop_start()
            # Wait a moment for connection
            time.sleep(2)
            test_client.disconnect()
            test_client.loop_stop()
            return True
        except Exception as e:
            _logger.error(f"Check connection failed: {e}")
            return False
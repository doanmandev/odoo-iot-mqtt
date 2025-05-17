odoo.define('mqtt_signal.auto_send', function (require) {
    "use strict";

    var AbstractAction = require('web.AbstractAction');
    var core = require('web.core');
    var session = require('web.session');
    var ajax = require('web.ajax');
    var _t = core._t;
    var rpc = require('web.rpc');
    var QWeb = core.qweb;

    var AutoSendMQTT = AbstractAction.extend({
        template: 'mqtt_integration.AutoSendMQTT', // Template QWeb
        events: {
            'click .js_stop_auto_send': '_onStopAutoSend',
        },

        /**
         * Initialization 
         */
        init: function (parent, action) {
            this._super.apply(this, arguments);
            this.recordId = action.record_id;
            this.autoSendTimer = null;
            this.isSending = false;
            this.sentCount = 0;
            this.lastSentTime = null;
            
            // Get last sent time from action
            if (action.last_sent_timestamp) {
                this.lastSentTime = new Date(action.last_sent_timestamp);
            } else {
                this.lastSentTime = null;
            }
        },

        /**
         * Download last-sent data
         */
        _loadLastSentData: function() {
            var self = this;
            
            // Use RPC to call the method to get the last sent time
            return rpc.query({
                model: 'mqtt.signal',
                method: 'get_last_mqtt_send',
                args: [this.recordId],
            }).then(function(result) {
                if (result.success && result.data && result.data.timestamp) {
                    self.lastSentTime = new Date(result.data.timestamp);
                    self._updateStats();
                }
            });
        },


        /**
        * Starts when the component is rendered
         */
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function() {
                // Load the most recent sent data if not already present
                if (!self.lastSentTime) {
                    return self._loadLastSentData();
                }
            }).then(function() {
                // Update initial statistics
                self._updateStats();
                
                // Start sending automatically when the component is rendered
                self._startAutoSend();
            });
        },

        /**
         * Updates the displayed statistics
         */
        _updateStats: function() {
            // Update the number of submissions
            this.$('.js_sent_count').text(this.sentCount);
            
            // Update last sent time
            if (this.lastSentTime) {
                // Time format with HH:MM:SS
                var hours = this.lastSentTime.getHours().toString().padStart(2, '0');
                var minutes = this.lastSentTime.getMinutes().toString().padStart(2, '0');
                var seconds = this.lastSentTime.getSeconds().toString().padStart(2, '0');
                
                var formattedTime = hours + ':' + minutes + ':' + seconds;
                this.$('.js_last_sent').text(formattedTime);
            } else {
                this.$('.js_last_sent').text('Not yet');
            }
        },

        /**
         * Start sending MQTT automatically every 1 second
         */
        _startAutoSend: function () {
            var self = this;
            this.isSending = true;
            
            function sendMQTT() {
                if (!self.isSending) {
                    return;
                }
                
                ajax.jsonRpc('/web/dataset/call_button', 'call', {
                    model: 'mqtt.signal',
                    method: 'action_send_mqtt',
                    args: [[self.recordId]],
                    kwargs: {},
                    context: session.user_context,
                }).then(function (result) {
                    self.sentCount++;
                    self.lastSentTime = new Date();
                    self._updateStats();
                    console.log("MQTT sent successfully, count:", self.sentCount);
                }).guardedCatch(function (error) {
                    console.error("Error sending MQTT:", error);
                }).finally(function () {
                    // Lên lịch gửi tiếp theo sau 1 giây
                    if (self.isSending) {
                        self.autoSendTimer = setTimeout(function () {
                            sendMQTT();
                        }, 1000);
                    }
                });
            }
            
            // Start the first cycle immediately
            sendMQTT();
        },

        /**
         * Handle event when the stop button is pressed
         */
        _onStopAutoSend: function (ev) {
            ev.preventDefault();
            this._stopAutoSend();
            
            // Show a message before closing
            this.displayNotification({
                title: _t("MQTT Auto Sender"),
                message: _t("Stopped after sending " + this.sentCount + " MQTT message"),
                type: 'info'
            });
            
            // Close the window in a moment
            setTimeout(() => {
                this.do_action({
                    type: 'ir.actions.act_window_close'
                });
            }, 1000);
        },
        
        /**
         * Stop auto-sending
         */
        _stopAutoSend: function () {
            console.log("Stopping auto-send, total sent:", this.sentCount);
            this.isSending = false;
            if (this.autoSendTimer) {
                clearTimeout(this.autoSendTimer);
                this.autoSendTimer = null;
            }
        },
        
        /**
         * Clean up when a component is destroyed
         */
        destroy: function () {
            this._stopAutoSend();
            this._super.apply(this, arguments);
        }
    });

    // Register action with core
    core.action_registry.add('auto_send_mqtt', AutoSendMQTT);

    return AutoSendMQTT;
});
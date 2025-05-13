# Tài liệu MQTT Integration
### Phần 1: tóm tắt tài liệu
### Phần 2: Chi tiết

# Phần 1
## Tóm tắt tài liệu
Tài liệu MQTT_Integration.md cung cấp một hướng dẫn chi tiết và toàn diện về giao diện trừu tượng MQTT trong Odoo. 

Tài liệu này bao gồm:
- Giới thiệu về mục đích và thiết kế của MQTT Integration
- Kiến trúc hệ thống và luồng dữ liệu
- API chi tiết với các ví dụ mã nguồn
- Hướng dẫn quản lý thread MQTT
- Cách lưu trữ và xử lý tin nhắn MQTT
- Xử lý lỗi và cơ chế tái kết nối
- Cách tích hợp với các module Odoo khác
- Cấu hình bảo mật
- Hướng dẫn triển khai
- Các thực tiễn tốt nhất
- Phương pháp gỡ lỗi và giám sát hiệu suất

Tài liệu này giúp nhà phát triển hiểu rõ cách sử dụng và mở rộng MQTT Integration cho các ứng dụng IoT và tích hợp hệ thống trong Odoo.

# Phần 2
## Giới thiệu
MQTT Integration là lớp trừu tượng cung cấp giao diện thống nhất cho việc giao tiếp MQTT trong hệ thống Odoo. 
Module này đóng vai trò làm cầu nối giữa Odoo và các thiết bị IoT hoặc dịch vụ bên ngoài, cho phép trao đổi dữ liệu theo thời gian thực thông qua giao thức MQTT.

## Mục đích thiết kế
- **Tính trừu tượng hóa**: Đóng gói và che giấu độ phức tạp của việc giao tiếp MQTT
- **Tính mở rộng**: Cho phép dễ dàng thêm các broker MQTT mới và định dạng tin nhắn
- **Tích hợp hệ thống**: Cung cấp khung làm việc thống nhất cho các module khác sử dụng MQTT
- **Quản lý trạng thái**: Theo dõi và quản lý kết nối MQTT trong suốt vòng đời ứng dụng

## Kiến trúc hệ thống
### Thành phần chính
1. **MQTT Service Manager**:
   - Model: `mqtt.service`
   - Quản lý vòng đời của dịch vụ MQTT
   - Cung cấp API để khởi động, dừng và kiểm tra trạng thái kết nối
   - Lưu trữ thông tin về kết nối và thread hiện tại

2. **MQTT Thread Manager**:
   - Quản lý các thread MQTT chạy song song với tiến trình chính của Odoo
   - Sử dụng từ điển toàn cục `MQTT_THREADS` để theo dõi các thread đang hoạt động
   - Đảm bảo dừng an toàn khi cần thiết

3. **Abstract Interface Class**:
   - Định nghĩa các phương thức tiêu chuẩn cho kết nối MQTT
   - Điều chỉnh các callback cho các sự kiện MQTT khác nhau
   - Cung cấp xử lý lỗi và tái kết nối tự động

## API của Abstract Interface
### Khởi tạo Kết nối
```python 
def __init__(self, env): # Khởi tạo các thông số kết nối
    self.registry = env.registry
    self.dbname = env.cr.dbname

    # Cấu hình client
    client_id = f"odoo_mqtt_interface_{identifier}"
    self.client = mqtt.Client(client_id=client_id, callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    
    # Cấu hình broker
    self.broker = "broker_address"
    self.port = 1883
    
    # Cấu hình topics
    self.topics = [("topic/path", qos)]
```

### Kết nối và Ngắt kết nối
```python
def connect(self): # Kết nối đến broker 
    self.client.connect(self.broker, self.port, keepalive)
    self.client.loop_start()

def disconnect(self): # Ngắt kết nối an toàn 
    self.client.loop_stop()
    self.client.disconnect()
```

### Đăng ký và Hủy đăng ký Topic
```python
def subscribe(self, topic, qos=0): # Đăng ký nhận tin nhắn từ topic 
    self.client.subscribe(topic, qos)
def unsubscribe(self, topic): # Hủy đăng ký topic 
    self.client.unsubscribe(topic)
```

### Gửi tin nhắn
```python
def publish(self, topic, payload, qos=0, retain=False): # Gửi tin nhắn đến topic 
    self.client.publish(topic, payload, qos, retain)
```

### Callback xử lý sự kiện MQTT
```python
def on_connect(self, client, userdata, flags, rc, properties=None): # Xử lý khi kết nối thành công hoặc thất bại
def on_disconnect(self, client, userdata, rc, properties=None): # Xử lý khi ngắt kết nối
def on_message(self, client, userdata, msg, properties=None): # Xử lý khi nhận được tin nhắn mới
def on_subscribe(self, client, userdata, mid, granted_qos, properties=None): # Xử lý khi đăng ký topic thành công
def on_publish(self, client, userdata, mid, properties=None): # Xử lý khi gửi tin nhắn thành công
```

## Quản lý MQTT Thread
### Khởi động Thread
```python
def start_mqtt_thread(self, thread_name): # Khởi tạo và lưu thread 
    thread_id = f"mqtt_thread_{thread_name}_{identifier}" 
    listener_thread = MQTTListener(self.env) 
    MQTT_THREADS[thread_id] = listener_thread

    # Khởi động thread
    listener_thread.start()
    return thread_id
```

### Dừng Thread
```python
def stop_mqtt_thread(self, thread_id): # Lấy thread từ dictionary
    if thread_id in MQTT_THREADS: 
        thread = MQTT_THREADS[thread_id]

        # Dừng thread an toàn
        if thread and thread.is_alive():
            thread.stop()
            thread.join(timeout=5)
            
        # Xóa thread khỏi dictionary
        del MQTT_THREADS[thread_id]
        return True
    return False
```

### Kiểm tra trạng thái Thread
```python
def check_thread_status(self, thread_id): # Kiểm tra thread có tồn tại và đang chạy
    if thread_id in MQTT_THREADS: 
        thread = MQTT_THREADS[thread_id] 
        if thread and thread.is_alive(): # Kiểm tra trạng thái kết nối
            if hasattr(thread, '_connected'): 
                return thread._connected 
    return False
```

## Lưu trữ Tin nhắn
### Model Data
Các model cơ bản được sử dụng để lưu trữ thông tin về tin nhắn MQTT:
1. **mqtt.message.history**
   - Lưu lịch sử các tin nhắn gửi và nhận
   - Các trường: topic, payload, qos, direction, retain, timestamp

2. **mqtt.broker**
   - Lưu thông tin về các broker MQTT
   - Các trường: name, host, port, username, password

3. **mqtt.topic**
   - Quản lý các topic được sử dụng
   - Các trường: name, description, qos, retain

### Lưu tin nhắn
```python
def store_message(self, env, msg, direction='receive'): # Lưu tin nhắn vào database
    env['mqtt.message.history'].create({
        'topic': msg.topic, 
        'message_id': msg.mid if hasattr(msg, 'mid') else False, 
        'payload': msg.payload.decode(errors='ignore'), 
        'qos': msg.qos, 
        'direction': direction, 
        'retain': msg.retain if hasattr(msg, 'retain') else False, 
    })
```

## Xử lý Lỗi và Tái Kết Nối
### Tái kết nối tự động
```python
def handle_reconnection(self): # Cấu hình thời gian tái kết nối
    self._reconnect_delay = 5 # Thời gian giữa các lần thử kết nối
    # Logic tái kết nối
    while not connected and not stop_event.is_set():
        try:
            # Thử kết nối
            self.client.connect(self.broker, self.port, keepalive)
            self.client.loop_start()
        except Exception as e:
            # Xử lý lỗi và đợi
            log_error(f"Connection failed: {e}")
            time.sleep(self._reconnect_delay)
```

### Xử lý ngoại lệ
```python
def safe_mqtt_operation(self, operation, *args, **kwargs): 
    try:
        # Thực hiện hành động MQTT an toàn
        return operation(*args, **kwargs) 
    except Exception as e: 
        # Ghi log và phục hồi 
        log_error(f"MQTT operation failed: {e}")
        self._handle_mqtt_error(e)
    return False
```

## Tích Hợp với Odoo
### Sử dụng trong Module Khác
```python
from ..controllers.mqtt_interface import MQTTAbstractInterface
class MyCustomClass(models.Model):
    _name = 'my.custom.model'
    
    def send_mqtt_message(self):
        mqtt_service = self.env['mqtt.service']
    
        # Kiểm tra dịch vụ đang chạy
        if mqtt_service.check_mqtt_status()['status'] == 'connected':
            # Gửi tin nhắn
            payload = json.dumps({'key': 'value'})
            topic = 'my/custom/topic'
            
            # Sử dụng phương thức publish
            self.env['mqtt.interface'].publish(topic, payload, qos=1)
```

### Mở Rộng Abstract Interface
```python
from ..controllers.mqtt_interface import MQTTAbstractInterface
class CustomMQTTInterface(MQTTAbstractInterface): 
    def __init__(self, env):
        super().__init__(env) # Ghi đè cấu hình 
        self.broker = "custom-broker.com"
        self.port = 8883
    
    def on_message(self, client, userdata, msg, properties=None):
        # Ghi đè xử lý tin nhắn
        custom_payload = json.loads(msg.payload.decode())
        
        # Logic xử lý tùy chỉnh
        if custom_payload.get('action') == 'specific_action':
            self._handle_specific_action(custom_payload)
            
        # Gọi phương thức của lớp cha
        super().on_message(client, userdata, msg, properties)
```

## Bảo Mật
### Xác thực
```python
def setup_authentication(self, username, password):
    # Thiết lập thông tin xác thực
    self.client.username_pw_set(username, password)
```

### TLS/SSL
```python
def setup_tls(self, ca_certs=None, certfile=None, keyfile=None):
    # Cấu hình TLS/SSL
    if all([ca_certs, certfile, keyfile]):
        self.client.tls_set(
            ca_certs=ca_certs,
            certfile=certfile,
            keyfile=keyfile
        )
    else:
        # Sử dụng TLS nhưng không xác thực client
        self.client.tls_set()
```

### Kiểm Soát Truy Cập
```python
def check_topic_permission(self, user, topic, operation='subscribe'):
    # Kiểm tra quyền truy cập topic
    topic_obj = self.env['mqtt.topic'].search([('name', '=', topic)])

    if not topic_obj:
        return False

    # Kiểm tra quyền của người dùng
    return self.env['mqtt.access.control'].check_access(user, topic_obj, operation)
```

## Triển Khai
### Cài Đặt Module
1. Đảm bảo thư viện paho-mqtt đã được cài đặt:

### Quản lý dịch vụ MQTT
```text
pip install paho-mqtt
```

2. Thêm module vào đường dẫn addons của Odoo
3. Cài đặt module qua Odoo Apps Store hoặc cài đặt thủ công

### Cấu Hình Ban Đầu
1. Truy cập menu MQTT Configuration
2. Cấu hình các broker và topic mặc định
3. Khởi động dịch vụ MQTT

## Thực Tiễn Tốt Nhất
1. **Sử dụng QoS phù hợp**:
    - QoS 0: Gửi tin nhắn một lần, không đảm bảo gửi thành công
    - QoS 1: Đảm bảo tin nhắn được gửi ít nhất một lần
    - QoS 2: Đảm bảo tin nhắn được gửi đúng một lần

2. **Xử lý kết nối mất**:
    - Luôn kiểm tra trạng thái kết nối trước khi gửi tin nhắn
    - Triển khai cơ chế tái kết nối tự động
    - Sử dụng cờ "Last Will and Testament" để thông báo khi client mất kết nối

3. **Thiết kế Topic**:
    - Sử dụng cấu trúc phân cấp: `/level1/level2/level3`
    - Tránh sử dụng wildcards quá rộng
    - Đặt tên topic có ý nghĩa và nhất quán

4. **Xử lý Payload**:
    - Sử dụng JSON cho dữ liệu có cấu trúc
    - Xác thực và kiểm tra dữ liệu trước khi xử lý
    - Xử lý các trường hợp lỗi dữ liệu

## Gỡ Lỗi
### Ghi Log Chi Tiết
```python
def enable_detailed_logging(self):
    # Bật ghi log chi tiết cho client MQTT
    self.client.enable_logger(_logger)

    # Cấu hình mức log
    logging.getLogger("paho.mqtt").setLevel(logging.DEBUG)
```

### Kiểm Tra Kết Nối
```python
def test_connection(self):
    try:
        # Tạo client tạm thời để kiểm tra kết nối
        test_client = mqtt.Client(client_id=f"odoo_test_{uuid.uuid4().hex}",
                                  callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

        # Thử kết nối
        test_client.connect(self.broker, self.port, 10)
        test_client.disconnect()
        return True
    except Exception as e:
        _logger.error(f"Connection test failed: {e}")
        return False
```

### Giám Sát Hiệu Suất
```python
def start_mqtt_monitor(self):
    # Khởi tạo monitor
    self._message_count = 0
    self._start_time = time.time()

    # Cấu hình callback thống kê
    def on_message_stats(*args):
        self._message_count += 1
        if self._message_count % 100 == 0:
            elapsed = time.time() - self._start_time
            rate = self._message_count / elapsed
            _logger.info(f"MQTT stats: {self._message_count} messages, {rate:.2f} msgs/sec")

    original_on_message = self.client.on_message
    self.client.on_message = lambda *args: (on_message_stats(*args), original_on_message(*args))
```

## Tài liệu tham khảo
1. [Tài liệu Paho MQTT Python](https://www.eclipse.org/paho/index.php?page=clients/python/index.php)
2. [Thông số kỹ thuật MQTT v5.0](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
3. [Hướng dẫn sử dụng MQTT với Odoo](https://www.odoo.com/documentation)
4. [Các mẫu thiết kế cho IoT](https://iot.eclipse.org/community/resources/iot-protocols/)

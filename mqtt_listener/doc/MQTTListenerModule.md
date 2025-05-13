# Tài liệu Module MQTT Listener
### Phần 1: tóm tắt tài liệu
### Phần 2: Chi tiết

# Phần 1
## Tóm tắt tài liệu

Tài liệu MQTT_Listener_Document.md là một hướng dẫn toàn diện về module MQTT Listener, bao gồm:

- Giới thiệu tổng quan về module và mục đích sử dụng
- Các tính năng chính của module
- Cấu trúc thư mục và tệp tin
- Hướng dẫn sử dụng chi tiết
- Mô tả về luồng hoạt động của module
- Thông số kỹ thuật của kết nối MQTT
- Hướng dẫn xử lý sự cố
- Yêu cầu hệ thống
- Hướng dẫn phát triển và tùy chỉnh

Tài liệu này sẽ giúp người dùng và nhà phát triển hiểu rõ về cách hoạt động của module MQTT Listener, cách sử dụng và cách mở rộng nó cho các nhu cầu cụ thể.

# Phần 2
## Giới thiệu

Module MQTT Listener là một giải pháp tích hợp Odoo với các thiết bị IoT và dịch vụ bên ngoài thông qua giao thức MQTT. Module này tạo ra kênh giao tiếp hai chiều giữa Odoo và các hệ thống bên ngoài, cho phép việc nhận, xử lý và gửi tin nhắn MQTT.

## Các tính năng chính

- Kết nối Odoo với broker MQTT và lắng nghe các topic đã đăng ký
- Quản lý dịch vụ MQTT (khởi động, dừng, kiểm tra trạng thái) từ giao diện Odoo
- Lưu lịch sử tin nhắn gửi và nhận
- Gửi tin nhắn MQTT từ Odoo đến các thiết bị/hệ thống khác
- Tự động kết nối lại khi mất kết nối
- Tự động khởi động dịch vụ khi Odoo khởi động

## Cách sử dụng

### Quản lý dịch vụ MQTT

1. **Truy cập menu MQTT Service:**
   - Đường dẫn: `MQTT → MQTT Service`
   - Hiển thị thông tin về trạng thái dịch vụ MQTT hiện tại

2. **Khởi động dịch vụ:**
   - Nhấn nút "Khởi động Dịch vụ" từ giao diện
   - Trạng thái dịch vụ sẽ chuyển sang "Đang chạy"
   - Trạng thái kết nối ban đầu sẽ là "Đang kết nối" và sau đó chuyển sang "Đã kết nối" khi kết nối thành công

3. **Dừng dịch vụ:**
   - Nhấn nút "Dừng Dịch vụ" để ngừng lắng nghe MQTT
   - Trạng thái dịch vụ sẽ chuyển sang "Đã dừng"

### Gửi tin nhắn MQTT

1. **Truy cập menu Messages:**
   - Đường dẫn: `MQTT → Messages`
   - Nhấn "Tạo mới" để tạo tin nhắn mới

2. **Cấu hình tin nhắn:**
   - Chọn Broker và Subscription (topic)
   - Nhập nội dung tin nhắn vào trường Payload
   - Thiết lập các tham số QoS và Retain nếu cần

3. **Gửi tin nhắn:**
   - Nhấn nút "Gửi" để gửi tin nhắn
   - Tin nhắn sẽ được lưu vào lịch sử gửi

### Xem lịch sử tin nhắn

- Trong form chi tiết tin nhắn, phần "Send/receive history" hiển thị lịch sử gửi/nhận tin nhắn theo từng topic
- Tin nhắn đến sẽ tự động được ghi vào lịch sử này

## Luồng hoạt động

### Khởi động dịch vụ

1. **Khởi động tự động:**
   - Khi module được cài đặt, hàm `_post_init_hook` được gọi để khởi động dịch vụ
   - Sau mỗi lần khởi động Odoo, hàm `_auto_start_mqtt` tự động kích hoạt dịch vụ

2. **Khởi động thủ công:**
   - Người dùng nhấn "Khởi động Dịch vụ" trong giao diện
   - Hệ thống tạo thread MQTTListener mới với định danh duy nhất
   - Thread được lưu trong biến toàn cục `MQTT_THREADS` để theo dõi

### Lắng nghe MQTT

1. **Kết nối và đăng ký topic:**
   - Thread kết nối đến broker MQTT (mặc định: broker.emqx.io:1883)
   - Đăng ký các topic cấu hình: "mqtt/control" và "mqtt/#"

2. **Xử lý tin nhắn:**
   - Khi nhận được tin nhắn, callback `on_message` được gọi
   - Tin nhắn được giải mã và lưu vào bảng `mqtt.message.history`
   - Thông tin về tin nhắn được ghi vào log hệ thống

3. **Duy trì kết nối:**
   - Thread liên tục kiểm tra trạng thái kết nối
   - Nếu mất kết nối, tự động thử kết nối lại sau mỗi 5 giây
   - Gửi ping định kỳ để đảm bảo kết nối vẫn hoạt động

### Gửi tin nhắn

1. **Khởi tạo kết nối tạm thời:**
   - Khi gửi tin nhắn, hệ thống tạo kết nối tạm thời đến broker
   - Gửi tin nhắn đến topic với các tham số đã cấu hình
   - Ngắt kết nối sau khi gửi xong

2. **Cập nhật lịch sử:**
   - Tin nhắn gửi được lưu vào lịch sử với hướng "send"
   - Lưu thông tin thời gian, topic, payload, QoS và Retain

### Dừng dịch vụ

1. **Dừng thủ công:**
   - Người dùng nhấn "Dừng Dịch vụ"
   - Thread MQTTListener nhận tín hiệu dừng (`stop()`)
   - Thread ngắt kết nối MQTT và kết thúc an toàn
   - Thông tin thread được xóa khỏi `MQTT_THREADS`

2. **Dừng tự động:**
   - Khi gỡ cài đặt module, hàm `_uninstall_hook` dừng dịch vụ
   - Khi Odoo tắt, thread tự động kết thúc (daemon thread)

## Thông số kỹ thuật

- **Broker mặc định:** broker.emqx.io
- **Cổng mặc định:** 1883
- **Topics mặc định:** "mqtt/control" (QoS 0), "mqtt/#" (QoS 0)
- **Keepalive:** 30 giây
- **Thời gian tái kết nối:** 5 giây
- **Client ID format:** odoo_mqtt_listener_{thread_id}

## Xử lý sự cố

### Không thể kết nối đến broker

1. **Kiểm tra kết nối mạng:**
   - Xác nhận máy chủ có thể truy cập Internet
   - Kiểm tra tường lửa không chặn cổng 1883

2. **Kiểm tra broker:**
   - Xác minh broker hoạt động và có thể truy cập
   - Thử kết nối thủ công:
   ```
   telnet broker.emqx.io 1883
   ```

3. **Xem logs:**
   - Kiểm tra logs Odoo để xem thông tin lỗi chi tiết

### Không nhận được tin nhắn

1. **Kiểm tra trạng thái dịch vụ:**
   - Xác nhận dịch vụ đang ở trạng thái "Đang chạy"
   - Kiểm tra trạng thái kết nối là "Đã kết nối"

2. **Kiểm tra topic:**
   - Xác nhận đã đăng ký đúng topic
   - Sử dụng công cụ MQTT khác để kiểm tra topic đang hoạt động

3. **Gửi tin nhắn thử:**
   - Gửi tin nhắn thử nghiệm đến topic đã đăng ký

### Hiệu suất kém

1. **Giảm số lượng topic:**
   - Hạn chế sử dụng wildcards (#, +) quá rộng
   - Chỉ đăng ký các topic cần thiết

2. **Tối ưu xử lý tin nhắn:**
   - Đảm bảo xử lý tin nhắn hiệu quả trong callback `on_message`

3. **Kiểm tra tài nguyên:**
   - Đảm bảo server có đủ CPU và RAM

## Yêu cầu hệ thống

- Odoo v16 hoặc cao hơn
- Python 3.8+
- Thư viện: paho-mqtt (`pip install paho-mqtt`)
- Module phụ thuộc: mqtt_abstract_interface

## Phát triển và tùy chỉnh

### Thêm broker mới

Để thêm hoặc thay đổi broker, chỉnh sửa file `controllers/listener.py`:

```python
self.broker = "your-broker-address"
self.port = 1883  # Hoặc cổng khác
```

### Thêm xử lý tin nhắn tùy chỉnh

Mở rộng phương thức `on_message` trong file `controllers/listener.py` để thêm logic xử lý:

```python
def on_message(self, client, userdata, msg, properties=None):
    payload = msg.payload.decode(errors='ignore')
    _logger.info(f"Received message on {msg.topic}: {payload}")

    # Thêm xử lý tùy chỉnh ở đây
    if msg.topic == "mqtt/special/topic":
        # Xử lý đặc biệt cho topic này
        pass

    # Lưu tin nhắn vào database
    try:
        with self.registry.cursor() as cr:
            env = Environment(cr, SUPERUSER_ID, {})
            env['mqtt.message.history'].create({
                'topic': msg.topic,
                'message_id': False,
                'payload': payload,
                'qos': msg.qos,
                'direction': 'receive',
                'retain': msg.retain,
            })
            cr.commit()
    except Exception as e:
        _logger.error(f"Error processing MQTT message: {e}", exc_info=True)
```

# Hướng dẫn Kỹ thuật - MQTT Listener

Tài liệu này cung cấp thông tin chi tiết về cách hoạt động, kiến trúc và các thông số kỹ thuật của module MQTT Listener.

## Kiến trúc hệ thống

### Các thành phần chính

1. **MQTT Service Manager**:
   - Model: `mqtt.service`
   - Quản lý dịch vụ MQTT, bao gồm khởi động, dừng và kiểm tra trạng thái của dịch vụ
   - Lưu trữ thông tin về trạng thái hiện tại của dịch vụ và thread đang chạy

2. **MQTT Listener**:
   - Class: `MQTTListener` (controllers/listener.py)
   - Thread chạy nền để lắng nghe và xử lý tin nhắn MQTT từ các broker
   - Xử lý kết nối, ngắt kết nối và tái kết nối tự động

3. **Lưu trữ tin nhắn MQTT**:
   - Models: `mqtt.message`, `mqtt.message.history`
   - Lưu lịch sử các tin nhắn gửi và nhận

## Luồng hoạt động chi tiết

### Luồng khởi động dịch vụ

1. **Khởi động tự động khi cài đặt**:
   - Khi module được cài đặt, hàm `_post_init_hook` được gọi để tự động khởi động dịch vụ MQTT
   - Sau mỗi lần khởi động Odoo, hàm `_auto_start_mqtt` sẽ tự động kích hoạt dịch vụ

2. **Khởi động thủ công**:
   ```
   Người dùng → MQTT Service UI → start_mqtt_service() → Tạo MQTTListener → Lưu thông tin thread
   ```
   - Người dùng nhấn nút "Khởi động Dịch vụ" trong giao diện MQTT Service
   - Hệ thống gọi phương thức `start_mqtt_service()` trên model `mqtt.service`
   - Một thread MQTTListener mới được tạo với một định danh duy nhất
   - Thông tin về thread được lưu vào biến toàn cục `MQTT_THREADS` để theo dõi
   - Phương thức `start()` được gọi để khởi động thread
   - Cập nhật trạng thái dịch vụ trong cơ sở dữ liệu

### Luồng lắng nghe MQTT

1. **Khởi tạo kết nối**:
   ```
   MQTTListener.run() → Kết nối broker → Đăng ký topic → on_connect()
   ```
   - Thread MQTTListener kết nối đến broker MQTT (mặc định là broker.emqx.io)
   - Khi kết nối thành công, callback `on_connect` được gọi
   - Đăng ký (subscribe) vào các topic đã cấu hình, ví dụ: "mqtt/control" và "mqtt/#"

2. **Xử lý tin nhắn nhận được**:
   ```
   Nhận tin nhắn → on_message() → Lưu vào mqtt.message.history
   ```
   - Khi có tin nhắn gửi đến các topic đã đăng ký, hàm `on_message` được gọi
   - Tin nhắn được giải mã và lưu vào bảng `mqtt.message.history`
   - Thông tin về tin nhắn được hiển thị trong log

3. **Duy trì kết nối**:
   ```
   Vòng lặp → Kiểm tra kết nối → Tái kết nối nếu cần → Gửi ping định kỳ
   ```
   - Thread thực hiện vòng lặp liên tục kiểm tra trạng thái kết nối
   - Nếu kết nối bị mất, hệ thống sẽ tự động thử kết nối lại sau một khoảng thời gian chờ
   - Gửi ping định kỳ để đảm bảo kết nối vẫn hoạt động

### Luồng gửi tin nhắn MQTT

1. **Tạo tin nhắn**:
   ```
   Người dùng → Tạo tin nhắn → Nhập nội dung, chọn topic
   ```
   - Người dùng tạo tin nhắn mới trong hệ thống với payload và topic

2. **Kết nối và gửi**:
   ```
   action_send_mqtt() → Kết nối broker → Gửi tin nhắn → Ngắt kết nối
   ```
   - Khi nhấn nút "Gửi", hệ thống gọi phương thức `action_send_mqtt()`
   - Hệ thống tạo kết nối tạm thời đến broker
   - Gửi tin nhắn đến topic đã chọn với các tham số đã cấu hình (QoS, Retain)
   - Ngắt kết nối tạm thời

3. **Lưu lịch sử**:
   ```
   Gửi thành công → Cập nhật thông tin → Lưu vào lịch sử
   ```
   - Khi tin nhắn được gửi thành công, hệ thống cập nhật thời điểm gửi
   - Tạo bản ghi mới trong `mqtt.message.history` với hướng 'send'

### Luồng dừng dịch vụ

1. **Dừng thủ công**:
   ```
   Người dùng → MQTT Service UI → stop_mqtt_service() → Dừng thread → Xóa khỏi danh sách
   ```
   - Người dùng nhấn nút "Dừng Dịch vụ" 
   - Hệ thống gọi phương thức `stop_mqtt_service()` trên model `mqtt.service`
   - Lấy thread từ biến toàn cục `MQTT_THREADS` bằng định danh
   - Gọi phương thức `stop()` để gửi tín hiệu dừng đến thread
   - Thread hoàn thành các tác vụ còn lại và kết thúc
   - Xóa thread khỏi biến toàn cục `MQTT_THREADS`

2. **Dừng tự động**:
   - Khi gỡ cài đặt module, hàm `_uninstall_hook` được gọi để dừng dịch vụ
   - Khi server Odoo tắt, thread tự động kết thúc do được đặt là daemon thread

## Thông số kỹ thuật

### Cấu hình MQTT mặc định

- **Broker**: broker.emqx.io
- **Port**: 1883
- **Topics**:
  - mqtt/control (QoS 0)
  - mqtt/# (QoS 0)
- **Keepalive**: 30 giây
- **Reconnect delay**: 5 giây
- **Client ID**: Tự động tạo theo định dạng `odoo_mqtt_listener_{thread_id}`

### Thông tin thread

- **Daemon**: True (tự động kết thúc khi chương trình chính kết thúc)
- **Lưu trữ thread**: Biến toàn cục `MQTT_THREADS` dạng dict lưu trữ theo định danh

### Xử lý sự kiện MQTT

- **on_connect**: Khi kết nối thành công, đăng ký vào tất cả các topic đã cấu hình
- **on_disconnect**: Ghi nhận sự kiện ngắt kết nối và cập nhật trạng thái
- **on_message**: Lưu tin nhắn vào cơ sở dữ liệu và ghi log
- **on_subscribe**: Ghi nhận sự kiện đăng ký topic thành công
- **on_log**: Ghi log các sự kiện liên quan đến kết nối MQTT

## Khả năng mở rộng

### Thêm broker mới

- Có thể cập nhật model để hỗ trợ nhiều broker khác nhau
- Thêm giao diện cấu hình broker trong màn hình quản lý dịch vụ

### Xử lý nâng cao

- Hỗ trợ thêm các callback xử lý tin nhắn tùy chỉnh
- Thêm khả năng lọc và định tuyến tin nhắn theo topic
- Tích hợp với các module khác để xử lý sự kiện khi nhận tin nhắn
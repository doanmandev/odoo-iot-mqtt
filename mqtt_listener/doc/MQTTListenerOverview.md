# MQTT Listener - Tổng quan sử dụng

Module MQTT Listener là một giải pháp tích hợp để kết nối Odoo với các thiết bị IoT và dịch vụ bên ngoài thông qua giao thức MQTT. Module này cho phép hệ thống Odoo nhận, xử lý và gửi tin nhắn MQTT, tạo ra một kênh giao tiếp hai chiều giữa Odoo và các hệ thống bên ngoài.

## Các tính năng chính

- Quản lý dịch vụ MQTT từ giao diện Odoo
- Lắng nghe và xử lý tin nhắn MQTT từ các broker
- Gửi tin nhắn MQTT đến các topic
- Lưu lịch sử tin nhắn MQTT gửi/nhận
- Tự động khởi động dịch vụ khi Odoo khởi động
- Duy trì kết nối ổn định với broker MQTT

## Hướng dẫn sử dụng cơ bản

### Thiết lập và khởi động dịch vụ

1. **Truy cập menu MQTT Service**:
   - Đi tới menu `MQTT Service` (nằm trong menu gốc MQTT)
   - Hệ thống sẽ hiển thị giao diện quản lý dịch vụ MQTT

2. **Khởi động dịch vụ**:
   - Nhấn nút "Khởi động Dịch vụ" để bắt đầu dịch vụ MQTT Listener
   - Sau khi khởi động, trạng thái sẽ chuyển sang "Đang chạy"
   - Trạng thái kết nối lúc đầu sẽ là "Đang kết nối", và sau đó chuyển sang "Đã kết nối" khi kết nối đến broker thành công

3. **Dừng dịch vụ**:
   - Nhấn nút "Dừng Dịch vụ" để tạm dừng dịch vụ
   - Sau khi dừng, trạng thái sẽ chuyển sang "Đã dừng"

### Gửi tin nhắn MQTT

1. **Truy cập menu Messages**:
   - Đi tới menu `Messages` trong mục MQTT
   - Nhấn "Tạo mới" để tạo tin nhắn mới

2. **Điền thông tin**:
   - Chọn Broker MQTT từ danh sách có sẵn
   - Chọn Subscription (topic) mục tiêu
   - Nhập nội dung tin nhắn vào trường Payload
   - Tùy chỉnh các thông số QoS và Retain nếu cần

3. **Gửi tin nhắn**:
   - Nhấn nút "Gửi" để gửi tin nhắn
   - Hệ thống sẽ ghi nhận thời điểm gửi và thêm vào lịch sử tin nhắn

### Xem lịch sử tin nhắn

- Trong form chi tiết tin nhắn, phần "Send/receive history" sẽ hiển thị lịch sử gửi/nhận tin nhắn theo từng topic
- Tin nhắn nhận từ broker sẽ được tự động ghi vào lịch sử này

## Tài liệu liên quan

Để biết thêm thông tin chi tiết về cách hoạt động và thông số kỹ thuật của module, vui lòng tham khảo:

- [Hướng dẫn kỹ thuật](technical_guide.md) - Chi tiết về luồng hoạt động và thông số kỹ thuật
- [Khắc phục sự cố](troubleshooting.md) - Hướng dẫn xử lý các vấn đề thường gặp

## Yêu cầu

- Odoo v16
- Thư viện Python: paho-mqtt
- Module phụ thuộc: mqtt_integration
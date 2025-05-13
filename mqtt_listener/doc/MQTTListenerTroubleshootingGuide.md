# Khắc phục sự cố - MQTT Listener

Tài liệu này cung cấp hướng dẫn giải quyết các vấn đề phổ biến khi sử dụng module MQTT Listener.

## Vấn đề kết nối

### Không thể kết nối đến broker

**Triệu chứng:** Dịch vụ trong trạng thái "Đang chạy" nhưng trạng thái kết nối là "Đang kết nối" hoặc "Mất kết nối"

**Giải pháp:**

1. **Kiểm tra kết nối mạng:**
   - Xác nhận máy chủ Odoo có thể kết nối Internet (nếu sử dụng broker public)
   - Kiểm tra tường lửa không chặn cổng MQTT (mặc định 1883)

   ```bash
   # Kiểm tra kết nối tới broker
   ping broker.emqx.io
   
   # Kiểm tra cổng MQTT
   telnet broker.emqx.io 1883
   ```

2. **Kiểm tra cấu hình broker:**
   - Xác minh thông tin broker trong mã nguồn là chính xác
   - Sửa đổi cấu hình trong file `controllers/listener.py` nếu cần

3. **Kiểm tra logs:**
   - Xem logs của Odoo để biết thông tin chi tiết về lỗi kết nối:
   
   ```bash
   # Xem logs
   tail -f /path/to/odoo/log/odoo.log | grep MQTT
   ```

4. **Khởi động lại dịch vụ:**
   - Dừng và khởi động lại dịch vụ từ giao diện
   - Nếu không hiệu quả, khởi động lại toàn bộ server Odoo

### Kết nối không ổn định

**Triệu chứng:** Dịch vụ MQTT liên tục ngắt kết nối và kết nối lại

**Giải pháp:**

1. **Tăng thời gian keepalive:**
   - Điều chỉnh thông số keepalive trong file `controllers/listener.py`:
   
   ```python
   # Tăng từ 30 lên 60
   keepalive = 60
   ```

2. **Kiểm tra tải tài nguyên:**
   - Đảm bảo server Odoo có đủ tài nguyên (CPU, RAM)
   - Kiểm tra không có quá nhiều connections đến broker

3. **Điều chỉnh thời gian tái kết nối:**
   - Tăng thời gian chờ giữa các lần kết nối lại:
   
   ```python
   self._reconnect_delay = 10  # Tăng từ 5 lên 10 giây
   ```

## Vấn đề về tin nhắn

### Không nhận được tin nhắn

**Triệu chứng:** Dịch vụ đang chạy và kết nối thành công, nhưng không nhận được tin nhắn

**Giải pháp:**

1. **Kiểm tra đăng ký topic:**
   - Xác minh đã đăng ký đúng topic trong file `controllers/listener.py`
   - Đảm bảo không có lỗi cú pháp trong chuỗi topic

2. **Kiểm tra bằng công cụ khác:**
   - Sử dụng MQTT client khác (như MQTT Explorer) để kiểm tra việc nhận tin nhắn
   - Gửi tin nhắn thử nghiệm để kiểm tra

   ```bash
   # Sử dụng mosquitto_pub để gửi tin nhắn thử
   mosquitto_pub -h broker.emqx.io -t "mqtt/control" -m "test message"
   ```

3. **Kiểm tra log và quyền truy cập:**
   - Xem logs để tìm các lỗi khi xử lý tin nhắn
   - Kiểm tra quyền truy cập cơ sở dữ liệu cho model `mqtt.message.history`

### Tin nhắn gửi thất bại

**Triệu chứng:** Không thể gửi tin nhắn MQTT từ giao diện Odoo

**Giải pháp:**

1. **Kiểm tra kết nối broker:**
   - Đảm bảo broker có thể truy cập được
   - Xác minh thông tin đăng nhập broker nếu có

2. **Kiểm tra quyền đăng ký topic:**
   - Đảm bảo topic đích không bị hạn chế quyền ghi
   - Xác minh định dạng topic là hợp lệ

3. **Kiểm tra payload:**
   - Đảm bảo kích thước payload không vượt quá giới hạn
   - Kiểm tra định dạng payload phù hợp

## Vấn đề hiệu suất

### Tiêu tốn nhiều tài nguyên

**Triệu chứng:** Dịch vụ MQTT Listener sử dụng quá nhiều CPU hoặc RAM

**Giải pháp:**

1. **Giảm số lượng topics:**
   - Hạn chế số lượng topics đăng ký, đặc biệt là wildcards (#, +)
   - Chỉ đăng ký các topics cần thiết

2. **Tối ưu xử lý tin nhắn:**
   - Điều chỉnh hàm `on_message` để xử lý tin nhắn hiệu quả hơn
   - Cân nhắc thêm logic lọc tin nhắn

3. **Sử dụng QoS thấp hơn:**
   - Sử dụng QoS 0 thay vì QoS 1 hoặc 2 nếu phù hợp

### Cơ sở dữ liệu phình to

**Triệu chứng:** Bảng `mqtt.message.history` phình to nhanh chóng

**Giải pháp:**

1. **Thiết lập quy trình dọn dẹp định kỳ:**
   - Thêm cron job để xóa tin nhắn cũ:
   
   ```xml
   <!-- Trong file data/mqtt_cron.xml -->
   <record id="ir_cron_mqtt_cleanup" model="ir.cron">
       <field name="name">MQTT Message History Cleanup</field>
       <field name="model_id" ref="model_mqtt_message_history"/>
       <field name="state">code</field>
       <field name="code">model.cleanup_old_messages(days=30)</field>
       <field name="interval_number">1</field>
       <field name="interval_type">days</field>
       <field name="numbercall">-1</field>
   </record>
   ```

2. **Thêm phương thức dọn dẹp trong model:**
   ```python
   @api.model
   def cleanup_old_messages(self, days=30):
       """Xóa tin nhắn cũ hơn số ngày chỉ định"""
       cutoff_date = fields.Datetime.now() - timedelta(days=days)
       old_messages = self.search([('create_date', '<', cutoff_date)])
       old_messages.unlink()
       _logger.info(f"Đã xóa {len(old_messages)} tin nhắn MQTT cũ")
   ```

## Vấn đề với thread

### Thread không dừng đúng cách

**Triệu chứng:** Thread MQTT vẫn chạy sau khi dừng dịch vụ hoặc có nhiều thread cùng chạy

**Giải pháp:**

1. **Kiểm tra cơ chế dừng thread:**
   - Xác nhận phương thức `stop()` được gọi và xử lý đúng cách
   - Đảm bảo flag `_stop_event` được kiểm tra thường xuyên

2. **Dọn dẹp thread thủ công:**
   - Sử dụng công cụ quản lý quy trình để xác định và dừng thread zombie:
   
   ```python
   # Script để liệt kê và dừng các thread MQTT còn sót lại
   import threading
   
   for thread in threading.enumerate():
       if "MQTT" in thread.name:
           print(f"Found MQTT thread: {thread.name}")
           # Cách dừng an toàn nếu thread có phương thức stop
           if hasattr(thread, 'stop'):
               thread.stop()
   ```

3. **Khởi động lại Odoo:**
   - Trong trường hợp cần thiết, khởi động lại server Odoo để đảm bảo tất cả thread được dọn dẹp

## Vấn đề nâng cấp

### Lỗi sau khi nâng cấp module

**Triệu chứng:** Dịch vụ MQTT không hoạt động sau khi nâng cấp module

**Giải pháp:**

1. **Cập nhật các phụ thuộc:**
   - Đảm bảo thư viện paho-mqtt được cập nhật lên phiên bản mới nhất
   
   ```bash
   pip install --upgrade paho-mqtt
   ```

2. **Kiểm tra thay đổi API:**
   - Xác nhận mã nguồn tương thích với phiên bản mới của paho-mqtt
   - Cập nhật code nếu có thay đổi trong API

3. **Làm mới dịch vụ:**
   - Xóa bản ghi dịch vụ hiện tại và tạo mới:
   
   ```python
   # Thực hiện trong shell Odoo
   env['mqtt.service'].search([]).unlink()
   env['mqtt.service'].create({})
   env['mqtt.service'].start_mqtt_service()
   ```

## Hỗ trợ thêm

Nếu bạn gặp vấn đề không được đề cập trong tài liệu này, vui lòng:

1. Kiểm tra logs hệ thống để biết thêm thông tin chi tiết
2. Xem mã nguồn trong thư mục module để hiểu rõ hơn về cách triển khai
3. Tham khảo tài liệu của thư viện paho-mqtt
4. Liên hệ với đội phát triển để được hỗ trợ
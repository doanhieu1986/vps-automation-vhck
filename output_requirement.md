# Yêu cầu về output

## Yêu cầu về workflow n8n
    - Workflow n8n sẽ được tạo thành file .json
    - File .json sẽ được lưu tại thư mục `n8n`
    - File .json sẽ được lưu với tên `vps_automation_vhck.json`
    - Workflow được tạo trên n8n thông qua mcp kết nối với Claude Code

## Yêu cầu về giao diện web
    - Giao diện web sẽ được tạo thành file .html, có cấu trúc và định dạng rõ ràng, dễ dàng cho VHCK review thông tin và xác nhận việc sẽ nhập thông tin vào BO. Thông tin hiển thị cần có cả link để xem thông tin gốc hoặc ảnh, hoặc full text để VHCK có thể dễ dàng tra cứu và xác nhận thông tin.
    - Các thông tin thu thập được trên `result.md` sẽ được cập nhật trên giao diện web, bao gồm cả trạng thái `confirmed` và `rejected`. Ngược lại khi người dùng xác nhận hoặc reject thông tin trên giao diện web, hệ thống sẽ tự động cập nhật trạng thái `result.md` thành `confirmed` hoặc `rejected` và hiển thị trạng thái `confirmed` hoặc `rejected` trên giao diện web.
    - File .html sẽ được lưu tại thư mục `web`
    - File .html sẽ được lưu với tên `vps_automation_vhck.html`
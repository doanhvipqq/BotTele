Hướng dẫn triển khai BotTele lên Render

Tổng quan:
- Repo sử dụng polling (main.py gọi bot.infinity_polling()), vì vậy trên Render cần tạo một Background Worker.
- Không commit TELEGRAM_TOKEN vào repo. Thay vào đó, set biến môi trường TELEGRAM_TOKEN trên dashboard Render.

Các bước:
1) Thu hồi hoặc đổi token hiện tại (nếu token đã bị public):
   - Mở Telegram -> @BotFather -> revoke existing token hoặc tạo bot mới để lấy token mới.

2) Xóa hoặc thay thế .env đã chứa token trong repository:
   - Trong repo này mình đã thay .env để bỏ giá trị token. Bạn nên chạy thêm các lệnh git nếu muốn xóa token khỏi lịch sử commit (tùy chọn):
     - Sử dụng BFG hoặc git filter-repo để loại bỏ hoàn toàn token khỏi lịch sử (cẩn thận, thao tác này thay đổi lịch sử Git):
       - Ví dụ với BFG: bfg --delete-files .env  (xem hướng dẫn BFG)

3) Cấu hình trên Render (GUI):
   - Tạo một service mới: chọn "Background Worker".
   - Branch: main
   - Build command: pip install -r requirements.txt
   - Start command: python -u main.py
   - Thêm Environment Variables: TELEGRAM_TOKEN = <token_mới>

4) Tùy chọn: deploy bằng Docker
   - Nếu bạn muốn dùng Docker, Render sẽ dùng Dockerfile có sẵn.

5) Debugging
   - Xem Logs trên Render dashboard nếu service crash.
   - Kiểm tra requirements.txt nếu gặp ModuleNotFoundError.
   - Sử dụng python -u để logs không bị buffer.

Lưu ý bảo mật:
- Không commit token hoặc secrets vào repo.
- Sau khi đổi token, thu hồi token cũ.

Nếu bạn muốn mình tiếp tục: mình có thể tạo Pull Request, hoặc nếu bạn cho phép mình push trực tiếp, mình sẽ thực hiện các thay đổi trên branch main như mô tả.

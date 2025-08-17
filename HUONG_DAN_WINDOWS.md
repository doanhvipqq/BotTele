# Hướng dẫn cài đặt và chạy Bot Telegram trên Windows

## 🚀 Cách 1: Sử dụng file .bat (Đơn giản nhất)

### Cài đặt lần đầu:
1. **Tải và giải nén** project về máy
2. **Double-click** vào file `setup_and_run.bat`
3. **Làm theo hướng dẫn** trên màn hình:
   - Script sẽ tự động kiểm tra Python
   - Cài đặt các thư viện cần thiết
   - Tạo file .env và hướng dẫn nhập token

### Chạy bot (các lần sau):
- **Double-click** vào file `run_bot.bat`

## 🛠️ Cách 2: Sử dụng Command Prompt (CMD)

### Bước 1: Mở CMD
- Nhấn `Win + R`, gõ `cmd`, nhấn Enter
- Hoặc tìm "Command Prompt" trong Start Menu

### Bước 2: Di chuyển đến thư mục bot
```cmd
cd /d "C:\path\to\BotTele"
```
*Thay `C:\path\to\BotTele` bằng đường dẫn thật đến thư mục bot*

### Bước 3: Cài đặt Python (nếu chưa có)
- Tải từ: https://www.python.org/downloads/
- **Quan trọng**: Tick ☑️ "Add Python to PATH" khi cài đặt

### Bước 4: Cài đặt thư viện
```cmd
pip install -r requirements.txt
```

### Bước 5: Thiết lập token bot
```cmd
copy .env.example .env
notepad .env
```
- Thay `your_telegram_bot_token_here` bằng token thật từ @BotFather

### Bước 6: Chạy bot
```cmd
python main.py
```

## 🔑 Cách lấy Token Bot Telegram

1. **Mở Telegram**, tìm kiếm `@BotFather`
2. **Gửi lệnh**: `/newbot`
3. **Đặt tên bot**: Ví dụ "My Awesome Bot"
4. **Đặt username**: Ví dụ "my_awesome_bot" (phải kết thúc bằng "bot")
5. **Copy token** mà BotFather gửi (dạng: `123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)
6. **Paste vào file .env**:
   ```
   TELEGRAM_TOKEN=123456789:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
   ```

## 📁 Cấu trúc thư mục
```
BotTele/
├── setup_and_run.bat    ← Chạy file này lần đầu
├── run_bot.bat          ← Chạy file này các lần sau
├── main.py              ← File chính của bot
├── .env                 ← Chứa token bot (tạo từ .env.example)
├── .env.example         ← Template cho .env
├── requirements.txt     ← Danh sách thư viện cần thiết
└── bot/                 ← Các module chức năng
```

## ⚠️ Lỗi thường gặp

### "python không được nhận dạng..."
- ✅ **Giải pháp**: Cài đặt Python và tick "Add to PATH"
- 🔗 **Link tải**: https://www.python.org/downloads/

### "pip không được nhận dạng..."
- ✅ **Giải pháp**: Cài đặt lại Python với pip
- 📝 **Hoặc**: Chạy `python -m pip install -r requirements.txt`

### "Error 409: Conflict"
- ✅ **Giải pháp**: Đảm bảo không có bot nào khác đang chạy với cùng token
- 🔄 **Hoặc**: Đợi 5-10 phút rồi thử lại

### Bot không phản hồi
- ✅ **Kiểm tra**: Token có đúng không?
- ✅ **Kiểm tra**: Bot có đang chạy không?
- ✅ **Kiểm tra**: Đã add bot vào group chưa?

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. **Kiểm tra lại** từng bước trong hướng dẫn
2. **Đảm bảo** Python và pip đã được cài đặt đúng
3. **Kiểm tra** token bot có chính xác không
4. **Thử chạy** `setup_and_run.bat` với quyền Administrator

---

💡 **Mẹo**: Sử dụng file `.bat` để dễ dàng hơn, không cần nhớ lệnh!

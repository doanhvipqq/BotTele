# BotTele - Telegram Bot

Một bot Telegram đa chức năng được viết bằng Python với nhiều tính năng thú vị.

## 🚀 Tính năng

- **Xử lý hình ảnh**: Các lệnh `/img`, `/img1`, `/cosplay`, `/r34`, `/pixxx`
- **Mạng xã hội**: Share Facebook (`/share`), TikTok info (`/tiktok`)
- **Giải trí**: Meme (`/meme`), reaction (`/reaction`), random content (`/random`)
- **Công cụ**: Encode file (`/encode`), proxy (`/proxy`), search (`/search`)
- **Thông tin**: GitHub profile (`/github`), thông tin user (`/in4`)
- **SMS**: Spam SMS (`/sms`, `/smsvip`) - chỉ dành cho VIP
- **Manga**: Đọc manga (`/lx`, `/lxmanga`)
- **Tiện ích**: Thời gian (`/time`), thumbnail (`/thumb`), help (`/help`)

## 📋 Yêu cầu

- Python 3.12+
- Các thư viện trong `requirements.txt`
- Token bot Telegram từ [@BotFather](https://t.me/botfather)

## 🛠️ Cài đặt

### Cách 1: Sử dụng Batch Scripts (Windows - Đơn giản nhất)

1. **Tải và giải nén** project về máy
2. **Double-click** vào file `setup_and_run.bat`
3. **Làm theo hướng dẫn** trên màn hình
4. **Các lần sau** chỉ cần chạy `run_bot.bat`

📖 **Xem hướng dẫn chi tiết**: [HUONG_DAN_WINDOWS.md](HUONG_DAN_WINDOWS.md)

### Cách 2: Cài đặt thủ công

1. **Clone repository:**
   ```bash
   git clone https://github.com/doanhvipqq/BotTele.git
   cd BotTele
   ```

2. **Cài đặt dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Thiết lập biến môi trường:**
   ```bash
   cp .env.example .env
   ```
   Sau đó chỉnh sửa file `.env` và thêm token bot của bạn:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token_here
   ```

4. **Chạy bot:**
   ```bash
   python main.py
   ```

## ⚙️ Cấu hình

- Chỉnh sửa `config.py` để thay đổi:
  - `ADMIN_ID`: ID Telegram của admin
  - `GROUP_ID`: Danh sách các nhóm được phép sử dụng bot
  - `ERROR_MSG`: Thông báo lỗi mặc định

## 📝 Lệnh bot

### Lệnh cơ bản:
- `/help` - Hiển thị danh sách lệnh
- `/time` - Hiển thị thời gian hiện tại
- `/in4` - Thông tin người dùng

### Hình ảnh và giải trí:
- `/img [tag]` - Tìm hình ảnh
- `/img1 [tag]` - Tìm hình ảnh (phiên bản 2)
- `/cosplay` - Hình ảnh cosplay
- `/meme` - Hình ảnh meme ngẫu nhiên
- `/reaction` - Reaction ngẫu nhiên

### Công cụ:
- `/encode` - Encode file Python
- `/proxy` - Lấy proxy ngẫu nhiên
- `/search [query]` - Tìm kiếm trên web
- `/github [username]` - Thông tin GitHub profile

### Mạng xã hội:
- `/share [id] [số lượng]` - Share Facebook
- `/tiktok [url]` - Thông tin video TikTok

### VIP (yêu cầu quyền admin):
- `/sms [số] [vòng lặp]` - Spam SMS
- `/smsvip [số] [vòng lặp]` - Spam SMS VIP
- `/add [user_id]` - Thêm user vào VIP

## 🔒 Bảo mật

- File `.env` chứa token nhạy cảm đã được loại trừ khỏi git
- Chỉ admin mới có thể sử dụng một số lệnh nhất định
- Giới hạn thời gian sử dụng cho một số lệnh

## 📂 Cấu trúc project

```
BotTele/
├── setup_and_run.bat    # Windows: Cài đặt và chạy tự động
├── run_bot.bat          # Windows: Chạy nhanh bot
├── HUONG_DAN_WINDOWS.md # Hướng dẫn chi tiết cho Windows
├── main.py              # File chính để chạy bot
├── config.py            # Cấu hình bot
├── requirements.txt     # Dependencies
├── .env.example         # Template cho biến môi trường
├── .gitignore          # Git ignore rules
└── bot/                # Các module chức năng
    ├── encode.py       # Encode files
    ├── img.py          # Xử lý hình ảnh
    ├── share.py        # Share Facebook
    ├── spamsms.py      # Spam SMS
    └── ...             # Các module khác
```

## 🤝 Đóng góp

1. Fork repository
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📞 Liên hệ

- GitHub: [@doanhvipqq](https://github.com/doanhvipqq)
- Telegram Bot: [@doanhcccvip_bot](https://t.me/doanhcccvip_bot)

---

⭐ **Nếu project này hữu ích, hãy cho một star nhé!** ⭐

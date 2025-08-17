@echo off
chcp 65001 >nul
title Bot Telegram - Cài đặt và Chạy
color 0A

echo ===============================================
echo           BOT TELEGRAM - CÀI ĐẶT
echo ===============================================
echo.

REM Kiểm tra Python
echo [1/5] Kiểm tra Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python chưa được cài đặt!
    echo 📥 Vui lòng tải Python từ: https://www.python.org/downloads/
    echo ⚠️  Nhớ tick "Add Python to PATH" khi cài đặt
    pause
    exit /b 1
) else (
    echo ✅ Python đã được cài đặt
)

REM Kiểm tra pip
echo [2/5] Kiểm tra pip...
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip không khả dụng!
    pause
    exit /b 1
) else (
    echo ✅ pip đã sẵn sàng
)

REM Cài đặt dependencies
echo [3/5] Cài đặt thư viện cần thiết...
echo 📦 Đang cài đặt packages từ requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Lỗi khi cài đặt thư viện!
    pause
    exit /b 1
) else (
    echo ✅ Đã cài đặt thành công tất cả thư viện
)

REM Kiểm tra file .env
echo [4/5] Kiểm tra cấu hình...
if not exist .env (
    echo ⚠️  File .env chưa tồn tại!
    echo 📝 Đang tạo file .env từ template...
    copy .env.example .env >nul
    echo.
    echo 🔑 QUAN TRỌNG: Bạn cần thêm token bot vào file .env
    echo 📂 Mở file .env và thay đổi:
    echo    TELEGRAM_TOKEN=your_telegram_bot_token_here
    echo 👉 Thành token thật của bạn từ @BotFather
    echo.
    echo 📋 Hướng dẫn lấy token:
    echo    1. Mở Telegram, tìm @BotFather
    echo    2. Gửi /newbot và làm theo hướng dẫn
    echo    3. Copy token và paste vào file .env
    echo.
    pause
    notepad .env
) else (
    echo ✅ File .env đã tồn tại
    findstr /C:"your_telegram_bot_token_here" .env >nul
    if not errorlevel 1 (
        echo ⚠️  Token bot chưa được thiết lập!
        echo 🔑 Vui lòng chỉnh sửa file .env với token thật
        pause
        notepad .env
    )
)

echo [5/5] Kiểm tra hoàn tất!
echo.
echo ===============================================
echo           CHUẨN BỊ CHẠY BOT
echo ===============================================
echo.
echo 🚀 Nhấn Enter để chạy bot...
pause >nul

REM Chạy bot
cls
title Bot Telegram - Đang chạy
echo ===============================================
echo           BOT TELEGRAM - ĐANG CHẠY
echo ===============================================
echo.
echo 🤖 Bot đang khởi động...
echo 📱 Có thể kiểm tra bot trên Telegram
echo 🛑 Nhấn Ctrl+C để dừng bot
echo.

python main.py

echo.
echo ===============================================
echo 🛑 Bot đã dừng hoạt động
echo 📝 Nhấn Enter để thoát...
pause >nul

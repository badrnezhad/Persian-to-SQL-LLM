# دستیار فارسی MySQL

یک پروژه‌ی کوچک Flask که دستور فارسی را با OpenAI API به SQL تبدیل می‌کند، روی MySQL اجرا می‌کند و ۱۰ ردیف آخر جدول‌های `users`، `products` و `orders` را نشان می‌دهد.

## راه‌اندازی

پیش‌نیازها: Python 3.10+ و MySQL 8+.

1. محیط مجازی و وابستگی‌ها را نصب کنید:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. دیتابیس و جدول‌ها را بسازید. این فایل شامل چند ردیف آزمایشی هم هست:

   ```bash
   mysql -u root -p < schema.sql
   ```

3. کاربر محدود برنامه را در MySQL بسازید (رمز را عوض کنید):

   ```sql
   CREATE USER 'sql_chat_app'@'127.0.0.1' IDENTIFIED BY 'change_this_password';
   GRANT SELECT, INSERT, UPDATE, DELETE ON persian_sql_chat.* TO 'sql_chat_app'@'127.0.0.1';
   ```

4. تنظیمات نمونه را کپی و مقادیر را تکمیل کنید:

   ```bash
   cp .env.example .env
   ```

   `OPENAI_API_KEY`، `DB_PASSWORD` و `FLASK_SECRET_KEY` را در `.env` قرار دهید. کلید API در مرورگر قرار نمی‌گیرد و فقط در سرور استفاده می‌شود.

5. برنامه را اجرا کنید:

   ```bash
   python app.py
   ```

   سپس `http://127.0.0.1:5000` را باز کنید.

## نکته‌ی امنیتی

SQL مدل قبل از اجرا با `sqlglot` بررسی می‌شود: فقط یک دستور `SELECT`، `INSERT`، `UPDATE` یا `DELETE` و فقط برای سه جدول مجاز پذیرفته می‌شود. کاربر MySQL برنامه را با مجوزهای محدود بسازید و این نمونه را بدون احراز هویت روی اینترنت عمومی منتشر نکنید.

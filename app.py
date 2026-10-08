import os
import re

import pymysql
import sqlglot
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from openai import OpenAI
from sqlglot import exp

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "local-development-only")

TABLES = {"users", "products", "orders"}
SCHEMA_DESCRIPTION = """
MySQL schema:
- users(id, name, email, created_at)
- products(id, name, price, stock, created_at)
- orders(id, user_id, product_id, quantity, status, created_at)
Use these exact table and column names. For questions about recent rows,
use ORDER BY id DESC. Return one SQL statement only, without markdown fences.
"""


def db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "sql_chat_app"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "persian_sql_chat"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=5,
    )


def generate_sql(user_text):
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("کلید OPENAI_API_KEY در فایل .env تنظیم نشده است.")
    client = OpenAI()
    response = client.responses.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        instructions=(
            "Translate the user's Persian request into exactly one MySQL statement. "
            "Only generate SELECT, INSERT, UPDATE, or DELETE statements against "
            "users, products, and orders. Never generate DDL, grants, stored procedures, "
            "or statements that access other tables. If the request is ambiguous or "
            "outside scope, return exactly: UNSUPPORTED.\n" + SCHEMA_DESCRIPTION
        ),
        input=user_text,
    )
    return response.output_text.strip()


def validate_sql(sql):
    sql = re.sub(r"^```(?:sql)?\s*|\s*```$", "", (sql or "").strip(), flags=re.IGNORECASE)
    if not sql or sql.rstrip(";.").upper() == "UNSUPPORTED":
        raise ValueError("برای این درخواست نتوانستم کوئری مجاز بسازم.")
    try:
        statements = [stmt for stmt in sqlglot.parse(sql, read="mysql") if stmt is not None]
    except sqlglot.errors.ParseError as exc:
        raise ValueError("SQL تولیدشده معتبر نیست.") from exc
    if len(statements) != 1:
        raise ValueError("فقط اجرای یک کوئری در هر درخواست مجاز است.")
    tree = statements[0]
    if not isinstance(tree, (exp.Select, exp.Insert, exp.Update, exp.Delete)):
        raise ValueError("فقط SELECT، INSERT، UPDATE و DELETE مجاز هستند.")
    cte_names = {
        cte.alias_or_name.lower()
        for cte in tree.find_all(exp.CTE)
        if cte.alias_or_name
    }
    base_tables = []
    for table in tree.find_all(exp.Table):
        table_name = table.name.lower()
        if not table.db and not table.catalog and table_name in cte_names:
            continue
        if table.db or table.catalog or table_name not in TABLES:
            raise ValueError("این کوئری به جدول مجاز دسترسی ندارد.")
        base_tables.append(table_name)
    if not base_tables:
        raise ValueError("کوئری باید به یکی از جدول‌های مجاز دسترسی داشته باشد.")
    if isinstance(tree, (exp.Update, exp.Delete)) and tree.args.get("where") is None:
        raise ValueError("برای UPDATE و DELETE باید شرط WHERE مشخص شود.")
    return tree.sql(dialect="mysql")


def execute_sql(sql):
    connection = db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql)
            if cursor.description:
                result = {"kind": "rows", "columns": [d[0] for d in cursor.description], "rows": cursor.fetchall()}
            else:
                result = {"kind": "write", "affected_rows": cursor.rowcount}
        connection.commit()
        return result
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/tables")
def table_data():
    connection = db_connection()
    try:
        tables = {}
        with connection.cursor() as cursor:
            for name in ("users", "products", "orders"):
                cursor.execute(f"SELECT * FROM `{name}` ORDER BY id DESC LIMIT 10")
                tables[name] = {"columns": [d[0] for d in cursor.description], "rows": cursor.fetchall()}
        return jsonify(tables)
    finally:
        connection.close()


@app.post("/api/chat")
def chat():
    body = request.get_json(silent=True) or {}
    user_text = str(body.get("message", "")).strip()
    if not user_text:
        return jsonify(error="دستور خالی است."), 400
    if len(user_text) > 1500:
        return jsonify(error="دستور خیلی طولانی است (حداکثر ۱۵۰۰ نویسه)."), 400
    try:
        sql = validate_sql(generate_sql(user_text))
        result = execute_sql(sql)
        return jsonify(sql=sql, result=result)
    except ValueError as exc:
        return jsonify(error=str(exc)), 400
    except Exception:
        app.logger.exception("Chat request failed")
        return jsonify(error="خطا در ارتباط با سرویس هوش مصنوعی یا دیتابیس. تنظیمات و گزارش سرور را بررسی کنید."), 500


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=False)

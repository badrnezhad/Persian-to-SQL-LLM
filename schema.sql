-- Run this file in MySQL as an administrator.
CREATE DATABASE IF NOT EXISTS persian_sql_chat
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE persian_sql_chat;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(120) NOT NULL,
  email VARCHAR(190) NOT NULL UNIQUE,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS products (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(160) NOT NULL,
  price DECIMAL(12, 2) NOT NULL,
  stock INT UNSIGNED NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS orders (
  id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT UNSIGNED NOT NULL,
  product_id BIGINT UNSIGNED NOT NULL,
  quantity INT UNSIGNED NOT NULL DEFAULT 1,
  status VARCHAR(40) NOT NULL DEFAULT 'pending',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_orders_user FOREIGN KEY (user_id) REFERENCES users(id),
  CONSTRAINT fk_orders_product FOREIGN KEY (product_id) REFERENCES products(id)
) ENGINE=InnoDB;

-- Optional demo rows:
INSERT IGNORE INTO users (id, name, email) VALUES
  (1, 'علی رضایی', 'ali@example.com'),
  (2, 'مینا احمدی', 'mina@example.com');

INSERT IGNORE INTO products (id, name, price, stock) VALUES
  (1, 'دفتر یادداشت', 125000, 30),
  (2, 'خودکار آبی', 25000, 100),
  (3, 'ماگ سرامیکی', 210000, 12);

INSERT IGNORE INTO orders (id, user_id, product_id, quantity, status) VALUES
  (1, 1, 1, 2, 'paid'),
  (2, 2, 3, 1, 'pending');

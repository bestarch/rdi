import os
import sys
import time
import mysql.connector

MYSQL_HOST = os.getenv("MYSQL_HOST", "127.0.0.1")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "admin")

parts = []
parts.append(f"drop schema if exists sample_shop;")
parts.append(f"CREATE schema IF NOT EXISTS sample_shop;")
parts.append(f"USE sample_shop;")

parts.append("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
""")

parts.append("""
CREATE TABLE IF NOT EXISTS orders (
    order_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'PENDING',
    total_amount DECIMAL(10,2),
    shipping_address VARCHAR(255),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB;
""")

parts.append("""
CREATE TABLE IF NOT EXISTS products (
    product_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(150) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2) NOT NULL,
    stock_quantity INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
""")

parts.append("""
CREATE TABLE IF NOT EXISTS order_products (
    order_id BIGINT NOT NULL,
    product_id BIGINT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price_at_purchase DECIMAL(10,2),
    PRIMARY KEY (order_id, product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB;
""")

# Users insert
parts.append("""
INSERT INTO users (full_name, email, phone)
VALUES
('Amit Sharma', 'amit.sharma@example.com', '+91-9000000001'),
('Priya Mehta', 'priya.mehta@example.com', '+91-9000000002'),
('Rohan Gupta', 'rohan.gupta@example.com', '+91-9000000003'),
('Neha Verma', 'neha.verma@example.com', '+91-9000000004'),
('Karan Singh', 'karan.singh@example.com', '+91-9000000005'),
('Sneha Iyer', 'sneha.iyer@example.com', '+91-9000000006'),
('Arjun Patel', 'arjun.patel@example.com', '+91-9000000007'),
('Divya Reddy', 'divya.reddy@example.com', '+91-9000000008'),
('Vikram Das', 'vikram.das@example.com', '+91-9000000009'),
('Ananya Bose', 'ananya.bose@example.com', '+91-9000000010'),
('Manish Tiwari', 'manish.tiwari@example.com', '+91-9000000011'),
('Isha Nair', 'isha.nair@example.com', '+91-9000000012'),
('Raj Malhotra', 'raj.malhotra@example.com', '+91-9000000013'),
('Simran Gill', 'simran.gill@example.com', '+91-9000000014'),
('Nikhil Joshi', 'nikhil.joshi@example.com', '+91-9000000015'),
('Aarti Dey', 'aarti.dey@example.com', '+91-9000000016'),
('Sameer Khan', 'sameer.khan@example.com', '+91-9000000017'),
('Pooja Sethi', 'pooja.sethi@example.com', '+91-9000000018'),
('Rahul Bhat', 'rahul.bhat@example.com', '+91-9000000019'),
('Tanya Kapoor', 'tanya.kapoor@example.com', '+91-9000000020');
""")

# Products insert
parts.append("""
INSERT INTO products (product_name, category, price, stock_quantity)
VALUES
('Apple iPhone 15', 'Electronics', 79999.00, 25),
('Samsung Galaxy S23', 'Electronics', 74999.00, 30),
('Sony WH-1000XM5 Headphones', 'Electronics', 29999.00, 50),
('MacBook Air M3', 'Computers', 124999.00, 20),
('Dell XPS 13', 'Computers', 119999.00, 15),
('LG 55-inch OLED TV', 'Home Appliances', 109999.00, 10),
('Dyson V12 Vacuum', 'Home Appliances', 49999.00, 25),
('Nike Air Zoom Pegasus', 'Fashion', 8999.00, 100),
('Adidas Ultraboost 23', 'Fashion', 10999.00, 80),
('Puma Running Shorts', 'Fashion', 1999.00, 150),
('Wilson Tennis Racket', 'Sports', 14999.00, 40),
('Yonex Badminton Racquet', 'Sports', 7999.00, 60),
('Nivia Football', 'Sports', 1499.00, 200),
('Protein Powder 1kg', 'Groceries', 2999.00, 100),
('Organic Honey 500g', 'Groceries', 499.00, 300),
('Apple Watch Series 9', 'Electronics', 45999.00, 50),
('Samsung Galaxy Watch 6', 'Electronics', 32999.00, 40),
('Lenovo Legion 5 Pro', 'Computers', 139999.00, 12),
('Mi Smart Speaker', 'Electronics', 4999.00, 90),
('Google Nest Hub', 'Electronics', 8999.00, 40);
""")

# Orders insert
parts.append("""
INSERT INTO orders (user_id, order_date, status, total_amount, shipping_address)
VALUES
(1, NOW(), 'COMPLETED', 85999.00, 'Mumbai, India'),
(2, NOW(), 'PENDING', 124999.00, 'Pune, India'),
(3, NOW(), 'COMPLETED', 29999.00, 'Bangalore, India'),
(4, NOW(), 'COMPLETED', 9999.00, 'Delhi, India'),
(5, NOW(), 'PENDING', 4999.00, 'Hyderabad, India'),
(6, NOW(), 'CANCELLED', 109999.00, 'Kolkata, India'),
(7, NOW(), 'COMPLETED', 45999.00, 'Chennai, India'),
(8, NOW(), 'COMPLETED', 14999.00, 'Noida, India'),
(9, NOW(), 'COMPLETED', 89999.00, 'Gurugram, India'),
(10, NOW(), 'PENDING', 1999.00, 'Ahmedabad, India'),
(11, NOW(), 'COMPLETED', 119999.00, 'Indore, India'),
(12, NOW(), 'PENDING', 999.00, 'Surat, India'),
(13, NOW(), 'COMPLETED', 3999.00, 'Chandigarh, India'),
(14, NOW(), 'COMPLETED', 8999.00, 'Jaipur, India'),
(15, NOW(), 'COMPLETED', 179999.00, 'Nagpur, India'),
(16, NOW(), 'PENDING', 1599.00, 'Bhopal, India'),
(17, NOW(), 'COMPLETED', 29999.00, 'Lucknow, India'),
(18, NOW(), 'PENDING', 3999.00, 'Kanpur, India'),
(19, NOW(), 'COMPLETED', 74999.00, 'Patna, India'),
(20, NOW(), 'COMPLETED', 5999.00, 'Ranchi, India');
""")

# Order products insert
parts.append("""
INSERT INTO order_products (order_id, product_id, quantity, price_at_purchase)
VALUES
(1, 1, 1, 79999.00),
(1, 16, 1, 45999.00),
(2, 4, 1, 124999.00),
(3, 3, 1, 29999.00),
(4, 8, 2, 17998.00),
(5, 15, 3, 1497.00);
""")

SQL_SCRIPT = "\n".join(parts)

def execute_script():
    print(f"Connecting to MySQL at {MYSQL_HOST}:{MYSQL_PORT} as '{MYSQL_USER}'")
    try:
        conn = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        cursor = conn.cursor()
        statements = [stmt.strip() for stmt in SQL_SCRIPT.split(';') if stmt.strip()]
        for statement in statements:
            cursor.execute(statement)
        conn.commit()
        print("SQL script executed successfully.")
        cursor.close()
        conn.close()
    except Exception as e:
        print("Failed to create sample_shop schema and populate data. See errors above.", e)
        sys.exit(1)


if __name__ == "__main__":
    try:
        execute_script()
    except Exception as e:
        print("Failed to create sample_shop schema and populate data. See errors above.", e)
        sys.exit(1)

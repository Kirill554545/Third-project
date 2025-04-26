import psycopg2
conn = psycopg2.connect(
    dbname='projectdb',
    user='postgres',
    password='1234',
    host='localhost',
    port='5432'
)

cursor = conn.cursor()

# cursor.execute("""SELECT username FROM users WHERE user_id = %s;""", (1078189371, ))
# n = cursor.fetchall()
# print(n)
# SQL-команда для создания таблицы
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id BIGINT UNIQUE,
    username TEXT DEFAULT 'Не указано',
    user_phone_number TEXT DEFAULT 'Не указан',
    email TEXT DEFAULT 'Не указана',
    delivery_address TEXT DEFAULT 'Не указан',
    role INTEGER DEFAULT 1
);""")

cursor.execute("""CREATE TABLE IF NOT EXISTS roles (
    id SERIAL PRIMARY KEY,
    role VARCHAR(20));""")

cursor.execute("""CREATE TABLE IF NOT EXISTS bouqets (
    id SERIAL PRIMARY KEY,
    bouqet_name TEXT DEFAULT 'Не указано',
    bouqet_photo TEXT DEFAULT 'Не добавлено',
    bouqet_description TEXT DEFAULT 'Не указано',
    bouqet_price TEXT DEFAULT 'Не указана')""")

cursor.execute("""CREATE TABLE IF NOT EXISTS basket (
    id SERIAL PRIMARY KEY,
    bouqet_id INTEGER, 
    user_id TEXT)""")

# cursor.execute("""INSERT INTO roles (role) VALUES ('Пользователь'), ('Флорист'), ('Администратор')""")
conn.commit()
cursor.close()
conn.close()

print("Таблица 'users' успешно создана.")

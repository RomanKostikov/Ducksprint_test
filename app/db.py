import sqlite3
from cryptography.fernet import Fernet
from config import FERNET_KEY

# Инициализация шифратора
cipher_suite = Fernet(FERNET_KEY)

# Подключение к базе данных
conn = sqlite3.connect('tokens.db')
c = conn.cursor()

# Создаем таблицу для хранения токенов
c.execute('''CREATE TABLE IF NOT EXISTS tokens
             (user_id INTEGER PRIMARY KEY, access_token TEXT)''')
conn.commit()


def save_token(user_id, token):
    encrypted_token = cipher_suite.encrypt(token.encode())
    c.execute('INSERT OR REPLACE INTO tokens (user_id, access_token) VALUES (?, ?)',
              (user_id, encrypted_token))
    conn.commit()


def get_token(user_id):
    c.execute('SELECT access_token FROM tokens WHERE user_id = ?', (user_id,))
    result = c.fetchone()
    if result:
        return cipher_suite.decrypt(result[0]).decode()
    return None


def close_connection():
    conn.close()

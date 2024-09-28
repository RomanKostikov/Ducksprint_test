from dotenv import load_dotenv
import os

# Загрузка переменных окружения
load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_API_TOKEN')

# Генерация или загрузка ключа для шифрования токенов
FERNET_KEY = os.getenv('FERNET_KEY')

if FERNET_KEY is None:
    from cryptography.fernet import Fernet
    FERNET_KEY = Fernet.generate_key()

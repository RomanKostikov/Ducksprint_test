from flask import Flask, request, redirect
import requests
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

app = Flask(__name__)

# Получаем данные из .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')


@app.route('/')
def home():
    return 'Приложение работает. Перейдите по /auth для начала авторизации.'


@app.route('/auth')
def auth():
    # Формируем URL для авторизации
    auth_url = f'https://www.avito.ru/oauth/authorize?' \
               f'client_id={CLIENT_ID}&' \
               f'response_type=code&' \
               f'redirect_uri={REDIRECT_URI}'
    return redirect(auth_url)


@app.route('/callback')
def callback():
    # Получаем код авторизации
    code = request.args.get('code')

    if not code:
        return "Ошибка: код авторизации не передан", 400

    # Отправляем запрос для обмена кода на токен
    token_url = 'https://api.avito.ru/token'
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    # Делаем запрос на получение токена
    token_response = requests.post(token_url, data=token_data)

    # Проверяем статус запроса
    if token_response.status_code != 200:
        return f"Ошибка при обмене кода на токен: {token_response.status_code} {token_response.text}", 400

    # Получаем JSON ответ
    token_json = token_response.json()

    # Проверяем наличие токена в ответе
    if 'access_token' not in token_json:
        return f"Ошибка при получении токена: {token_json}", 400

    # Получаем токен доступа и токен для обновления
    access_token = token_json.get('access_token')
    refresh_token = token_json.get('refresh_token')
    return f'Access Token: {access_token}<br>Refresh Token: {refresh_token}'


if __name__ == '__main__':
    app.run(port=8000)

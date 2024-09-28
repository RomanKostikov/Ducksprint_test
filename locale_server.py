from flask import Flask, request
import requests

app = Flask(__name__)

CLIENT_ID = 'your_client_id' # выдают при подписке
CLIENT_SECRET = 'your_client_secret' # выдают при подписке
REDIRECT_URI = 'https://example.com/callback'


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

    # Получаем токен доступа
    access_token = token_json.get('access_token')
    return f'Access Token: {access_token}'


if __name__ == '__main__':
    app.run(port=8000)

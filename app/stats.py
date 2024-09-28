import aiohttp
from openpyxl import Workbook
from fake_data import get_fake_stats

test_mode = False


# Установка режима тестирования
def set_test_mode(value):
    global test_mode
    test_mode = value


# Проверка активен ли тестовый режим
def is_test_mode_active():
    return test_mode


# Получение списка аккаунтов
async def get_user_accounts(token):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.avito.ru/core/v1/accounts',
                               headers=headers) as response:
            data = await response.json()
            accounts = data.get('result', {}).get('accounts', [])
            account_ids = [account['id'] for account in accounts]
            return account_ids


# Получение данных из Avito API или фиктивных данных
async def get_avito_stats(token, account_ids):
    headers = {
        'Authorization': f'Bearer {token}',
    }
    stats_per_account = {}
    async with aiohttp.ClientSession() as session:
        for account_id in account_ids:
            # Получаем список объявлений для аккаунта
            async with session.get(f'https://api.avito.ru/core/v1/accounts/{account_id}/items',
                                   headers=headers) as response:
                data = await response.json()
                items = data.get('result', {}).get('items', [])
                stats = []
                for item in items:
                    item_id = item['id']
                    title = item['title']
                    # Получаем статистику звонков для объявления
                    async with session.get(
                            f'https://api.avito.ru/core/v1/accounts/{account_id}/items/{item_id}/calls/stats/',
                            headers=headers) as stats_response:
                        stats_data = await stats_response.json()
                        stat = {
                            'title': title,
                            'answered': stats_data.get('answered', 0),
                            'calls': stats_data.get('calls', 0),
                            'new': stats_data.get('new', 0),
                            'newAnswered': stats_data.get('newAnswered', 0),
                        }
                        stats.append(stat)
                stats_per_account[account_id] = stats
    return stats_per_account


# Создание отчета в формате XLSX


def create_xlsx_report(stats_per_account, user_id):
    wb = Workbook()
    # Удаляем стандартный лист, созданный по умолчанию
    wb.remove(wb.active)

    for account_id, stats in stats_per_account.items():
        ws = wb.create_sheet(title=f"Аккаунт {account_id}")

        # Заголовки
        ws.append(['Название объявления', 'Отвеченные звонки', 'Звонки всего', 'Новые звонки',
                   'Новые и отвеченные звонки'])

        # Добавление данных
        for stat in stats:
            ws.append(
                [stat['title'], stat['answered'], stat['calls'], stat['new'], stat['newAnswered']])

    # Сохранение файла
    file_path = f'stats_{user_id}.xlsx'
    wb.save(file_path)
    return file_path

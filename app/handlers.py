import os
import logging
from aiogram import types
from aiogram.filters import Command
from aiogram import Dispatcher
from db import save_token, get_token
from stats import get_avito_stats, create_xlsx_report, set_test_mode, is_test_mode_active, \
    get_user_accounts
from aiogram.types import FSInputFile
from fake_data import get_fake_stats


keyboard_markup = types.ReplyKeyboardMarkup(
    keyboard=[
        [types.KeyboardButton(text='Показать статистику')],
        [types.KeyboardButton(text='Включить тестовый режим'),
         types.KeyboardButton(text='Выключить тестовый режим')]
    ],
    resize_keyboard=True
)


# Команда старт
async def start_command(message: types.Message):
    await message.answer("Привет! Отправь мне свой токен авторизации для работы с Avito API.",
                         reply_markup=keyboard_markup)


# Обработка токена от пользователя
async def receive_token(message: types.Message):
    user_id = message.from_user.id
    token = message.text
    save_token(user_id, token)
    await message.answer("Токен сохранен. Теперь ты можешь запросить статистику.",
                         reply_markup=keyboard_markup)


# Включение/выключение тестового режима
async def toggle_test_mode(message: types.Message):
    if message.text == 'Включить тестовый режим':
        set_test_mode(True)
        await message.answer("Тестовый режим включен. Все данные будут фиктивными.")
    else:
        set_test_mode(False)
        await message.answer("Тестовый режим выключен. Все данные будут реальными.")


# Обработка кнопки парсинга
async def show_stats(message: types.Message):
    user_id = message.from_user.id

    # Проверяем, включен ли тестовый режим
    if not is_test_mode_active():
        token = get_token(user_id)
        if not token:
            await message.answer("Ты не отправил токен. Пожалуйста, отправь токен авторизации.")
            return

    await message.answer("Начинаю парсинг данных... Это может занять некоторое время.")

    try:
        if is_test_mode_active():
            stats_per_account = {'Тестовый аккаунт 1': get_fake_stats(),
                                 'Тестовый аккаунт 2': get_fake_stats()}
        else:
            token = get_token(user_id)
            account_ids = await get_user_accounts(token)
            stats_per_account = await get_avito_stats(token, account_ids)
        file_path = create_xlsx_report(stats_per_account, user_id)
        await message.answer_document(FSInputFile(file_path))
        os.remove(file_path)
    except Exception as e:
        logging.exception("Ошибка при парсинге или создании отчета:")
        await message.answer(
            "Произошла ошибка при парсинге данных. Проверь токен и попробуй снова.")


# Регистрация всех обработчиков
def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command(commands=['start']))
    dp.message.register(receive_token, lambda message: len(message.text) > 30)
    dp.message.register(toggle_test_mode,
                        lambda message: message.text in ['Включить тестовый режим',
                                                         'Выключить тестовый режим'])
    dp.message.register(show_stats, lambda message: message.text == 'Показать статистику')

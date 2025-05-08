import os
import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Токен вашего бота (замените на свой)
API_TOKEN = 5000594913:AAGJbliI31vdL0AkUhCsk9grA2fipApF3vo

# Инициализация бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Файл для хранения данных
DATA_FILE = "user_data.json"

# Настройки казино
DAILY_BONUS = 100  # Ежедневный бонус
SLOT_COST = 500    # Стоимость игры на слотах
DICE_COST = 500    # Стоимость игры на кубиках

# Клавиатура
menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_kb.add(KeyboardButton('/balance'), KeyboardButton('/slots'))
menu_kb.add(KeyboardButton('/dice'), KeyboardButton('/daily'))


# === Утилиты для работы с данными === #
def load_data():
    """Загрузка данных из JSON-файла"""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_data(data):
    """Сохранение данных в JSON-файл"""
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_user_balance(user_id):
    """Получить баланс пользователя"""
    data = load_data()
    return data.get(str(user_id), {}).get("balance", 500)  # Начальный баланс


def update_user_balance(user_id, new_balance):
    """Обновить баланс пользователя"""
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["balance"] = new_balance
    save_data(data)


def set_daily_claimed(user_id, claimed=True):
    """Установить статус получения ежедневного бонуса"""
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["daily_claimed"] = claimed
    save_data(data)


def get_daily_claimed(user_id):
    """Проверить, получал ли пользователь ежедневный бонус"""
    data = load_data()
    return data.get(str(user_id), {}).get("daily_claimed", False)


# === Команды бота === #
@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    """Команда /start"""
    user_id = message.from_user.id

    # Инициализируем пользователя, если он новый
    if get_user_balance(user_id) == 500:
        update_user_balance(user_id, 500)

    await message.answer(
        "🎰 Добро пожаловать в StarSpin Casino!\n"
        "Используйте меню для игры и проверки своего баланса.",
        reply_markup=menu_kb
    )


@dp.message_handler(commands=['balance'])
async def balance_cmd(message: types.Message):
    """Команда /balance"""
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    await message.answer(f"💰 Ваш баланс: {balance} StarCoins")


@dp.message_handler(commands=['slots'])
async def slots_cmd(message: types.Message):
    """Команда /slots"""
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    if balance < SLOT_COST:
        return await message.answer("❌ У вас недостаточно средств для игры на слотах (нужно 500 StarCoins).")

    # Списываем стоимость игры
    update_user_balance(user_id, balance - SLOT_COST)

    # Генерация символов
    symbols = ['⭐', '7️⃣', '🔥', '💎']
    result = [random.choice(symbols) for _ in range(3)]
    text = ' | '.join(result)

    # Проверка выигрыша
    if len(set(result)) == 1:  # Джекпот
        winnings = 1500
        update_user_balance(user_id, get_user_balance(user_id) + winnings)
        await message.answer(f"{text}\n🎉 Джекпот! Вы выиграли {winnings} StarCoins!")
    elif len(set(result)) == 2:  # Частичный выигрыш
        winnings = 700
        update_user_balance(user_id, get_user_balance(user_id) + winnings)
        await message.answer(f"{text}\n👍 Вы выиграли {winnings} StarCoins!")
    else:  # Проигрыш
        await message.answer(f"{text}\n😢 Увы, вы ничего не выиграли.")


@dp.message_handler(commands=['dice'])
async def dice_cmd(message: types.Message):
    """Команда /dice"""
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    if balance < DICE_COST:
        return await message.answer("❌ У вас недостаточно средств для броска кубиков (нужно 500 StarCoins).")

    # Списываем стоимость игры
    update_user_balance(user_id, balance - DICE_COST)

    # Броски
    user_throw = random.randint(1, 6)
    bot_throw = random.randint(1, 6)

    await message.answer(f"🎲 Вы выбросили: {user_throw}\n🤖 Казино выбросило: {bot_throw}")

    # Определение результата
    if user_throw > bot_throw:
        winnings = 1000
        update_user_balance(user_id, get_user_balance(user_id) + winnings)
        await message.answer(f"🎉 Вы победили и выиграли {winnings} StarCoins!")
    elif user_throw == bot_throw:
        update_user_balance(user_id, get_user_balance(user_id) + DICE_COST)
        await message.answer("🤝 Ничья! Ваша ставка возвращена.")
    else:
        await message.answer("😢 Увы, вы проиграли.")


@dp.message_handler(commands=['daily'])
async def daily_cmd(message: types.Message):
    """Команда /daily"""
    user_id = message.from_user.id

    if get_daily_claimed(user_id):
        return await message.answer("❌ Вы уже получили ежедневный бонус. Приходите завтра!")

    # Добавляем бонус
    update_user_balance(user_id, get_user_balance(user_id) + DAILY_BONUS)
    set_daily_claimed(user_id, True)

    await message.answer(f"🎁 Вы получили ежедневный бонус: {DAILY_BONUS} StarCoins!")

    # Сбрасываем ежедневный бонус через 24 часа
    await asyncio.sleep(86400)
    set_daily_claimed(user_id, False)


# === Запуск бота === #
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
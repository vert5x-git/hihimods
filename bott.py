import os
import json
import random
import asyncio
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

API_TOKEN = "5000594913:AAGJbliI31vdL0AkUhCsk9grA2fipApF3vo"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

DATA_FILE = "user_data.json"

DAILY_BONUS = 100
SLOT_COST = 500
DICE_COST = 500

menu_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
menu_kb.add(KeyboardButton('/balance'), KeyboardButton('/slots'))
menu_kb.add(KeyboardButton('/dice'), KeyboardButton('/daily'))


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)


def get_user_balance(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("balance", 500)


def update_user_balance(user_id, new_balance):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["balance"] = new_balance
    save_data(data)


def set_daily_claimed(user_id, claimed=True):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {}
    data[str(user_id)]["daily_claimed"] = claimed
    save_data(data)


def get_daily_claimed(user_id):
    data = load_data()
    return data.get(str(user_id), {}).get("daily_claimed", False)


@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id

    if get_user_balance(user_id) == 500:
        update_user_balance(user_id, 500)

    await message.answer(
        "🎰 Добро пожаловать в StarSpin Casino!\n"
        "Используйте меню для игры и проверки своего баланса.",
        reply_markup=menu_kb
    )


@dp.message_handler(commands=['balance'])
async def balance_cmd(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)
    await message.answer(f"💰 Ваш баланс: {balance} StarCoins")


@dp.message_handler(commands=['slots'])
async def slots_cmd(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    if balance < SLOT_COST:
        return await message.answer("❌ У вас недостаточно средств для игры на слотах (нужно 500 StarCoins).")

    update_user_balance(user_id, balance - SLOT_COST)

    symbols = ['⭐', '7️⃣', '🔥', '💎']
    result = [random.choice(symbols) for _ in range(3)]
    text = ' | '.join(result)

    if len(set(result)) == 1:
        winnings = 1500
        update_user_balance(user_id, get_user_balance(user_id) + winnings)
        await message.answer(f"{text}\n🎉 Джекпот! Вы выиграли {winnings} StarCoins!")
    elif len(set(result)) == 2:
        winnings = 700
        update_user_balance(user_id, get_user_balance(user_id) + winnings)
        await message.answer(f"{text}\n👍 Вы выиграли {winnings} StarCoins!")
    else:
        await message.answer(f"{text}\n😢 Увы, вы ничего не выиграли.")


@dp.message_handler(commands=['dice'])
async def dice_cmd(message: types.Message):
    user_id = message.from_user.id
    balance = get_user_balance(user_id)

    if balance < DICE_COST:
        return await message.answer("❌ У вас недостаточно средств для броска кубиков (нужно 500 StarCoins).")

    update_user_balance(user_id, balance - DICE_COST)

    user_throw = random.randint(1, 6)
    bot_throw = random.randint(1, 6)

    await message.answer(f"🎲 Вы выбросили: {user_throw}\n🤖 Казино выбросило: {bot_throw}")

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
    user_id = message.from_user.id

    if get_daily_claimed(user_id):
        return await message.answer("❌ Вы уже получили ежедневный бонус. Приходите завтра!")

    update_user_balance(user_id, get_user_balance(user_id) + DAILY_BONUS)
    set_daily_claimed(user_id, True)

    await message.answer(f"🎁 Вы получили ежедневный бонус: {DAILY_BONUS} StarCoins!")

    await asyncio.sleep(86400)
    set_daily_claimed(user_id, False)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
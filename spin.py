from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import random
import asyncio

API_TOKEN = '5000594913:AAGJbliI31vdL0AkUhCsk9grA2fipApF3vo'
ADMIN_ID = ADMIN_ID = 5000594913

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Баланс пользователей
user_balances = {}

# Клавиатура
menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
menu_kb.add(KeyboardButton('/balance'), KeyboardButton('/slots'))
menu_kb.add(KeyboardButton('/dice'), KeyboardButton('/daily'))

# DAILY бонусы
daily_bonus = 100
user_daily = {}

@dp.message_handler(commands=['start'])
async def start_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_balances:
        user_balances[user_id] = 500  # начальный баланс
    await message.answer("Добро пожаловать в StarSpin Casino!", reply_markup=menu_kb)

@dp.message_handler(commands=['balance'])
async def balance_cmd(message: types.Message):
    user_id = message.from_user.id
    balance = user_balances.get(user_id, 0)
    await message.answer(f"Ваш баланс: {balance} StarCoins")

@dp.message_handler(commands=['slots'])
async def slots_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_balances.get(user_id, 0) < 500:
        return await message.answer("Недостаточно средств для игры. Нужно 500 StarCoins.")

    user_balances[user_id] -= 500
    symbols = ['⭐', '7️⃣', '🔥', '💎']
    result = [random.choice(symbols) for _ in range(3)]
    text = ' | '.join(result)

    if len(set(result)) == 1:
        winnings = 1500
        user_balances[user_id] += winnings
        await message.answer(f"{text}\nДжекпот! Вы выиграли {winnings} StarCoins!")
    elif len(set(result)) == 2:
        winnings = 700
        user_balances[user_id] += winnings
        await message.answer(f"{text}\nНеплохо! Вы выиграли {winnings} StarCoins!")
    else:
        await message.answer(f"{text}\nУвы, вы ничего не выиграли.")

@dp.message_handler(commands=['dice'])
async def dice_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_balances.get(user_id, 0) < 500:
        return await message.answer("Недостаточно средств для броска. Нужно 500 StarCoins.")

    user_balances[user_id] -= 500
    user_throw = random.randint(1, 6)
    bot_throw = random.randint(1, 6)
    await message.answer(f"Вы выбросили: {user_throw}\nКазино выбросило: {bot_throw}")

    if user_throw > bot_throw:
        win = 1000
        user_balances[user_id] += win
        await message.answer(f"Вы выиграли {win} StarCoins!")
    elif user_throw == bot_throw:
        user_balances[user_id] += 500
        await message.answer("Ничья! Ваша ставка возвращена.")
    else:
        await message.answer("Увы, вы проиграли.")

@dp.message_handler(commands=['daily'])
async def daily_cmd(message: types.Message):
    user_id = message.from_user.id
    if user_daily.get(user_id):
        return await message.answer("Вы уже получили ежедневный бонус. Приходите завтра!")

    user_balances[user_id] = user_balances.get(user_id, 0) + daily_bonus
    user_daily[user_id] = True
    await message.answer(f"Вы получили {daily_bonus} StarCoins как ежедневный бонус!")

    await asyncio.sleep(86400)  # ждем 24 часа
    user_daily[user_id] = False

# Админ-команды (только для ADMIN_ID)
@dp.message_handler(commands=['admin'])
async def admin_menu(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = (
        "Админ-панель:\n"
        "/give [user_id] [amount] — выдать монеты\n"
        "/take [user_id] [amount] — забрать монеты\n"
        "/users — список пользователей"
    )
    await message.answer(text)

@dp.message_handler(lambda message: message.text.startswith('/give'))
async def admin_give(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = message.text.split()
        uid = int(uid)
        amount = int(amount)
        user_balances[uid] = user_balances.get(uid, 0) + amount
        await message.answer(f"Выдано {amount} StarCoins пользователю {uid}.")
    except:
        await message.answer("Неверный формат команды. Пример: /give 123456789 1000")

@dp.message_handler(lambda message: message.text.startswith('/take'))
async def admin_take(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    try:
        _, uid, amount = message.text.split()
        uid = int(uid)
        amount = int(amount)
        user_balances[uid] = max(0, user_balances.get(uid, 0) - amount)
        await message.answer(f"Забрано {amount} StarCoins у пользователя {uid}.")
    except:
        await message.answer("Неверный формат команды. Пример: /take 123456789 500")

@dp.message_handler(commands=['users'])
async def admin_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    text = "Список пользователей и их балансы:\n"
    for uid, bal in user_balances.items():
        text += f"{uid}: {bal} StarCoins\n"
    await message.answer(text)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
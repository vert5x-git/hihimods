import random
import asyncio
from telethon import TelegramClient, events, Button

# Замените на ваши значения
api_id = 26694251
api_hash = '5b041e7b70b74c095435be2b74c02abf'
bot_token = '5000594913:AAGJbliI31vdL0AkUhCsk9grA2fipApF3vo'
ADMIN_ID = 5000047781  # Замените на ваш Telegram ID

client = TelegramClient('casino_bot', api_id, api_hash).start(bot_token=bot_token)

# Словари для хранения данных пользователей
user_balances = {}
user_daily = {}

# Команда /start
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    user_id = event.sender_id
    user_balances.setdefault(user_id, 500)  # Начальный баланс
    user_daily.setdefault(user_id, False)
    await event.respond(
        "🎰 Добро пожаловать в казино-бот!\nВыберите действие:",
        buttons=[
            [Button.inline('💰 Баланс', b'balance'), Button.inline('🎰 Слоты', b'slots')],
            [Button.inline('🎲 Кубик', b'dice'), Button.inline('🃏 Блэкджек', b'blackjack')],
            [Button.inline('🎡 Колесо фортуны', b'wheel'), Button.inline('🎁 Бонус', b'daily')],
            [Button.inline('👤 Профиль', b'profile'), Button.inline('🏆 Топ игроков', b'top')]
        ]
    )

# Обработка нажатий на кнопки
@client.on(events.CallbackQuery)
async def callback(event):
    user_id = event.sender_id
    data = event.data.decode()

    if data == 'balance':
        balance = user_balances.get(user_id, 0)
        await event.respond(f"💰 Ваш баланс: {balance} StarCoins")
    elif data == 'slots':
        await play_slots(event, user_id)
    elif data == 'dice':
        await play_dice(event, user_id)
    elif data == 'blackjack':
        await play_blackjack(event, user_id)
    elif data == 'wheel':
        await play_wheel(event, user_id)
    elif data == 'daily':
        await daily_bonus(event, user_id)
    elif data == 'profile':
        await show_profile(event, user_id)
    elif data == 'top':
        await show_top(event)
    else:
        await event.respond("❌ Неизвестная команда.")

# Игра: Слоты
async def play_slots(event, user_id):
    if user_balances.get(user_id, 0) < 100:
        await event.respond("❌ Недостаточно средств для игры. Нужно 100 StarCoins.")
        return
    user_balances[user_id] -= 100
    emojis = ['🍒', '🍋', '🔔', '⭐', '💎']
    result = [random.choice(emojis) for _ in range(3)]
    await event.respond(f"🎰 {' | '.join(result)}")
    if len(set(result)) == 1:
        winnings = 500
        user_balances[user_id] += winnings
        await event.respond(f"🎉 Поздравляем! Вы выиграли {winnings} StarCoins!")
    else:
        await event.respond("😢 Увы, вы проиграли.")

# Игра: Кубик
async def play_dice(event, user_id):
    if user_balances.get(user_id, 0) < 50:
        await event.respond("❌ Недостаточно средств для игры. Нужно 50 StarCoins.")
        return
    user_balances[user_id] -= 50
    user_roll = random.randint(1, 6)
    bot_roll = random.randint(1, 6)
    await event.respond(f"🎲 Вы бросили: {user_roll}\n🤖 Бот бросил: {bot_roll}")
    if user_roll > bot_roll:
        winnings = 100
        user_balances[user_id] += winnings
        await event.respond(f"🎉 Вы выиграли {winnings} StarCoins!")
    elif user_roll == bot_roll:
        user_balances[user_id] += 50
        await event.respond("🤝 Ничья! Ваша ставка возвращена.")
    else:
        await event.respond("😢 Увы, вы проиграли.")

# Игра: Блэкджек
async def play_blackjack(event, user_id):
    if user_balances.get(user_id, 0) < 100:
        await event.respond("❌ Недостаточно средств для игры. Нужно 100 StarCoins.")
        return
    user_balances[user_id] -= 100
    user_score = random.randint(15, 21)
    dealer_score = random.randint(17, 21)
    result = f"🃏 Ваш счёт: {user_score}\n🏢 Счёт дилера: {dealer_score}\n"
    if user_score > dealer_score:
        winnings = 200
        user_balances[user_id] += winnings
        result += f"🎉 Вы выиграли {winnings} StarCoins!"
    elif user_score == dealer_score:
        user_balances[user_id] += 100
        result += "🤝 Ничья! Ваша ставка возвращена."
    else:
        result += "😢 Увы, вы проиграли."
    await event.respond(result)

# Игра: Колесо фортуны
async def play_wheel(event, user_id):
    if user_balances.get(user_id, 0) < 50:
        await event.respond("❌ Недостаточно средств для вращения. Нужно 50 StarCoins.")
        return
    user_balances[user_id] -= 50
    prizes = [0, 100, 200, 300, 500, 1000]
    prize = random.choice(prizes)
    user_balances[user_id] += prize
    if prize == 0:
        message = "😢 Увы, вы ничего не выиграли."
    else:
        message = f"🎉 Поздравляем! Вы выиграли {prize} StarCoins!"
    await event.respond(message)

# Ежедневный бонус
async def daily_bonus(event, user_id):
    if user_daily.get(user_id):
        await event.respond("🎁 Вы уже получили ежедневный бонус. Приходите завтра!")
    else:
        bonus = 200
        user_balances[user_id] += bonus
        user_daily[user_id] = True
        await event.respond(f"🎁 Вы получили ежедневный бонус: {bonus} StarCoins!")

# Профиль пользователя
async def show_profile(event, user_id):
    balance = user_balances.get(user_id, 0)
    daily_status = "Получен" if user_daily.get(user_id) else "Доступен"
    profile_info = (
        f"👤 Профиль пользователя:\n"
        f"🆔 ID: {user_id}\n"
        f"💰 Баланс: {balance} StarCoins\n"
        f"🎁 Ежедневный бонус: {daily_status}"
    )
    await event.respond(profile_info)

# Топ игроков
async def show_top(event):
    top_users = sorted(user_balances.items(), key=lambda x: x[1], reverse=True)[:5]
    leaderboard = "🏆 Топ 5 игроков:\n"
    for idx, (uid, bal) in enumerate(top_users, start=1):
        leaderboard += f"{idx}. ID {uid}: {bal} StarCoins\n"
    await event.respond(leaderboard)

# Административные команды
@client.on(events.NewMessage(pattern='/reset_daily'))
async def reset_daily(event):
    if event.sender_id != ADMIN_ID:
        return
    for uid in user_daily:
        user_daily[uid] = False
    await event.respond("✅ Статусы ежедневных бонусов сброшены для всех пользователей.")

@client.on(events.NewMessage(pattern='/remove_user'))
async def remove_user(event):
    if event.sender_id != ADMIN_ID:
        return
    try:
        _, uid = event.message.text.split()
        uid = int(uid)
        user_balances.pop(uid, None)
        user_daily.pop(uid, None)
        await event.respond(f"✅ Пользователь {uid} удалён из базы данных.")
    except:
        await event.respond("❌ Неверный формат команды. Пример: /remove_user 123456789")

# Запуск бота
client.run_until_disconnected()
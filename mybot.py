import telebot
from telebot import types
import time
import sqlite3

TOKEN = '7718204976:AAGhQNlS9ulnqj_SatBQucQTsABVnOE9Co0'
ADMIN_IDS = [6450469685]
SUPPORT_CHAT_ID = -4805465459

bot = telebot.TeleBot(TOKEN)

def init_db():
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        last_name TEXT,
        registration_date TEXT
    )
    ''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tickets (
        ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        question TEXT,
        status TEXT DEFAULT 'open',
        created_at TEXT,
        admin_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users (user_id)
    ''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, registration_date) VALUES (?, ?, ?, ?, ?)',
                   (user_id, username, first_name, last_name, time.strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("📨 Задать вопрос")
    btn2 = types.KeyboardButton("ℹ️ Помощь")
    markup.add(btn1, btn2)
    
    bot.send_message(message.chat.id, f"👋 Привет, {first_name}!\n\nЯ бот поддержки. Ты можешь задать вопрос, нажав кнопку ниже.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "📨 Задать вопрос")
def ask_question(message):
    msg = bot.send_message(message.chat.id, "Напишите ваш вопрос:")
    bot.register_next_step_handler(msg, process_question)

def process_question(message):
    user_id = message.from_user.id
    question = message.text
    
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tickets (user_id, question, created_at) VALUES (?, ?, ?)',
                   (user_id, question, time.strftime('%Y-%m-%d %H:%M:%S')))
    ticket_id = cursor.lastrowid
    conn.commit()
    
    cursor.execute('SELECT username, first_name, last_name FROM users WHERE user_id = ?', (user_id,))
    user_info = cursor.fetchone()
    conn.close()
    
    username, first_name, last_name = user_info if user_info else (None, None, None)
    user_name = f"@{username}" if username else f"{first_name} {last_name}" if first_name or last_name else f"ID: {user_id}"
    
    for admin_id in ADMIN_IDS:
        try:
            bot.send_message(admin_id, f"📨 Новый вопрос (#{ticket_id}) от {user_name}:\n\n{question}\n\nОтветьте на это сообщение, чтобы отправить ответ пользователю.")
        except Exception as e:
            print(f"Ошибка отправки админу {admin_id}: {e}")
    
    if SUPPORT_CHAT_ID:
        try:
            bot.send_message(SUPPORT_CHAT_ID, f"📨 Новый вопрос (#{ticket_id}) от {user_name}:\n\n{question}")
        except Exception as e:
            print(f"Ошибка отправки в чат поддержки: {e}")
    
    bot.send_message(message.chat.id, "✅ Ваш вопрос отправлен. Ожидайте ответа.")

@bot.message_handler(func=lambda message: message.reply_to_message and message.from_user.id in ADMIN_IDS)
def handle_admin_reply(message):
    try:
        original_text = message.reply_to_message.text
        if "Новый вопрос (#" in original_text:
            ticket_id = int(original_text.split('(#')[1].split(')')[0])
            original_question = original_text.split(':\n\n')[1].split('\n\nОтветьте')[0]
            
            conn = sqlite3.connect('support_bot.db')
            cursor = conn.cursor()
            cursor.execute('UPDATE tickets SET status = ?, admin_id = ? WHERE ticket_id = ?',
                         ('closed', message.from_user.id, ticket_id))
            
            cursor.execute('SELECT user_id FROM tickets WHERE ticket_id = ?', (ticket_id,))
            user_id = cursor.fetchone()[0]
            conn.commit()
            conn.close()
            
            try:
                bot.send_message(user_id, f"📩 Ответ от поддержки:\n\n❓ Ваш вопрос: {original_question}\n\n💬 Ответ: {message.text}")
                bot.send_message(message.chat.id, "✅ Ответ отправлен.")
            except Exception as e:
                bot.send_message(message.chat.id, "❌ Не удалось отправить ответ. Пользователь заблокировал бота.")
        else:
            bot.send_message(message.chat.id, "Это не вопрос поддержки.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка: {e}")

@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def send_help(message):
    bot.send_message(message.chat.id, "ℹ️ Справка:\n\n• Нажмите '📨 Задать вопрос' для обращения в поддержку\n• Администраторы ответят в порядке очереди")

@bot.message_handler(commands=['stats'])
def send_stats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.send_message(message.chat.id, "⛔ Нет прав.")
        return
    
    conn = sqlite3.connect('support_bot.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM users')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tickets')
    total_tickets = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM tickets WHERE status = "open"')
    open_tickets = cursor.fetchone()[0]
    
    stats_text = f"📊 Статистика:\n\n• Пользователей: {total_users}\n• Обращений: {total_tickets}\n• Открыто: {open_tickets}\n\n"
    
    if open_tickets > 0:
        cursor.execute('SELECT t.ticket_id, t.question, u.user_id, u.username FROM tickets t JOIN users u ON t.user_id = u.user_id WHERE t.status = "open" ORDER BY t.created_at DESC LIMIT 5')
        open_tickets_list = cursor.fetchall()
        
        stats_text += "📨 Последние открытые:\n"
        for ticket in open_tickets_list:
            ticket_id, question, user_id, username = ticket
            username = f"@{username}" if username else f"ID: {user_id}"
            stats_text += f"#{ticket_id} от {username}: {question[:50]}...\n"
    
    conn.close()
    bot.send_message(message.chat.id, stats_text)

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()
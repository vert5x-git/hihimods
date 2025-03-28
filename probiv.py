from .. import loader
import logging
import datetime
import re

# meta developer: @hihimods

logger = logging.getLogger(__name__)

class AutoProbe(loader.Module):
    """🔍 Авто-пробив пользователей, пишущих в ЛС + фан-статистика"""

    strings = {"name": "AutoProbe"}

    def __init__(self):
        self.db = {}  # Храним фан-статистику

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message):
        if not message.is_private:  # Только ЛС
            return

        user = await self.client.get_entity(message.sender_id)
        user_id = str(user.id)

        # Обновляем фан-статистику
        if user_id not in self.db:
            self.db[user_id] = {
                "messages": 0,
                "total_length": 0,
                "longest": "",
                "shortest": "",
                "words": {}
            }

        user_data = self.db[user_id]
        user_data["messages"] += 1
        user_data["total_length"] += len(message.text)
        words = re.findall(r"\b\w+\b", message.text.lower())

        for word in words:
            user_data["words"][word] = user_data["words"].get(word, 0) + 1

        if not user_data["longest"] or len(message.text) > len(user_data["longest"]):
            user_data["longest"] = message.text

        if not user_data["shortest"] or (0 < len(message.text) < len(user_data["shortest"])):
            user_data["shortest"] = message.text

        # Получаем топ-3 любимых слова
        top_words = sorted(user_data["words"].items(), key=lambda x: x[1], reverse=True)[:3]
        top_words_text = ", ".join(f"{w[0]} ({w[1]})" for w in top_words) if top_words else "Нет данных"

        # Формируем ответ
        user_info = f"🔎 **Пробив пользователя:**\n\n"
        user_info += f"🆔 **ID:** `{user.id}`\n"
        user_info += f"👤 **Username:** @{user.username if user.username else 'Нет'}\n"
        user_info += f"📅 **Дата регистрации:** {user.date.strftime('%Y-%m-%d') if user.date else 'Неизвестно'}\n"
        user_info += f"💎 **Premium:** {'✅ Да' if getattr(user, 'premium', False) else '❌ Нет'}\n"
        user_info += f"📞 **Номер:** `{user.phone if user.phone else 'Скрыт'}`\n"
        user_info += f"🟢 **Статус:** {str(user.status).replace('UserStatus', '')}\n\n"

        # Добавляем фан-статистику
        user_info += "📊 **Фан-статистика:**\n"
        user_info += f"📩 **Сообщений отправлено:** {user_data['messages']}\n"
        user_info += f"📏 **Средняя длина сообщений:** {round(user_data['total_length'] / user_data['messages'], 1)} символов\n"
        user_info += f"🔠 **Самое длинное:** {user_data['longest'][:50]}...\n"
        user_info += f"🔡 **Самое короткое:** {user_data['shortest'][:50]}...\n"
        user_info += f"🔝 **Любимые слова:** {top_words_text}\n"

        await message.client.send_message('me', user_info)
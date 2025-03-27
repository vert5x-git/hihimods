from hikka import loader

# #meta developer = @hihimods

class AutoChat(loader.Module):
    """Модуль для автопоиска собеседников и отправки сообщений"""
    strings = {"name": "AutoChat"}

    async def client_ready(self, client, db):
        self.client = client
        self.target_chat = "@palata_6numberr"
        self.message_text = (
            "🌟 Приглашаем вас на ламповые посиделки в нашем чате! 🌟\n\n"
            "Присоединяйтесь к дружной компании, где вас ждут:\n\n"
            "✨ Добрые администраторы, готовые помочь и поддержать!\n"
            "🎉 Увлекательные розыгрыши на звёзды!\n"
            "💬 Интересные обсуждения и весёлые беседы!\n\n"
            "Не упустите возможность стать частью нашей дружной семьи!\n\n"
            "👨‍👩‍👧 Требования к семье:\n\n"
            "🔞 Возраст: от 13\n"
            "👤 Пол: не важен!!!\n\n"
            "👉 Ссылка на чат: @palata_6numberr\n\n"
            "Ждем вас с нетерпением! 💖"
        )

    @loader.command()
    async def start(self, message):
        """Запуск бота"""
        await self.client.send_message(message.chat_id, "Бот успешно запущен!")

    @loader.command()
    async def set_chat(self, message, chat_name: str):
        """Устанавливает целевой чат для отправки сообщений"""
        self.target_chat = chat_name
        await self.client.send_message(message.chat_id, f"Целевой чат изменён на: {self.target_chat}")

    @loader.command()
    async def set_message(self, message, new_message: str):
        """Устанавливает новый текст сообщения"""
        self.message_text = new_message
        await self.client.send_message(message.chat_id, "Сообщение обновлено!")

    @loader.command()
    async def i(self, message):
        """Запуск поиска собеседников"""
        await self.client.send_message(message.chat_id, "Поиск собеседников начат!")
        await self.client.send_message(self.target_chat, "Искать собеседника 🌀")

    @loader.command()
    async def stop(self, message):
        """Останавливает поиск собеседников"""
        await self.client.send_message(message.chat_id, "Поиск собеседников остановлен!")
        self.is_running = False
        await self.client.send_message(self.target_chat, "Остановить 💔")
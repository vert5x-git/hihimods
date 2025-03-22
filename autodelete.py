from .. import loader
import asyncio

#meta developer: @Vert5x

class SelfDestruct(loader.Module):
    """💣 Автоматическое удаление сообщений через заданное время"""

    strings = {"name": "SelfDestruct"}

    def __init__(self):
        self.chats = {}  # Словарь {chat_id: время удаления}
        self.default_time = 10  # По умолчанию 10 секунд

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.chats = db.get(self.strings["name"], "chats", {})

    async def sdoncmd(self, message):
        """💣 Включить автоудаление (по умолчанию 10 секунд)"""
        chat_id = message.chat_id
        args = message.raw_text.split()
        time = int(args[1][:-1]) if len(args) > 1 and args[1][:-1].isdigit() else self.default_time

        self.chats[chat_id] = time
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit(f"✅ Автоудаление включено ({time} сек).")

    async def sdoffcmd(self, message):
        """🚫 Отключить автоудаление в чате"""
        chat_id = message.chat_id
        if chat_id in self.chats:
            del self.chats[chat_id]
            self.db.set(self.strings["name"], "chats", self.chats)
            await message.edit("🚫 Автоудаление отключено.")
        else:
            await message.edit("⚠️ Автоудаление уже выключено.")

    async def sdsetcmd(self, message):
        """⏳ Установить время автоудаления (пример: .sdset 30s)"""
        args = message.raw_text.split()
        if len(args) < 2 or not args[1][:-1].isdigit():
            return await message.edit("⚠️ Укажите время (пример: `.sdset 30s`).")

        self.default_time = int(args[1][:-1])
        await message.edit(f"✅ Время автоудаления установлено: {self.default_time} сек.")

    async def sdchatscmd(self, message):
        """📋 Показать чаты с включенным автоудалением"""
        if not self.chats:
            return await message.edit("⚠️ Нет активных автоудалений.")

        text = "📋 **Активные автоудаления:**\n"
        for chat, time in self.chats.items():
            text += f"- `{chat}` ⏳ {time} сек.\n"

        await message.edit(text)

    async def sdclearcmd(self, message):
        """🗑 Очистить все автоудаления"""
        self.chats.clear()
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit("🗑 Все автоудаления отключены.")

    async def watcher(self, message):
        """Автоудаление сообщений"""
        if message.chat_id in self.chats:
            await asyncio.sleep(self.chats[message.chat_id])
            await message.delete()
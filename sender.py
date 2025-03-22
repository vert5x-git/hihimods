from .. import loader
from telethon.tl.custom import Button
import asyncio

#meta developer: @Vert5x

class BulkMessenger(loader.Module):
    """📢 Массовая рассылка сообщений по чатам."""

    strings = {"name": "BulkMessenger"}

    def __init__(self):
        self.sending = False
        self.fast_mode = False
        self.chats = []

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.chats = db.get(self.strings["name"], "chats", [])

    async def addchatcmd(self, message):
        """➕ Добавить текущий чат"""
        chat_id = message.chat_id
        if chat_id not in self.chats:
            self.chats.append(chat_id)
            self.db.set(self.strings["name"], "chats", self.chats)
            await message.edit("✅ Чат добавлен.")
        else:
            await message.edit("⚠️ Уже в списке.")

    async def delchatcmd(self, message):
        """➖ Удалить текущий чат"""
        chat_id = message.chat_id
        if chat_id in self.chats:
            self.chats.remove(chat_id)
            self.db.set(self.strings["name"], "chats", self.chats)
            await message.edit("✅ Чат удалён.")
        else:
            await message.edit("⚠️ Чат не найден.")

    async def sendcmd(self, message):
        """📩 Отправить сообщение с кнопками"""
        text = message.raw_text.split(" ", 1)[1] if len(message.raw_text.split(" ", 1)) > 1 else "Сообщение по умолчанию"
        
        # Создание кнопок для взаимодействия
        buttons = [
            [Button.text("Добавить чат", resize=True), Button.text("Список чатов", resize=True)],
            [Button.text("Остановить рассылку", resize=True)],
        ]

        self.sending = True
        count = 0
        for chat in self.chats:
            if not self.sending:
                return await message.edit("⏹ Остановлено!")

            try:
                # Отправка сообщения с кнопками
                await self.client.send_message(chat, text, buttons=buttons)
                count += 1
                if not self.fast_mode:
                    await asyncio.sleep(1)
            except Exception:
                pass

        await message.edit(f"✅ Отправлено в {count} чатов.")

    async def stopcmd(self, message):
        """⏹ Остановить рассылку"""
        self.sending = False
        await message.edit("⏹ Рассылка остановлена!")

    async def fastcmd(self, message):
        """⚡ Включить быстрый режим (100 сообщений в секунду)"""
        self.fast_mode = True
        await message.edit("⚡ Быстрый режим включен.")

    async def slowcmd(self, message):
        """🐢 Включить медленный режим (1 сообщение в секунду)"""
        self.fast_mode = False
        await message.edit("🐢 Медленный режим включен.")

    async def addallcmd(self, message):
        """📥 Добавить все чаты (без каналов)"""
        dialogs = await self.client.get_dialogs()
        self.chats = [
            dialog.id for dialog in dialogs
            if (dialog.is_group or dialog.is_user) and not dialog.is_channel
        ]
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit(f"✅ Добавлено {len(self.chats)} чатов.")

    async def clearcmd(self, message):
        """🗑 Очистить список чатов"""
        self.chats = []
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit("🗑 Чаты очищены.")
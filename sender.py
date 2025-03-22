from .. import loader
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterGif

#meta developer: @Novichok_v_Crypto

class MassSender(loader.Module):
    """📢 Массовая рассылка по чатам с поддержкой фото, гиф и настройками."""

    strings = {"name": "MassSender"}

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.chats = db.get(self.strings["name"], "chats", [])
        self.allow_pms = db.get(self.strings["name"], "allow_pms", False)

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

    async def chatscmd(self, message):
        """📜 Список чатов"""
        if not self.chats:
            return await message.edit("📭 Список пуст.")
        chat_list = "\n".join([f"`{chat}`" for chat in self.chats])
        await message.edit(f"📜 Чаты:\n{chat_list}")

    async def sendcmd(self, message):
        """📩 Отправить сообщение, фото или гиф (реплай или текст)"""
        reply = await message.get_reply_message()
        text = message.raw_text.split(" ", 1)[1] if len(message.raw_text.split(" ", 1)) > 1 else None

        if not reply and not text:
            return await message.edit("⚠️ Укажите текст или ответьте на сообщение.")

        count = 0
        for chat in self.chats:
            if not self.allow_pms and chat > 0:
                continue  # Пропускаем личные сообщения

            try:
                if reply and (reply.photo or reply.gif):
                    await self.client.send_file(chat, reply)
                else:
                    await self.client.send_message(chat, text if text else reply)
                count += 1
            except Exception:
                pass

        await message.edit(f"✅ Отправлено в {count} чатов.")

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

    async def togglepmscmd(self, message):
        """🔧 Включить/выключить отправку в ЛС"""
        self.allow_pms = not self.allow_pms
        self.db.set(self.strings["name"], "allow_pms", self.allow_pms)
        await message.edit(f"🔧 Отправка в ЛС {'✅ включена' if self.allow_pms else '❌ отключена'}.")
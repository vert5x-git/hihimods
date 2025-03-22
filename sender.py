from .. import loader

#meta developer: @Novichok_v_Crypto

class MassSender(loader.Module):
    """📢 Массовая рассылка сообщений по чатам."""

    strings = {"name": "MassSender"}

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

    async def chatscmd(self, message):
        """📜 Список чатов"""
        if not self.chats:
            return await message.edit("📭 Список пуст.")
        chat_list = "\n".join([f"{chat}" for chat in self.chats])
        await message.edit(f"📜 Чаты:\n{chat_list}")

    async def sendcmd(self, message):
        """📩 Отправить сообщение (реплай или текст)"""
        reply = await message.get_reply_message()
        text = message.raw_text.split(" ", 1)[1] if len(message.raw_text.split(" ", 1)) > 1 else None

        if not reply and not text:
            return await message.edit("⚠️ Укажите текст или ответьте на сообщение.")

        msg = text if text else reply

        count = 0
        for chat in self.chats:
            try:
                await self.client.send_message(chat, msg)
                count += 1
            except Exception:
                pass

        await message.edit(f"✅ Отправлено в {count} чатов.")

    async def addallcmd(self, message):
        """📥 Добавить все чаты"""
        dialogs = await self.client.get_dialogs()
        self.chats = [dialog.id for dialog in dialogs if dialog.is_group or dialog.is_channel or dialog.is_user]
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit(f"✅ Добавлено {len(self.chats)} чатов.")

    async def clearcmd(self, message):
        """🗑 Очистить список чатов"""
        self.chats = []
        self.db.set(self.strings["name"], "chats", self.chats)
        await message.edit("🗑 Чаты очищены.")
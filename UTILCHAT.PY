from .. import loader, utils
import asyncio

class MassX(loader.Module):
    strings = {"name": "MassX"}
    
    def __init__(self):
        self.chats = []
        self.auto_mode = False
        self.delay = 2

    async def client_ready(self, client, db):
        await client.send_message('me', "🔹 MassX активен!\n📢 Команды:\n• .ms <текст/реплай>\n• .add <чат>\n• .del <чат>\n• .list\n• .auto\n• .stop\n• .speed <секунды>")

    async def ms(self, message):
        reply = await message.get_reply_message()
        args = utils.get_args_raw(message)
        
        if not args and not reply:
            return await message.edit("❌ Нет текста или реплая!")
            
        if not self.chats:
            return await message.edit("⚠️ Нет чатов!")
            
        content = reply.text if reply else args
        await self.send_message_to_chats(message.client, content)
        await message.edit(f"✅ Отправлено в {len(self.chats)} чат(ов)")

    async def add(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("❌ Укажите чат")
        if args in self.chats:
            return await message.edit("⚠️ Чат уже есть")
        self.chats.append(args)
        await message.edit(f"✅ Чат добавлен. Всего: {len(self.chats)}")

    async def delete(self, message):
        args = utils.get_args_raw(message)
        if not args or args not in self.chats:
            return await message.edit("❌ Чат не найден")
        self.chats.remove(args)
        await message.edit(f"✅ Чат удалён. Осталось: {len(self.chats)}")

    async def list(self, message):
        if not self.chats:
            return await message.edit("📭 Список пуст")
        await message.edit(f"📜 Чаты ({len(self.chats)}):\n" + "\n".join(f"• {chat}" for chat in self.chats))

    async def auto(self, message):
        if not self.chats:
            return await message.edit("❌ Нет чатов")
        self.auto_mode = True
        await message.edit(f"♾ Авторассылка запущена (задержка: {self.delay} сек)")
        while self.auto_mode:
            await self.send_message_to_chats(message.client, "Автосообщение")
            await asyncio.sleep(self.delay)

    async def stop_auto(self, message):
        if not self.auto_mode:
            return await message.edit("ℹ️ Уже остановлено")
        self.auto_mode = False
        await message.edit("⏹ Авторассылка отключена")

    async def set_speed(self, message):
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            return await message.edit("❌ Укажите число секунд")
        self.delay = int(args)
        await message.edit(f"⏱ Задержка: {self.delay} сек")

    async def send_message_to_chats(self, client, text):
        for chat in self.chats:
            try:
                await client.send_message(chat, text)
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"Ошибка в {chat}: {e}")
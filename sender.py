from .. import loader, utils
import asyncio

#meta developer: @Vert5x

class MassX(loader.Module):
    """📢 Модуль для массовой рассылки сообщений"""

    strings = {"name": "MassX"}

    def __init__(self):
        self.chats = []
        self.auto_mode = False
        self.delay = 2  # По умолчанию задержка 2 секунды между отправками

    async def send_message_to_chats(self, client, message_text):
        for chat in self.chats:
            try:
                await client.send_message(chat, message_text)
                await asyncio.sleep(self.delay)
            except Exception as e:
                print(f"Ошибка при отправке в {chat}: {e}")

    async def ms(self, message):
        """📢 Отправить сообщение в чаты (.ms <текст>)"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("⚠️ Укажите текст сообщения.")

        await self.send_message_to_chats(message.client, args)
        await message.edit(f"✅ Сообщение отправлено в {len(self.chats)} чатов.")

    async def add(self, message):
        """➕ Добавить чат (.add <чат>)"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("⚠️ Укажите ID чата или ссылку на чат.")

        self.chats.append(args)
        await message.edit(f"✅ Чат {args} добавлен.")

    async def delete(self, message):
        """❌ Удалить чат (.del <чат>)"""
        args = utils.get_args_raw(message)
        if not args or args not in self.chats:
            return await message.edit("⚠️ Чат не найден.")

        self.chats.remove(args)
        await message.edit(f"✅ Чат {args} удалён.")

    async def list(self, message):
        """📜 Список чатов (.list)"""
        if not self.chats:
            return await message.edit("⚠️ Нет чатов для рассылки.")

        await message.edit(f"📜 **Чаты:**\n" + "\n".join(self.chats))

    async def auto(self, message):
        """🔄 Включить авторассылку (.auto)"""
        self.auto_mode = True
        await message.edit("✅ Авторассылка включена.")

        while self.auto_mode:
            await self.send_message_to_chats(message.client, "Автоматическое сообщение")
            await asyncio.sleep(self.delay)

    async def stop_auto(self, message):
        """⏹ Остановить авторассылку (.stop)"""
        self.auto_mode = False
        await message.edit("⏹ Авторассылка остановлена.")

    async def set_speed(self, message):
        """⚡ Установить скорость рассылки (.speed <секунды>)"""
        args = utils.get_args_raw(message)
        if not args or not args.isdigit():
            return await message.edit("⚠️ Укажите корректную скорость (в секундах).")

        self.delay = int(args)
        await message.edit(f"✅ Скорость рассылки установлена на {self.delay} секунд.")
# meta developer: @usershprot
# meta name: Taggs
# meta version: 0.1

from .. import loader, utils
from telethon.tl.types import Message
import asyncio

@loader.tds
class TaggsMod(loader.Module):
    """Тегает всех участников по одному с заданным текстом. Команда остановки: .stoptaggs"""
    strings = {"name": "Taggs"}

    def __init__(self):
        self.running = {}

    async def taggscmd(self, message: Message):
        """[текст] — тегает всех по одному с этим текстом"""
        text = utils.get_args_raw(message)
        if not text:
            await message.edit("Укажи текст после команды.\nПример: `.taggs иди сюда`")
            return

        chat = await message.get_chat()
        if not getattr(chat, "megagroup", False):
            await message.edit("Эта команда работает только в супергруппах.")
            return

        cid = message.chat_id
        self.running[cid] = True

        await message.edit("Начинаю тегать участников по одному...")

        async for user in message.client.iter_participants(cid):
            if not self.running.get(cid):
                await message.respond("Остановлено!")
                return

            if user.bot:
                continue

            mention = (
                f"[{user.first_name}](tg://user?id={user.id})"
                if not user.username else f"@{user.username}"
            )

            try:
                await message.respond(f"{mention} {text}")
                await asyncio.sleep(2)
            except:
                continue

        self.running.pop(cid, None)
        await message.respond("Готово!")
        await message.delete()

    async def stoptaggscmd(self, message: Message):
        """Останавливает тегание"""
        cid = message.chat_id
        if self.running.get(cid):
            self.running[cid] = False
            await message.edit("Останавливаю...")
        else:
            await message.edit("Ничего не запущено.")
from .. import loader, utils
import logging
import re

# meta developer: @hihimods

logger = logging.getLogger(__name__)

class AutoProbe(loader.Module):
    """🔍 Авто-пробив + фан-статистика"""

    strings = {"name": "AutoProbe"}

    def __init__(self):
        self.db = {}

    async def client_ready(self, client, db):
        self.client = client

    async def watcher(self, message):
        if message.is_private:
            await self.probe_user(message, message.sender_id)

    async def probe(self, message):
        """🔎 Пробить пользователя (.probe <реплай/юзернейм/ID>)"""
        args = utils.get_args_raw(message)
        user = await self.get_user(message, args)
        if user:
            await self.probe_user(message, user.id, send_to_me=False)

    async def get_user(self, message, args):
        if message.is_reply:
            return await message.get_reply_message().get_sender()
        if args.isdigit():
            return await self.client.get_entity(int(args))
        if args.startswith("@"):
            return await self.client.get_entity(args)
        return None

    async def probe_user(self, message, user_id, send_to_me=True):
        user = await self.client.get_entity(user_id)
        user_id = str(user.id)

        if user_id not in self.db:
            self.db[user_id] = {"messages": 0, "total_length": 0, "words": {}}

        self.db[user_id]["messages"] += 1
        self.db[user_id]["total_length"] += len(message.text)
        words = re.findall(r"\b\w+\b", message.text.lower())

        for word in words:
            self.db[user_id]["words"][word] = self.db[user_id]["words"].get(word, 0) + 1

        top_words = sorted(self.db[user_id]["words"].items(), key=lambda x: x[1], reverse=True)[:3]
        top_words_text = ", ".join(f"{w[0]} ({w[1]})" for w in top_words) if top_words else "Нет данных"

        user_info = (
            f"🔎 **Пробив пользователя:**\n"
            f"🆔 **ID:** `{user.id}`\n"
            f"👤 **Username:** @{user.username if user.username else 'Нет'}\n"
            f"💎 **Premium:** {'✅ Да' if getattr(user, 'premium', False) else '❌ Нет'}\n"
            f"📞 **Номер:** `{user.phone if user.phone else 'Скрыт'}`\n"
            f"📊 **Сообщений:** {self.db[user_id]['messages']}\n"
            f"📏 **Средняя длина:** {round(self.db[user_id]['total_length'] / self.db[user_id]['messages'], 1)} символов\n"
            f"🔝 **Любимые слова:** {top_words_text}"
        )

        if send_to_me:
            await self.client.send_message("me", user_info)
        else:
            await message.edit(user_info)
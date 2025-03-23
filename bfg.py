from .. import loader, utils
import asyncio
import random
from telethon.tl.functions.account import UpdateProfileRequest

#meta developer: @Vert5x

class NickChanger(loader.Module):
    """🔄 Автосмена ника в Telegram и BFG"""

    strings = {"name": "NickChanger"}

    def __init__(self):
        self.auto_mode = False
        self.delay = 600
        self.nicks = ["Player123", "CryptoKing", "GramHunter", "GamerX", "AnonUser"]
        self.bfg_bot = "@bforgame_bot"

    async def change_nick(self, client, mode, new_nick=None):
        new_nick = new_nick or random.choice(self.nicks)

        if mode in ["tg", "all"]:
            await client(UpdateProfileRequest(first_name=new_nick))

        if mode in ["bfg", "all"]:
            await client.send_message(self.bfg_bot, f"Сменить ник {new_nick}")

        return new_nick

    async def nickcmd(self, message):
        """🔄 Сменить ник (.n <ник> [tg/bfg/all])"""
        args = utils.get_args_raw(message).split()
        new_nick = args[0] if args else None
        mode = args[1] if len(args) > 1 and args[1] in ["tg", "bfg", "all"] else "all"

        new_nick = await self.change_nick(message.client, mode, new_nick)
        await message.edit(f"✅ Ник изменён ({mode.upper()}): {new_nick}")

    async def nlistcmd(self, message):
        """📜 Список ников (.nl)"""
        await message.edit("📜 **Доступные ники:**\n" + "\n".join(self.nicks))

    async def naddcmd(self, message):
        """➕ Добавить ник (.na <ник>)"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("⚠️ Укажите ник.")

        self.nicks.append(args)
        await message.edit(f"✅ Ник `{args}` добавлен.")

    async def nautc(self, message):
        """🔄 Автосмена ника (.naut <интервал> [tg/bfg/all])"""
        args = utils.get_args_raw(message).split()
        if args and args[0][:-1].isdigit():
            self.delay = int(args[0][:-1]) * 60

        mode = args[1] if len(args) > 1 and args[1] in ["tg", "bfg", "all"] else "all"

        self.auto_mode = True
        await message.edit(f"✅ Автоник включён ({self.delay//60} мин, {mode.upper()})")

        while self.auto_mode:
            await self.change_nick(message.client, mode)
            await asyncio.sleep(self.delay)

    async def nstopcmd(self, message):
        """⏹ Остановить автоник (.nst)"""
        self.auto_mode = False
        await message.edit("⏹ Автоник отключён.")
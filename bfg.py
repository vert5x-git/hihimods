from .. import loader, utils
import asyncio
import random
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.channels import EditAdminRequest, InviteToChannelRequest
from telethon.tl.types import ChatAdminRights

#meta developer: @Vert5x

class AutoNickChatManager(loader.Module):
    """🔄 Автосмена ника + Автосоздание чатов с @bforgame_bot"""

    strings = {"name": "AutoNickChatManager"}

    def __init__(self):
        self.auto_mode = False
        self.delay = 600
        self.nick_list = ["Player123", "CryptoKing", "GramHunter", "GamerX", "AnonUser"]
        self.chat_id = None

    async def client_ready(self, client, db):
        await self.auto_create_chat(client)
        await self.auto_change_nick(client, mode="all")

    async def auto_create_chat(self, client):
        chat_name = "BFG"
        new_chat = await client(CreateChatRequest(users=[], title=chat_name))
        self.chat_id = new_chat.chats[0].id

        await asyncio.sleep(3)
        try:
            await client(InviteToChannelRequest(self.chat_id, ["@bforgame_bot"]))
        except:
            pass

        await asyncio.sleep(5)
        try:
            await client(EditAdminRequest(
                self.chat_id,
                "@bforgame_bot",
                ChatAdminRights(
                    post_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True
                ),
                rank="Bot"
            ))
        except:
            pass

        await asyncio.sleep(2)
        try:
            await client.archive_chats([self.chat_id])
        except:
            pass

    async def auto_change_nick(self, client, mode="all"):
        new_nick = random.choice(self.nick_list)

        if mode in ["tg", "all"]:
            try:
                await client(UpdateProfileRequest(first_name=new_nick))
            except:
                pass

        if mode in ["bfg", "all"] and self.chat_id:
            try:
                await client.send_message(self.chat_id, f"Сменить ник {new_nick}")
            except:
                pass

    async def nickcmd(self, message):
        args = utils.get_args_raw(message).split()
        new_nick = args[0] if args else random.choice(self.nick_list)
        mode = args[1] if len(args) > 1 else "all"

        if mode in ["tg", "all"]:
            try:
                await message.client(UpdateProfileRequest(first_name=new_nick))
                await message.edit(f"✅ Ник в **Telegram** изменён на: {new_nick}")
            except:
                await message.edit(f"❌ Ошибка смены ника в Telegram")

        if mode in ["bfg", "all"] and self.chat_id:
            try:
                await message.client.send_message(self.chat_id, f"Сменить ник {new_nick}")
                await message.edit(f"✅ Ник в **BFG** изменён на: {new_nick}")
            except:
                await message.edit(f"❌ Ошибка смены ника в BFG")

    async def nicklistcmd(self, message):
        await message.edit("📜 **Список доступных ников:**\n" + "\n".join(self.nick_list))

    async def nickaddcmd(self, message):
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("⚠️ Укажите ник.")

        self.nick_list.append(args)
        await message.edit(f"✅ Ник `{args}` добавлен в список.")

    async def nickautocmd(self, message):
        args = utils.get_args_raw(message).split()
        if args and args[0][:-1].isdigit():
            self.delay = int(args[0][:-1]) * 60

        mode = args[1] if len(args) > 1 else "all"

        self.auto_mode = True
        await message.edit(f"✅ Автосмена ника включена (каждые {self.delay//60} мин, режим: {mode}).")

        while self.auto_mode:
            await self.auto_change_nick(message.client, mode)
            await asyncio.sleep(self.delay)

    async def nickstopcmd(self, message):
        self.auto_mode = False
        await message.edit("⏹ Автосмена ника отключена.")
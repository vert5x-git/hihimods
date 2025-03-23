from .. import loader, utils
import asyncio
import random
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.messages import CreateChatRequest
from telethon.tl.functions.channels import EditAdminRequest
from telethon.tl.types import ChatAdminRights

#meta developer: @Vert5x

class AutoNickChatManager(loader.Module):
    """🔄 Автосмена ника + Автосоздание чатов с @bforgame_bot"""

    strings = {"name": "AutoNickChatManager"}

    def __init__(self):
        self.auto_mode = False
        self.delay = 600  # 10 минут
        self.nick_list = ["Player123", "CryptoKing", "GramHunter", "GamerX", "AnonUser"]
        self.chat_id = None  # ID созданного чата

    async def client_ready(self, client, db):
        """🔄 Автоматическое создание чата и автосмена ника при запуске"""
        await self.auto_create_chat(client)
        await self.auto_change_nick(client)

    async def auto_create_chat(self, client):
        """🤖 Авто-создание чата с @bforgame_bot"""
        chat_name = "BFG AutoChat"

        new_chat = await client(CreateChatRequest(users=["@bforgame_bot"], title=chat_name))
        self.chat_id = new_chat.chats[0].id

        await asyncio.sleep(5)  # Ждём, пока бот зайдёт

        try:
            await client(EditAdminRequest(
                channel=self.chat_id,
                user_id="@bforgame_bot",
                admin_rights=ChatAdminRights(
                    post_messages=True,
                    delete_messages=True,
                    ban_users=True,
                    invite_users=True,
                    pin_messages=True
                ),
                rank="Bot"
            ))
        except:
            pass  # Если не удалось, просто продолжаем

        await asyncio.sleep(2)
        try:
            await client.archive_chats([self.chat_id])  # Архивируем
        except:
            pass  # Если не получилось, просто продолжаем

    async def auto_change_nick(self, client):
        """🔄 Автосмена ника при запуске"""
        new_nick = random.choice(self.nick_list)
        try:
            await client(UpdateProfileRequest(first_name=new_nick))
        except:
            pass
        try:
            if self.chat_id:
                await client.send_message(self.chat_id, f"/nick {new_nick}")
        except:
            pass

    async def nickcmd(self, message):
        """🔄 Сменить ник (.nick <ник>)"""
        args = utils.get_args_raw(message)
        new_nick = args if args else random.choice(self.nick_list)

        try:
            await message.client(UpdateProfileRequest(first_name=new_nick))
            await message.edit(f"✅ Ник в **Telegram** изменён на: {new_nick}")
        except:
            await message.edit(f"❌ Ошибка смены ника в Telegram")

        try:
            if self.chat_id:
                await message.client.send_message(self.chat_id, f"/nick {new_nick}")
                await message.edit(f"✅ Ник в **@bforgame_bot** изменён на: {new_nick}")
        except:
            await message.edit(f"❌ Ошибка смены ника в @bforgame_bot")

    async def nicklistcmd(self, message):
        """📜 Список доступных ников"""
        await message.edit("📜 **Список доступных ников:**\n" + "\n".join(self.nick_list))

    async def nickaddcmd(self, message):
        """➕ Добавить ник в список (.nickadd НовыйНик)"""
        args = utils.get_args_raw(message)
        if not args:
            return await message.edit("⚠️ Укажите ник.")

        self.nick_list.append(args)
        await message.edit(f"✅ Ник `{args}` добавлен в список.")

    async def nickautocmd(self, message):
        """🔄 Автосмена ника (.nickauto 10m)"""
        args = utils.get_args_raw(message)
        if args and args[:-1].isdigit():
            self.delay = int(args[:-1]) * 60

        self.auto_mode = True
        await message.edit(f"✅ Автосмена ника включена (каждые {self.delay//60} мин).")

        while self.auto_mode:
            new_nick = random.choice(self.nick_list)

            try:
                await message.client(UpdateProfileRequest(first_name=new_nick))
            except:
                pass

            try:
                if self.chat_id:
                    await message.client.send_message(self.chat_id, f"/nick {new_nick}")
            except:
                pass

            await asyncio.sleep(self.delay)

    async def nickstopcmd(self, message):
        """⏹ Остановить автосмену ника"""
        self.auto_mode = False
        await message.edit("⏹ Автосмена ника отключена.")
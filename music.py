from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.types import ChatAdminRights
from .. import loader, utils
import asyncio

@loader.tds
class MusicFinderMod(loader.Module):
    """Ищет музыку через @smusic2bot и отправляет её в чат"""
    strings = {"name": "MusicFinder"}

    def __init__(self):
        self.group_id = None
        self.bot_username = "smusic2bot"
        self.max_retries = 3
        self.retry_interval = 5

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.group_id = self.db.get(self.strings["name"], "group_id", None)

        if self.group_id is None:
            result = await client(CreateChannelRequest(
                title="InternalChat_" + utils.rand(6),
                about="Hidden group for music search",
                megagroup=True
            ))
            self.group_id = result.chats[0].id
            bot_entity = await client.get_entity(self.bot_username)

            await client(InviteToChannelRequest(
                channel=self.group_id,
                users=[bot_entity]
            ))

            await client(EditAdminRequest(
                channel=self.group_id,
                user_id=bot_entity,
                admin_rights=ChatAdminRights(
                    post_messages=True,
                    add_admins=False,
                    delete_messages=True,
                    ban_users=False,
                    invite_users=True,
                    pin_messages=False,
                    change_info=False
                ),
                rank="Bot"
            ))

            self.db.set(self.strings["name"], "group_id", self.group_id)

    @loader.command()
    async def sfind(self, message):
        """Поиск трека через @smusic2bot: .sfind <название> или в ответ на сообщение"""
        query = utils.get_args_raw(message)
        if not query and message.is_reply:
            reply = await message.get_reply_message()
            if reply and reply.text:
                query = reply.text.strip()

        if not query:
            await message.edit("Укажи запрос: `.sfind <название>` или ответь на сообщение.")
            return

        status = await message.edit("Ищу трек...")
        search_query = f"Найти {query}"

        sent = await self.client.send_message(self.group_id, search_query)
        retry_count = 0

        while retry_count < self.max_retries:
            async for msg in self.client.iter_messages(self.group_id, offset_id=sent.id, reverse=True, limit=5):
                if msg.sender and msg.sender.username == self.bot_username and msg.media:
                    await status.edit("Отправлено.")
                    await asyncio.sleep(0.3)
                    await status.delete()

                    await self.client.send_message(
                        message.chat_id,
                        msg.text or "",
                        file=msg.media,
                        reply_to=message.reply_to_msg_id,
                        silent=True
                    )

                    # Очистка из скрытого чата
                    await self.client.delete_messages(self.group_id, [sent.id, msg.id])
                    return

            retry_count += 1
            await asyncio.sleep(self.retry_interval)

        await status.edit("Ответ от бота не получен, возможно, проблема с запросом.")
        await asyncio.sleep(2)
        await status.delete()
        await self.client.delete_messages(self.group_id, [sent.id])
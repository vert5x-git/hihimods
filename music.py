from telethon.tl.functions.channels import CreateChannelRequest, InviteToChannelRequest, EditAdminRequest
from telethon.tl.types import ChatAdminRights
from .. import loader, utils
import asyncio

@loader.tds
class MusicFinderMod(loader.Module):
    strings = {"name": "MusicFinder"}

    def __init__(self):
        self.group_id = None
        self.bot_username = "smusic2bot"

    async def client_ready(self, client, db):
        self.client = client
        self.db = db
        self.group_id = self.db.get(self.strings["name"], "group_id", None)

        if self.group_id is None:
            result = await client(CreateChannelRequest(
                title="MusicFinder_Hidden_Group",
                about="Hidden group for music search",
                megagroup=True
            ))
            self.group_id = result.chats[0].id

            await client(InviteToChannelRequest(
                channel=self.group_id,
                users=[self.bot_username]
            ))

            await client(EditAdminRequest(
                channel=self.group_id,
                user_id=self.bot_username,
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

            # Уведомление в “Избранное” о функционале модуля
            await client.send_message('me', 'Модуль MusicFinder установлен: команда .sfind ищет трек по названию')

    @loader.command()
    async def sfind(self, message):
        query = utils.get_args_raw(message)
        if not query and message.is_reply:
            reply = await message.get_reply_message()
            if reply and reply.text:
                query = reply.text.strip()

        await message.delete()
        if not query:
            return

        search_query = f"найти {query}"
        sent = await self.client.send_message(self.group_id, search_query)

        for _ in range(10):
            async for msg in self.client.iter_messages(self.group_id, min_id=sent.id, reverse=True, limit=5):
                if msg.sender and msg.sender.username == self.bot_username and msg.media:
                    await self.client.send_message(
                        message.chat_id,
                        msg.text or "",
                        file=msg.media,
                        reply_to=message.reply_to_msg_id,
                        silent=True
                    )
                    return
            await asyncio.sleep(1)
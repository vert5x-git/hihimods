# meta developer: @shprot03
# meta name: SMusicTrack
# meta version: 1.0

from .. import loader, utils
from telethon.tl.functions.messages import CreateChatRequest, DeleteChatUserRequest, AddChatUserRequest
from telethon.tl.functions.messages import GetMessagesRequest
from telethon.tl.types import InputUser, InputPeerUser
import asyncio

class SMusicTrackMod(loader.Module):
    strings = {"name": "SMusicTrack"}

    async def sfindcmd(self, message):
        query = utils.get_args_raw(message)
        if not query:
            return await message.edit("Укажи название трека.")

        me = await message.client.get_me()
        smusic = await message.client.get_entity("smusic2bot")

        try:
            # Создание временной группы
            group = await message.client(CreateChatRequest(users=[smusic], title="TempSMusicGroup"))

            await asyncio.sleep(1)

            # Отправка запроса в группу
            await message.client.send_message(group.chats[0].id, query)

            await asyncio.sleep(4)

            async for msg in message.client.iter_messages(group.chats[0].id, from_user_id=smusic.id, limit=5):
                if msg.audio or msg.document:
                    await msg.forward_to(message.chat_id)
                    break
            else:
                await message.edit("Трек не найден.")
                return

            await message.client(DeleteChatUserRequest(group.chats[0].id, smusic.id))
            await message.client(DeleteChatUserRequest(group.chats[0].id, me.id))

        except Exception as e:
            await message.edit(f"Ошибка: {e}")
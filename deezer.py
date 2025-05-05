# meta developer: @shprot03
# meta name: SMusicTrack
# meta version: 1.2

from .. import loader, utils
from telethon.tl.functions.messages import CreateChatRequest, DeleteChatUserRequest
from telethon.tl.functions.channels import LeaveChannelRequest
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
            chat = await message.client(CreateChatRequest(users=[smusic], title="TempSMusicGroup"))
            group_id = chat.chats[0].id

            await asyncio.sleep(1)

            # Отправка "найти {запрос}"
            await message.client.send_message(group_id, f"найти {query}")
            await message.edit("Ожидаю ответ от @smusic2bot...")

            await asyncio.sleep(6)

            async for msg in message.client.iter_messages(group_id, limit=10):
                if msg.sender_id == smusic.id and (msg.audio or msg.document):
                    await msg.forward_to(message.chat_id)
                    break
            else:
                await message.edit("Трек не найден.")
                return

            await asyncio.sleep(1)
            await message.client(DeleteChatUserRequest(group_id, smusic.id))
            await asyncio.sleep(1)
            await message.client(LeaveChannelRequest(group_id))
            await message.delete()

        except Exception as e:
            await message.edit(f"Ошибка: {e}")
from telethon.tl.functions.messages import DeleteMessages from .. import loader, utils

class MassDeleteMod(loader.Module): """Удаление всех ваших сообщений в группе"""

strings = {
    "name": "MassDelete",
    "processing": "🚀 Удаление сообщений...",
    "done": "✅ Удаление завершено!"
}

async def massdelcmd(self, message):
    """Удаляет все ваши сообщения в текущем чате"""
    chat = message.chat_id
    me = await message.client.get_me()
    
    await utils.answer(message, self.strings["processing"])
    
    all_messages = []
    async for msg in message.client.iter_messages(chat, from_user=me.id):
        all_messages.append(msg.id)
    
    if all_messages:
        await message.client(DeleteMessages(all_messages, revoke=True))
    
    await utils.answer(message, self.strings["done"])


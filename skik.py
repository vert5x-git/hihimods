from hikka import loader, utils
from telethon.tl.functions.channels import JoinChannelRequest

class AutoRejoinMod(loader.Module):
    "Эффектный выход и возврат в чат."
    
    strings = {
        "name": "AutoRejoin",
        "suicide_msg": "Произошло СамоУбийство. Оставленное послание: Воскресите потом",
        "revive_msg": "Я вернулся с того света!"
    }

    def __init__(self):
        self.config = loader.ModuleConfig("TRIGGER_WORDS", ["воскресить", "вернись"], "Слова для возвращения")
        self._left_chats = set()

    async def skikcmd(self, message):
        "Выйти из чата эффектно."
        chat = message.chat_id
        self._left_chats.add(chat)
        await utils.answer(message, self.strings["suicide_msg"])
        await message.client.kick_participant(chat, "me")

    async def watcher(self, message):
        if not getattr(message, "text", None) or not message.chat or message.chat_id not in self._left_chats:
            return
        
        text = message.text.lower()
        trigger_words = self.config["TRIGGER_WORDS"]
        if any(word in text for word in trigger_words) and (message.is_reply or message.mentioned):
            chat = message.chat_id
            self._left_chats.remove(chat)
            await message.client(JoinChannelRequest(chat))
            await utils.answer(message, self.strings["revive_msg"])
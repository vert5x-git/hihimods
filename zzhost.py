# meta developer : @usershprot 
# -*- coding: utf-8 -*-
# Модуль Hikka: Управление #ZenZoneHosting 

from telethon import events
from .. import loader, utils
from telethon.tl.custom.button import Button


@loader.tds
class ZZHostControl(loader.Module):
    """Управление настоящим @zzhost_bot"""
    strings = {"name": "ZZHostControl"}

    async def client_ready(self, client, db):
        self.client = client
        self.bot = "zzhost_bot"
        self._msg = None
        self._user_id = (await client.get_me()).id

    async def zzstartcmd(self, message):
        """Найти последнее сообщение от @zzhost_bot с кнопками"""
        async for msg in self.client.iter_messages(self.bot, limit=20):
            if msg.buttons:
                self._msg = msg
                await self.client.send_message(
                    message.chat_id,
                    "Меню управления @zzhost_bot:",
                    buttons=msg.buttons
                )
                await message.delete()
                return
        await message.edit("❌ Не найдено сообщение с кнопками от @zzhost_bot.")

    @events.register(events.CallbackQuery)
    async def zzhost_button_handler(self, event):
        # Только владелец
        if event.sender_id != self._user_id:
            return await event.answer("⛔ Только для владельца.", alert=True)

        if not self._msg:
            return await event.answer("⚠️ Сначала введи .zzstart", alert=True)

        # Поиск совпадения кнопки по данным
        clicked = None
        for row in self._msg.buttons:
            for btn in row:
                if btn.data == event.data or btn.text == event.data.decode("utf-8"):
                    clicked = btn
                    break

        if not clicked:
            return await event.answer("❌ Кнопка не найдена в сообщении.", alert=True)

        await self._msg.click(data=clicked.data or clicked.text)
        await event.answer("✅ Команда отправлена.", alert=True)
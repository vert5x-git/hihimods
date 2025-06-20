# meta developer: @usershprot
# meta name: PremiumAutoResp
# meta version: 1.1
# meta description: Автоответчик в стиле Telegram Premium ✨
# meta license: MIT
# meta copyright: © 2025
# MIT License
# 
# Copyright (c) 2025 @usershprot
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.

# Далее весь код, который я уже тебе дал выше, начинается с:
# from telethon.tl.types import Message
# ...async def pacmd(self, message):
        """Вкл/выкл автоответчик"""
        self.config["enabled"] = not self.config["enabled"]
        status = self.strings("status_on") if self.config["enabled"] else self.strings("status_off")
        await utils.answer(message, f"<b>Автоответчик:</b> {status}")

    async def pagcmd(self, message):
        """Вкл/выкл автоответ в группах"""
        self.config["in_groups"] = not self.config["in_groups"]
        status = self.strings("status_on") if self.config["in_groups"] else self.strings("status_off")
        await utils.answer(message, f"<b>Ответы в группах:</b> {status}")

    async def padcmd(self, message):
        """Установить задержку: .pad 2 6"""
        args = utils.get_args(message)
        if len(args) != 2 or not all(a.isdigit() for a in args):
            return await utils.answer(message, "<b>Использование:</b> <code>.pad 2 5</code>")
        self.config["delay"] = list(map(int, args))
        await utils.answer(message, f"✅ Задержка установлена: {self.config['delay']} сек")

    async def pamcmd(self, message):
        """Управление сообщениями:
        .pam — показать
        .pam add <текст>
        .pam del <номер>
        .pam clear
        """
        args = utils.get_args_raw(message)
        msgs = self.config["messages"]

        if not args:
            if not msgs:
                return await utils.answer(message, "<b>Список сообщений пуст.</b>")
            out = "<b>Автоответы:</b>\n" + "\n".join(
                [f"<code>{i+1}.</code> {m}" for i, m in enumerate(msgs)]
            )
            return await utils.answer(message, out)

        if args.startswith("add "):
            text = args[4:].strip()
            if not text:
                return await utils.answer(message, "❌ Пустое сообщение")
            msgs.append(text)
            self.config["messages"] = msgs
            return await utils.answer(message, "✅ Добавлено")

        if args.startswith("del "):
            try:
                index = int(args[4:]) - 1
                deleted = msgs.pop(index)
                self.config["messages"] = msgs
                return await utils.answer(message, f"🗑 Удалено: {deleted}")
            except:
                return await utils.answer(message, "❌ Неправильный номер")

        if args == "clear":
            self.config["messages"] = []
            return await utils.answer(message, "🧹 Все сообщения удалены")

        return await utils.answer(message, "❓ Используй: .pam, add, del, clear")

    async def parcmd(self, message):
        """Вкл/выкл режим: 1 ответ или каждый раз"""
        self.config["one_reply_per_user"] = not self.config["one_reply_per_user"]
        mode = "🟢 Только 1 ответ на пользователя" if self.config["one_reply_per_user"] else "🔁 Ответ на каждое сообщение"
        await utils.answer(message, f"<b>Режим автоответа:</b> {mode}")
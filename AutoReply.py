from .. import loader, utils
from telethon.tl.custom import Button
import os
import time

#meta developer: @Vert5x

class AutoReplyMod(loader.Module):
    """Автоответчик для новых ЛС с базой пользователей и инлайн-кнопками"""

    strings = {
        "name": "AutoReply",
        "enabled": "✅ Автоответчик включён",
        "disabled": "❌ Автоответчик выключен",
        "reply_set": "✍️ Сообщение автоответа обновлено",
        "image_set": "🖼 Изображение автоответа обновлено",
        "no_image": "⚠️ Нет изображения",
        "arset": "✍️ Установить текст и изображение для автоответа",
        "arimage": "🖼 Установить изображение для автоответа",
        "artoggle": "🔄 Включить/выключить автоответчик",
    }

    DEFAULT_MESSAGE = (
        "⭐️ *Сообщение доставлено! (Но хозяин в offline...)*\n\n"
        "Не волнуйтесь! Владелец скоро вернется в сеть, а пока…\n\n"
        "• *📖 Читать FAQ* — возможно, там уже есть ответ!\n"
        "• *💰 Отправить донат* — и ускорить ответ!\n"
        "• *✉ Написать снова* — попробуйте еще раз!\n\n"
        "Спасибо за ваше терпение! ❤️"
    )

    DEFAULT_IMAGE_URL = "https://raw.githubusercontent.com/HelZDev/media-files/refs/heads/main/IMG_20250323_023021_126.jpg"
    REPLY_TIMEOUT = 3600

    async def client_ready(self, client, db):
        self.db = db
        self.reply_enabled = self.db.get("AutoReply", "enabled", False)
        self.reply_text = self.db.get("AutoReply", "reply_text", self.DEFAULT_MESSAGE)
        self.image_path = self.db.get("AutoReply", "image_path", None)
        self.users_db = self.db.get("AutoReply_users", {})

    def get_inline_keyboard(self):
        return [
            [Button.url("📖 Читать FAQ", "https://твой-сайт.com/faq")],
            [Button.url("💰 Отправить донат", "https://donate.com")],
            [Button.inline("✉ Написать снова", b"send_again")]
        ]

    async def artogglecmd(self, message):
        """Включает/выключает автоответчик"""
        self.reply_enabled = not self.reply_enabled
        self.db.set("AutoReply", "enabled", self.reply_enabled)
        await utils.answer(message, self.strings["enabled"] if self.reply_enabled else self.strings["disabled"])

    async def arsetcmd(self, message):
        """Задает новое сообщение и изображение для автоответчика"""
        reply = await message.get_reply_message()
        text = utils.get_args_raw(message) or (reply.text if reply else None)
        
        image_path = None
        if reply and reply.media:
            image_path = os.path.join(os.getcwd(), "auto_reply.jpg")
            await reply.download_media(image_path)
        
        if not text and not image_path:
            return await utils.answer(message, "⚠️ Укажите текст/фото или ответьте на сообщение!")

        if text:
            self.db.set("AutoReply", "reply_text", text)
            self.reply_text = text

        if image_path:
            self.db.set("AutoReply", "image_path", image_path)
            self.image_path = image_path

        await utils.answer(message, "✅ Автоответ обновлён!")

    async def arimagecmd(self, message):
        """Задает изображение для автоответчика"""
        reply = await message.get_reply_message()
        if not reply or not reply.media:
            return await utils.answer(message, self.strings["no_image"])

        file_path = os.path.join(os.getcwd(), "auto_reply.jpg")
        await reply.download_media(file_path)

        self.db.set("AutoReply", "image_path", file_path)
        self.image_path = file_path
        await utils.answer(message, self.strings["image_set"])

    async def watcher(self, message):
        """Отправляет автоответ в новых ЛС (кроме ботов) один раз, сбрасывая список через час"""
        if not self.reply_enabled or not message.is_private or message.out:
            return

        user = await message.get_sender()
        if user.bot:
            return

        user_id = message.chat_id
        current_time = time.time()

        user_data = self.users_db.get(user_id, {"count": 0, "last_reply": 0})
        
        if current_time - user_data["last_reply"] < self.REPLY_TIMEOUT:
            return

        await message.client.send_file(
            user_id,
            self.image_path if self.image_path else self.DEFAULT_IMAGE_URL,
            caption=self.reply_text,
            buttons=self.get_inline_keyboard(),
            parse_mode="MarkdownV2"
        )

        user_data["count"] += 1
        user_data["last_reply"] = current_time
        self.users_db[user_id] = user_data
        self.db.set("AutoReply_users", self.users_db)

    @loader.inline_handler()
    async def inline_button_handler(self, call):
        """Обработка инлайн-кнопки "Написать снова" """
        if call.data == b"send_again":
            await call.answer("Попробуйте написать снова!", alert=True)
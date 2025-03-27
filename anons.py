import asyncio
import random
import logging
from hikka import loader

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Чат для работы
TARGET_CHAT = "@palata_6numberr"

# Сообщение для отправки
MESSAGE_TEXT = (
    "🌟 Приглашаем вас на ламповые посиделки в нашем чате! 🌟\n\n"
    "Присоединяйтесь к дружной компании, где вас ждут:\n\n"
    "✨ Добрые администраторы, готовые помочь и поддержать!\n"
    "🎉 Увлекательные розыгрыши на звёзды!\n"
    "💬 Интересные обсуждения и весёлые беседы!\n\n"
    "Не упустите возможность стать частью нашей дружной семьи!\n\n"
    "👨‍👩‍👧 Требования к семье:\n\n"
    "🔞 Возраст: от 13\n"
    "👤 Пол: не важен!!!\n\n"
    "👉 Ссылка на чат: @palata_6numberr\n\n"
    "Ждем вас с нетерпением! 💖"
)

is_running = False  # Флаг активности


class AutoChat(loader.Module):
    """Авто-поиск собеседников и реклама"""
    strings = {"name": "AutoChat"}

    async def client_ready(self, client, db):
        self.client = client
        logger.info("Модуль AutoChat загружен.")

    async def watcher(self, message):
        global is_running

        try:
            if not message.text:
                return  # Игнорируем сообщения без текста

            text = message.text.strip().lower()
            logger.info(f"Получено сообщение: {text}")

            # Команда для начала поиска
            if text == "/i" and not is_running:
                is_running = True
                logger.info("Начинаем поиск нового диалога.")
                await asyncio.sleep(5)
                await self.client.send_message(TARGET_CHAT, "Искать собеседника 🌀")
                return

            if is_running:
                if "ты завершил диалог!" in message.raw_text.lower():
                    logger.info("Диалог завершён, ищем нового собеседника.")
                    await asyncio.sleep(3)
                    await self.client.send_message(TARGET_CHAT, "Искать собеседника 🌀")
                    return

                if "💭 собеседник уже в диалоге, общайтесь!" in message.raw_text.lower():
                    logger.info("Отправляем приглашение в чат.")
                    await self.client.send_message(TARGET_CHAT, MESSAGE_TEXT)

                    await asyncio.sleep(random.randint(1, 3))

                    logger.info("Останавливаем диалог.")
                    await self.client.send_message(TARGET_CHAT, "Остановить 💔")
                    return

        except Exception as e:
            logger.error(f"Ошибка в обработке: {e}")
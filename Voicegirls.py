#meta developer: @Vert5x

import pyttsx3
import io
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class AutoVoiceTTSMod(loader.Module):
    """Модуль для озвучивания текста с выбором голоса (без зависимостей)"""

    strings = {"name": "AutoVoiceTTS"}

    async def ocmd(self, message: Message):
        """Использование: .o [м/ж] <текст> — озвучить текст мужским или женским голосом"""
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("❌ Введите текст для озвучки!")
            return

        words = args.split(" ", 1)

        # Определяем голос
        if words[0].lower() == "м":
            voice = "male"
            text = words[1] if len(words) > 1 else "Ошибка: нет текста"
        elif words[0].lower() == "ж":
            voice = "female"
            text = words[1] if len(words) > 1 else "Ошибка: нет текста"
        else:
            voice = "female"  # По умолчанию женский голос
            text = args

        await message.edit(f"🎙 Озвучиваю текст ({'Мужской' if voice == 'male' else 'Женский'} голос)...")

        try:
            audio_fp = io.BytesIO()

            # Используем pyttsx3 (он работает без зависимостей)
            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            # Выбираем голос
            if voice == "male":
                engine.setProperty("voice", voices[0].id)  # Обычно [0] — мужской
            else:
                engine.setProperty("voice", voices[1].id)  # Обычно [1] — женский

            engine.save_to_file(text, "output.mp3")
            engine.runAndWait()

            with open("output.mp3", "rb") as f:
                audio_fp.write(f.read())

            audio_fp.seek(0)

            await message.client.send_file(
                message.chat_id, 
                audio_fp, 
                voice_note=True
            )
            await message.delete()

        except Exception as e:
            await message.edit(f"❌ Ошибка озвучки: {str(e)}")
#meta developer: @Vert5x

from gtts import gTTS
import io
import pyttsx3
import langdetect
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class AutoVoiceTTSMod(loader.Module):
    """Модуль для озвучивания текста с выбором голоса и автоопределением языка"""

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

        # Определяем язык текста
        try:
            lang = langdetect.detect(text)
        except:
            lang = "ru"  # Если не удалось определить язык, используем русский

        await message.edit(f"🎙 Озвучиваю текст ({'Мужской' if voice == 'male' else 'Женский'} голос, {lang})...")

        try:
            audio_fp = io.BytesIO()

            if voice == "male":
                # Используем pyttsx3 для мужского голоса (но он не поддерживает все языки)
                engine = pyttsx3.init()
                voices = engine.getProperty("voices")
                engine.setProperty("voice", voices[0].id)  # Обычно [0] — мужской голос
                engine.save_to_file(text, "output.mp3")
                engine.runAndWait()

                with open("output.mp3", "rb") as f:
                    audio_fp.write(f.read())

            else:
                # Используем gTTS для женского голоса (поддерживает много языков)
                tts = gTTS(text=text, lang=lang)
                tts.write_to_fp(audio_fp)

            audio_fp.seek(0)

            await message.client.send_file(
                message.chat_id, 
                audio_fp, 
                voice_note=True
            )
            await message.delete()

        except Exception as e:
            await message.edit(f"❌ Ошибка озвучки: {str(e)}")
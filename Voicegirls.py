#meta developer: @Vert5x

import pyttsx3
import io
import os
import subprocess
from telethon.tl.types import Message
from .. import loader, utils

@loader.tds
class AutoVoiceTTSMod(loader.Module):
    """Модуль для озвучивания текста с выбором голоса (с автоматической установкой зависимостей)"""

    strings = {"name": "AutoVoiceTTS"}

    def install_dependencies(self):
        """Автоматическая установка зависимостей (eSpeak и pyttsx3)"""
        try:
            subprocess.check_call(["which", "espeak"])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call(["pkg", "install", "espeak", "-y"])
            except Exception as e:
                raise RuntimeError(f"Ошибка установки eSpeak: {e}")

        try:
            subprocess.check_call(["pip", "show", "pyttsx3"])
        except subprocess.CalledProcessError:
            try:
                subprocess.check_call(["pip", "install", "pyttsx3"])
            except Exception as e:
                raise RuntimeError(f"Ошибка установки pyttsx3: {e}")

    async def ocmd(self, message: Message):
        args = utils.get_args_raw(message)
        if not args:
            await message.edit("❌ Введите текст для озвучки!")
            return

        try:
            self.install_dependencies()
        except Exception as e:
            await message.edit(f"❌ Ошибка установки зависимостей: {str(e)}")
            return

        words = args.split(" ", 1)

        if words[0].lower() == "м":
            voice = "male"
            text = words[1] if len(words) > 1 else "Ошибка: нет текста"
        elif words[0].lower() == "ж":
            voice = "female"
            text = words[1] if len(words) > 1 else "Ошибка: нет текста"
        else:
            voice = "female"
            text = args

        await message.edit(f"🎙 Озвучиваю текст ({'Мужской' if voice == 'male' else 'Женский'} голос)...")

        try:
            audio_fp = io.BytesIO()

            engine = pyttsx3.init()
            voices = engine.getProperty("voices")

            if voice == "male":
                engine.setProperty("voice", voices[0].id)
            else:
                engine.setProperty("voice", voices[1].id)

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
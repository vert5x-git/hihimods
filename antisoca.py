# meta developer: @usershprot
# meta name: DeezerFullTrack
# meta version: 1.1

from .. import loader, utils
import requests
import io
from PIL import Image

class DeezerFullTrackMod(loader.Module):
    """Отправка полного трека с обложкой и описанием"""
    strings = {"name": "DeezerFullTrack"}

    async def sfindcmd(self, message):
        """▫️ .sfind <название> — Найти и отправить трек с обложкой"""
        query = utils.get_args_raw(message)
        if not query:
            return await message.edit("Укажи название трека.")

        # 1. Ищем трек в Deezer
        res = requests.get(f"https://api.deezer.com/search?q={query}").json()
        if not res.get("data"):
            return await message.edit("Ничего не найдено.")

        track = res["data"][0]

        title = track['title']
        artist = track['artist']['name']
        cover_url = track['album']['cover_big']

        # 2. Получаем обложку
        cover = requests.get(cover_url).content
        img = io.BytesIO(cover)
        img.name = "cover.jpg"

        # 3. Получаем mp3-файл из внешнего источника
        search_query = f"{artist} - {title}"
        await message.edit(f"🔎 Ищу трек: <b>{search_query}</b>...", parse_mode="html")

        try:
            # Используем встроенного Telegram-бота через inline
            result = await message.client.inline_query("@ddownloaderbot", search_query)
            result = [r for r in result if r.type == "audio"]
            if not result:
                return await message.edit("Не удалось найти полный трек.")
            
            await result[0].click(message.chat_id)

            # Отправляем описание после
            caption = f"<b>{title}</b>\n<code>{artist}</code>"
            await message.client.send_file(
                message.chat_id,
                img,
                caption=caption,
                parse_mode="html"
            )

            await message.delete()

        except Exception as e:
            return await message.edit(f"Ошибка: {e}")
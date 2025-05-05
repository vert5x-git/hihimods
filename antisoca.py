# meta developer: @usershprot
# meta name: DeezerFullTrack
# meta version: 1.2

from .. import loader, utils
import yt_dlp as ytdl
import requests
import io
import os

class DeezerFullTrackMod(loader.Module):
    strings = {"name": "DeezerFullTrack"}

    async def sfindcmd(self, message):
        query = utils.get_args_raw(message)
        if not query:
            return await message.edit("Укажи название трека.")

        res = requests.get(f"https://api.deezer.com/search?q={query}").json()
        if not res.get("data"):
            return await message.edit("Ничего не найдено.")

        track = res["data"][0]
        title = track['title']
        artist = track['artist']['name']
        cover_url = track['album']['cover_big']
        cover = requests.get(cover_url).content
        img = io.BytesIO(cover)
        img.name = "cover.jpg"

        search_query = f"{artist} - {title}"
        await message.edit(f"🔎 Ищу трек: <b>{search_query}</b>...", parse_mode="html")

        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(title)s.%(ext)s',
                'noplaylist': True,
                'quiet': True,
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }

            with ytdl.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{search_query}", download=True)
                filename = ydl.prepare_filename(info['entries'][0]).replace(".webm", ".mp3").replace(".m4a", ".mp3")

            await message.client.send_file(
                message.chat_id,
                filename,
                caption=f"<b>{title}</b>\n<code>{artist}</code>",
                voice=False,
                parse_mode="html",
                thumb=img
            )

            os.remove(filename)
            await message.delete()

        except Exception as e:
            await message.edit(f"Ошибка: {e}")
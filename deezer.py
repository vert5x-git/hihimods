# meta developer: @usershprot
# meta name: DeezerPlayer
# meta version: 1.0

from .. import loader, utils
import requests

class DeezerPlayerMod(loader.Module):
    """Проигрыватель треков через Deezer API"""
    strings = {
        "name": "DeezerPlayer"
    }

    _auth_token = None
    _current_track = None

    async def sauthcmd(self, message):
        """▫️ .sauth — Первый этап аутентификации (заглушка)"""
        self._auth_token = "fake_token"
        await message.edit("Авторизация начата. Введите код: `.scode 123456`")

    async def scodecmd(self, message):
        """▫️ .scode <код> — Второй этап аутентификации (заглушка)"""
        code = utils.get_args_raw(message)
        if self._auth_token:
            self._auth_token = f"verified_token_{code}"
            await message.edit("Успешно авторизован в Deezer!")
        else:
            await message.edit("Сначала используйте `.sauth`.")

    async def unauthcmd(self, message):
        """▫️ .unauth — Отменить аутентификацию"""
        self._auth_token = None
        self._current_track = None
        await message.edit("Вы вышли из Deezer.")

    async def sfindcmd(self, message):
        """▫️ .sfind <название> — Найти трек по названию"""
        if not self._auth_token:
            return await message.edit("Сначала авторизуйтесь с помощью `.sauth`.")

        query = utils.get_args_raw(message)
        if not query:
            return await message.edit("Введите название трека.")

        res = requests.get(f"https://api.deezer.com/search?q={query}").json()
        if not res.get("data"):
            return await message.edit("Ничего не найдено.")

        track = res["data"][0]
        self._current_track = track

        text = (
            f"▶️ <b>{track['title']}</b>\n"
            f"🎤 <i>{track['artist']['name']}</i>\n"
            f"💽 <code>{track['album']['title']}</code>\n"
            f"⏱ {track['duration']} сек\n"
            f"<a href='{track['preview']}'>Слушать превью</a>"
        )
        await message.edit(text, parse_mode="html", link_preview=True)

    async def snowcmd(self, message):
        """▫️ .snow — Показать текущий трек"""
        if not self._current_track:
            return await message.edit("Нет текущего трека.")
        track = self._current_track
        text = (
            f"▶️ <b>{track['title']}</b>\n"
            f"🎤 <i>{track['artist']['name']}</i>\n"
            f"💽 <code>{track['album']['title']}</code>\n"
            f"<a href='{track['preview']}'>Слушать превью</a>"
        )
        await message.edit(text, parse_mode="html", link_preview=True)

    async def splaycmd(self, message):
        """▫️ .splay — Проиграть текущий трек (превью)"""
        if not self._current_track:
            return await message.edit("Нет трека для проигрывания.")
        await message.edit("Отправка превью...")
        await message.client.send_file(
            message.chat_id,
            self._current_track["preview"],
            voice=True,
            caption=f"{self._current_track['title']} — {self._current_track['artist']['name']}"
        )
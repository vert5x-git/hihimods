# meta developer: @hihimods
# meta name: PingX
# meta description: Проверка пинга и аптайма с настраиваемым шаблоном

from .. import loader, utils
import time
import datetime

@loader.tds
class PingXMod(loader.Module):
    """Модуль для кастомного .ping с поддержкой шаблонов"""
    strings = {
        "name": "PingX",
        "default_template": (
            "⚡ <b>Ping:</b> <code>{ping}ms</code>\n"
            "⏱ <b>Uptime:</b> <code>{uptime}</code>\n"
            "👤 <b>User:</b> <code>{user}</code>\n"
            "📅 <b>Date:</b> <code>{date}</code>\n"
            "🦊 <b>Bot:</b> <code>{botver}</code>"
        ),
        "default_loading": "⏳ Пинг...",
    }

    def __init__(self):
        self._start_time = time.time()
        self.config = loader.ModuleConfig(
            {
                "template": self.strings["default_template"],
                "loading_text": self.strings["default_loading"],
            },
            self
        )

    async def pinxcmd(self, message):
        """Показывает кастомный пинг с аптаймом и переменными"""
        start = time.time()
        loading = self.config["loading_text"]
        m = await message.edit(loading)

        ping = round((time.time() - start) * 1000)
        uptime = str(datetime.timedelta(seconds=int(time.time() - self._start_time)))
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        me = await message.client.get_me()
        user = me.first_name or "Unknown"
        username = f"@{me.username}" if me.username else "No username"
        botver = utils.get_bot_version()

        template = self.config["template"]

        try:
            result = template.format(
                ping=ping,
                uptime=uptime,
                user=user,
                username=username,
                date=date,
                botver=botver
            )
        except Exception as e:
            result = f"❌ Ошибка в шаблоне: <code>{e}</code>"

        if result == m.raw_text:
            result += "\u2060"

        await m.edit(result)
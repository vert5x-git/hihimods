# meta developer: @Vert5x
# meta name: PingX
# meta description: Проверка пинга и аптайма с фиксированным выводом

from .. import loader
import time
import datetime

@loader.tds
class PingXMod(loader.Module):
    strings = {"name": "PingX"}

    def __init__(self):
        self._start_time = time.time()

    async def pinxcmd(self, message):
        start = time.time()
        m = await message.edit("⏳ Пинг...")
        ping = round((time.time() - start) * 1000)
        uptime = str(datetime.timedelta(seconds=int(time.time() - self._start_time)))

        me = await message.client.get_me()
        owner_block = f'<blockquote><a href="https://t.me/{me.username}">{me.first_name}</a></blockquote>'

        text = (
            f"{owner_block}\n"
            "<blockquote>🌩️ <b><i>𝚜𝚢𝚗𝚝𝚑𝚎𝚝𝚒𝚌 𝚛𝚎𝚏𝚕𝚎𝚌𝚝𝚒𝚘𝚗:</i></b> <code>{ping}</code> 𝚖𝚜</blockquote>\n"
            "<blockquote>🧿 <b><i>𝚘𝚙𝚎𝚗 𝚎𝚢𝚎 𝚊𝚌𝚝𝚒𝚟𝚎 𝚜𝚒𝚗𝚌𝚎:</i></b> <code>{uptime}</code></blockquote>\n"
            "<blockquote>🌌 <b><i>𝚕𝚒𝚗𝚔 𝚝𝚘 𝚖𝚊𝚝𝚛𝚒𝚡 𝚌𝚘𝚗𝚏𝚒𝚛𝚖𝚎𝚍.</i></b></blockquote>"
        ).format(ping=ping, uptime=uptime)

        await m.edit(text)
from hikka import loader, utils

class CommandAliases(loader.Module):
    """Позволяет использовать сокращённые команды"""
    strings = {"name": "CommandAliases"}

    def __init__(self):
        self.config = loader.ModuleConfig(
            "ALIASES", {}  # Если алиасы отсутствуют, создаём пустой словарь
        )

    async def client_ready(self, client, db):
        self.aliases = self.config.get("ALIASES", {})  # Загружаем алиасы

    async def aliascmd(self, message):
        """Добавить алиас: .alias <команда> <алиас>"""
        args = utils.get_args_raw(message)
        if not args or len(args.split()) != 2:
            return await utils.answer(message, "Использование: .alias <команда> <алиас>")

        cmd, alias = args.split()
        if alias in self.aliases:
            return await utils.answer(message, f"Алиас `{alias}` уже существует!")

        self.aliases[alias] = cmd
        self.config["ALIASES"] = self.aliases  # Сохраняем в конфиг
        await utils.answer(message, f"Алиас `{alias}` теперь вызывает `{cmd}`")

    async def unaliascmd(self, message):
        """Удалить алиас: .unalias <алиас>"""
        args = utils.get_args_raw(message)
        if not args or args not in self.aliases:
            return await utils.answer(message, "Алиас не найден")

        del self.aliases[args]
        self.config["ALIASES"] = self.aliases
        await utils.answer(message, f"Алиас `{args}` удалён")

    async def watcher(self, message):
        """Перехватывает команды и заменяет алиасы"""
        if not message.text or not message.text.startswith("."):
            return

        cmd = message.text[1:].split()[0]  # Получаем команду без точки
        if cmd in self.aliases:
            new_text = "." + self.aliases[cmd] + message.text[len(cmd) + 1 :]
            await message.edit(new_text)  # Заменяем команду и повторно отправляем
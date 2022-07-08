import discord
from discord.ext import commands


class MessageManager:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.defaults = "defaults"

    def format_message(self, ctx: commands.Context, message: str, kwargs: dict) -> str:
        if not ("{" in message and "}" in message):
            return message
        def add(el, value):
            if el not in kwargs: kwargs[el] = value
        if ctx:
            add("message", ctx.message)
            add("user_name", ctx.author.display_name)
            add("user_mention", ctx.author.mention)
        return message.format(**kwargs)

    def get_message(self, func: str, msg_name: str) -> str:
        messages = self.bot.ConfigManager['messages']
        if func in messages  and  msg_name in messages[func]:
            return messages[func][msg_name]
        if msg_name in messages[self.defaults]:
            return messages[self.defaults][msg_name]
        self.bot.LogManager.print(f"MessageManager get_message could not get message '{msg_name}' for func '{func}'!")
        return ""

    def get_embed(self, func: str, embed_name: str) -> discord.Embed:
        data = self.get_message(func, embed_name)
        for el in ["color", "colour"]:
            if el in data and isinstance(data[el], list): data[el] = discord.Colour.from_rgb(*data[el])
        return discord.Embed(**data)

    async def send(self, _channel: discord.TextChannel, _func: str, _msg_name: str, _reserve_msg:str=None, **kwargs):
        try:
            message = self.get_message(_func, _msg_name)
            if not message:
                if _reserve_msg:
                    message = _reserve_msg
                else:
                    raise Exception("couldn't find the message!")

            ctx = False
            if isinstance(_channel, commands.Context): ctx = _channel

            if isinstance(message, list):
                colour, message = message
                color = discord.Color.from_rgb(*colour)
                message = self.format_message(ctx, message, kwargs)
                message = discord.Embed(description=message, color=color)
                await _channel.send(embed=message)
            else:
                message = self.format_message(ctx, message, kwargs)
                await _channel.send(message)

        except Exception as exc:
            self.bot.LogManager.print(f"MessageManager.send() failed to send message '{_msg_name}' for function '{_func}': {exc}")



def setup(bot):
    bot.ConfigManager.load("messages", "configs\\messages.json")
    bot.MessageManager = MessageManager(bot)
    bot.LogManager.print("MessageManager has been appended!")

def teardown(bot):
    bot.LogManager.print("MessageManager has been suspended!")

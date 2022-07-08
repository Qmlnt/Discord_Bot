import time
from discord.ext import commands


class LogManager:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.delay_time = 1
        self.last_time = 0
        self.start_time = time.ctime()
        if hasattr(bot, "LogManager"):
            self.start_time = bot.LogManager.start_time

    def print(self, content, **kwargs):
        print(content, **kwargs)
        self.log(content)

    def log(self, content: str):
        timestamp = time.time()
        try:
            path = f"logs\\{self.start_time}.txt".replace(':', '-')
            with open(path, "a+", encoding="utf-8") as file:
                if timestamp-self.last_time > self.delay_time:
                    self.last_time = timestamp
                    file.write(f"\n{time.ctime(timestamp)} ({timestamp})\n")
                file.write(str(content)+"\n")
        except Exception as exc:
            print(f"LogManager.log() couldn't log '{content}': {exc}")



def setup(bot):
    bot.LogManager = LogManager(bot)
    bot.LogManager.print("LogManager has been appended!")

def teardown(bot):
    bot.LogManager.print("LogManager has been suspended!")
import json
from discord.ext import commands


class ConfigManager:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.configs = {}   # name: [path, config]
        if hasattr(bot, "old_configs"):
            self.configs = bot.old_configs
            self.bot.LogManager.print(f"ConfigManager will restore: {list(self.configs.keys())}")
            self.refresh_all()


    def __delitem__(self, item):
        del self.configs[item]

    def __getitem__(self, item: str):
        return self.get(item)

    
    def load(self, name: str, path):
        with open(path, 'r', encoding="utf-8") as file:
            config = json.load(file)
        self.configs[name] = [path, config]
    
    def refresh(self, name: str):
        self.load(name, self.configs[name][0])
    
    def refresh_all(self):
        for cfg in self.configs:
            self.refresh(cfg)

    
    def save(self, name: str, force:bool=False):
        if not ("do_not_rewrite" in self.configs[name][1]) or force:
            with open(self.configs[name][0], "w", encoding="utf-8") as file:
                json.dump(self.configs[name][1], file, indent=1)
        else:
            self.bot.LogManager.print(f"Config '{name}' wasn't saved, it has do_not_rewrite attribute.")
    
    def save_all(self):
        for cfg in self.configs:
            self.save(cfg)

    
    def get(self, name: str) -> dict:
        if name in self.configs:
            return self.configs[name][1]
        return False

    
    def rollback(self, name: str):
        if hasattr(self.bot, "old_configs"):
            if (name in self.bot.old_configs) and (name in self.configs):
                self.configs[name][1] = self.bot.old_configs[name][1]
    
    def rollback_all(self):
        if hasattr(self.bot, "old_configs"):
            for cfg in self.configs:
                self.rollback(cfg)



def setup(bot):
    bot.ConfigManager = ConfigManager(bot)
    bot.LogManager.print("ConfigManager has been appended!")

def teardown(bot):
    bot.ConfigManager.save_all()
    bot.old_configs = bot.ConfigManager.configs
    bot.LogManager.print("ConfigManager has been suspended!")

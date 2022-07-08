from discord.ext import commands


class RoleManager:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.default = 3

    def validate_func(self, fname: str):
        if fname not in self.bot.ConfigManager["func_roles"]:
            self.bot.ConfigManager["func_roles"][fname] = 0
            self.bot.ConfigManager.save("func_roles", True)

    def validate_user(self, user: str):
        if user not in self.bot.ConfigManager["user_roles"]:
            self.bot.ConfigManager["user_roles"][user] = self.default
            self.bot.ConfigManager.save("user_roles", True)


    def check(self, fname: str, uid: int) -> bool:
        try:
            self.validate_func(fname)
            if uid not in self.bot.develoopers:
                self.validate_user(str(uid))
                if self.bot.ConfigManager["func_roles"][fname] < self.bot.ConfigManager["user_roles"][str(uid)]:
                    return False
            return True
        except Exception as exc:
            self.bot.LogManager.print(f"RolesManager.check() raised an exception for '{fname}': {exc}")
            self.bot.LogManager.print(f"Using develooper list to check roles: {self.bot.develoopers}")
            if uid in self.bot.develoopers: return True
            return False



def setup(bot):
    bot.ConfigManager.load("user_roles", "configs\\user_roles.json")
    bot.ConfigManager.load("func_roles", "configs\\func_roles.json")
    bot.RoleManager = RoleManager(bot)
    bot.LogManager.print("RoleManager has been appended!")

def teardown(bot):
    # bot.ConfigManager.save("user_roles")
    # bot.ConfigManager.save("func_roles")
    bot.LogManager.print("RoleManager has been suspended!")

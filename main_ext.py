import discord
from discord.ext import commands
from utils.wrappers import use_roles


class Main(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        if not hasattr(bot, "banned_functions"):
            bot.banned_functions = {}
        bot.check_banned = self.check_banned

    def check_banned(self) -> str:
        status = ""
        for comm in list(self.bot.all_commands.keys()):
            if comm in self.bot.banned_functions:
                self.bot.banned_functions[comm] = self.bot.all_commands.pop(comm)
                status += f"Banned '{comm}' command from {self.bot.banned_functions[comm].cog.qualified_name}.\n"
        return status

    @commands.command()
    @use_roles
    async def function(self, ctx: commands.Context, name:str=None):
        """Ban/restore a command or show banned commands."""
        if name is None:
            banned = list(self.bot.banned_functions.keys())
            self.bot.LogManager.print(f"Commands banned -> {banned}")
    
            if not banned: await ctx.send("Nothing is banned.")
            else: await ctx.send("Banned:\n" + '\n'.join(banned))
            return
        try:
            if name in self.bot.all_commands:
                status = "Baned command"
                self.bot.banned_functions[name] = self.bot.all_commands.pop(name)
            elif name in self.bot.banned_functions:
                status = "Restored command"
                self.bot.all_commands[name] = self.bot.banned_functions.pop(name)
            else:
                status = "Can't find"

            self.bot.LogManager.print(f"Function command -> {status} '{name}'")
            await ctx.send(f"{status} '{name}'")
        except Exception as exc:
            self.bot.LogManager.print(f"Exception in 'function' func: {exc}")
            await ctx.send("Failed!")


    @commands.command()
    @use_roles
    async def extensions(self, ctx: commands.Context):
        """List all bot extenisons."""
        loaded = list(self.bot.extensions.keys())
        self.bot.LogManager.print(f"Extensions command -> {loaded}")
        await ctx.send('\n'.join(loaded))

    @commands.command()
    @use_roles
    async def extension(self, ctx: commands.Context, name:str=None, reload:None=None):
        """Load/Unload/Reload an extension."""
        if name is None: await self.extensions(ctx); return
        try:
            if name in self.bot.extensions:
                if reload: 
                    status = "Reloaded"
                    self.bot.reload_extension(name)
                else:
                    status = "Unloaded"
                    self.bot.unload_extension(name)
            else:
                status = "Loaded"
                self.bot.load_extension(name)

            status = self.check_banned() + status

            await ctx.send(f"{status} '{name}'")
        except Exception as exc:
            self.bot.LogManager.print(f"Exception in 'extension' func: {exc}")
            await ctx.send("Failed!")



def setup(bot: commands.Bot):
    to_load = ["utils.LogManager", "utils.ConfigManager", "utils.RoleManager", "utils.MessageManager",
               "extensions.listeners", "extensions.callables", "extensions.test"]
    for ext in to_load:
        if ext not in bot.extensions:
            bot.load_extension(ext)

    bot.add_cog(Main(bot))

    try:
        for func in bot.all_commands:
            bot.RoleManager.validate_func(func)

        banned = bot.check_banned()
        if not banned: bot.LogManager.print("Nothing was banned")
        else: bot.LogManager.print(banned)
        
        bot.LogManager.print("Main extension has been appended!\n")

    except Exception as exc:
        bot.LogManager.print(f"MAIN EXTENSION HAS FAILED TO APPEND FULLY\n{exc}")
        if input("Continue anyway? no -> shutdown Y/n: ").lower() not in ["no", "n"]:
            bot.LogManager.print("Main extension was force loaded.")
        else:
            bot.LogManager.print("FORCE UNLOAD")
            for ext in list(bot.extensions.keys()):
                bot.unload_extension(ext)

def teardown(bot):
    bot.LogManager.print("Main extension has been suspended!")
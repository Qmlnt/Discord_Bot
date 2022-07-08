from discord.ext import commands
from utils.wrappers import use_roles

class Test(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command()
    @use_roles
    async def hello(self, ctx: commands.Context):
        """Say hello."""
        await ctx.reply("Hello")

    

def setup(bot):
    bot.add_cog(Test(bot))
    bot.LogManager.print("Test was loaded!")

def teardown(bot):
    bot.LogManager.print("Test was unloaded!")
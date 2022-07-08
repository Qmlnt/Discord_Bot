import discord
from discord.ext import commands

class Listeners(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error):
        self.bot.LogManager.print(error)
        if isinstance(error, commands.errors.CommandNotFound):
            await self.bot.MessageManager.send(ctx, "ListenersExt", "no_command")
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            await self.bot.MessageManager.send(ctx, "ListenersExt", "missing_arg")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        await self.bot.MessageManager.send(member.guild.system_channel,
        "ListenersExt", "member_join", user_mention=member.mention)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        await self.bot.MessageManager.send(member.guild.system_channel,
        "ListenersExt", "member_remove", user_mention=member.mention)



def setup(bot: commands.Bot):
    bot.add_cog(Listeners(bot))
    bot.LogManager.print("Listeners were loaded!")

def teardown(bot):
    bot.LogManager.print("Listeners were unloaded!")
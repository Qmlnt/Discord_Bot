import functools
from discord.ext import commands


annotations = {}

def use_roles(func):
    annotations[func.__name__] = func.__annotations__
    @functools.wraps(func)
    async def wrapper(self, ctx: commands.Context, *args, **kwargs):
        if self.bot.RoleManager.check(func.__name__, ctx.author.id):
            return await func(self, ctx, *args, **kwargs)
        await self.bot.MessageManager.send(ctx, func.__name__, "no_rights")
    return wrapper

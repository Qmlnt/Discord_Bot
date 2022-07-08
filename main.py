# 28/05/2022 - birthday date of the bot.
# I have been writing this bot for a long period of time,
# so there can be small mistakes somewhere or unnecessary things.

import discord
import functools
from discord.ext import commands


def get_prefix(bot, message):
    if message.guild or message.author.id in bot.develoopers:
        return commands.when_mentioned_or('~')(bot, message)
    print(f"DM from {message.author.name}#{message.author.discriminator} ({message.author.id})")
    return "Wanna dance?"

discord.member = True
bot = commands.Bot(intents=discord.Intents.all(), command_prefix=get_prefix, strip_after_prefix=True,
    activity = discord.Activity(type=discord.ActivityType.watching, name='the server.'), status=discord.Status.idle)
bot.remove_command("help")
def update_devs():
    try:
        with open("configs\\DEVELOOPERS") as file:
            devs = list(map(int, file.read().split(' ')))
        bot.develoopers = devs
        print(f"\nDEVELOOPERS: {bot.develoopers}\n")
    except Exception as exc:
        print(f"\nATTENTION!\nFailed to update develoopers!\n{exc}")
bot.develoopers = []
update_devs()
bot.update_devs = update_devs
bot.main_ext = "main_ext"
bot.load_extension(bot.main_ext)



@bot.event
async def on_ready(): print("\nReady!", bot.user)

def for_develoopers(func):
    @functools.wraps(func)
    async def wrapper(ctx: commands.Context, *args, **kwargs):
        if not bot.develoopers:
            bot.develoopers.append(int(input("\nATTENTION! DEVELOOPER LIST IS EMPTY\nenter develooper id: ")))
        if ctx.author.id in bot.develoopers:
            return await func(ctx, *args, **kwargs)
        await ctx.send(embed=discord.Embed(title="Who are you, to tell me!? 🔪🩸",
            color=discord.Colour.from_rgb(255,0,0)))
    return wrapper

@bot.command()
@for_develoopers
async def reload_devs(ctx: commands.Context):
    """Reload develoopers list."""
    update_devs()
    await ctx.send("Reloaded.")

@bot.command()
@for_develoopers
async def main_ext(ctx: commands.Context, reload=None):
    """Manage main extension."""
    try:
        if bot.main_ext in bot.extensions:
            if reload: bot.reload_extension(bot.main_ext); st="Reloaded"
            else: bot.unload_extension(bot.main_ext); st="Unloaded"
        else:
            bot.load_extension(bot.main_ext); st="Loaded"
        await ctx.send(f"{st} {bot.main_ext}.")
    except Exception as exc:
        print(f"\n{exc}\n")
        await ctx.send("Failed!")

@bot.command()
@for_develoopers
async def shutdown(ctx: commands.Context, reload=None):
    """Unload all extensions, reload or even shut down."""
    if reload == "die":
        await ctx.send("☠")
        await bot.change_presence(status=discord.Status.invisible)
        exit()

    exts = list(bot.extensions.keys())
    print("\nUnloading:", exts)
    for ext in exts:
        bot.unload_extension(ext)
        print("Left:", list(bot.extensions.keys()))
    print("\nUNLOADED!")
    await ctx.send("Shutted down.")

    if reload: await main_ext(ctx)


with open("configs\\TOKEN") as file:
    token = file.read()
bot.run(token)

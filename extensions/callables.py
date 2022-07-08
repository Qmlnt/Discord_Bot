import typing
import asyncio
import discord
from discord.ext import commands
from utils.wrappers import use_roles, annotations


class Callables(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot


    @commands.command()
    @use_roles
    async def move_messages(self, ctx: commands.Context, from_channel: discord.TextChannel, to_channel: discord.TextChannel, amount: int, ignore_members: commands.Greedy[discord.Member]):
        """Move messages from one channel to anther."""
        ignore_members = [author.id for author in ignore_members]
        messages: list[discord.Message] = await from_channel.history(limit=amount).flatten()
        messages.reverse()
        for msg in messages:
            if msg.author.id in ignore_members: continue
            author = f"{msg.author.display_name}#{msg.author.discriminator}"
            time = msg.created_at.ctime()
            message = msg.content
            done = ""
            if msg.reference:
                try:
                    r: discord.Message = await from_channel.fetch_message(msg.reference.message_id)
                    done = f"*Replyed to {r.author.display_name}#{r.author.discriminator}* \"`{r.content}`\":\n"
                except discord.NotFound:
                    done = f"Replyed to `can't find the initial message`:\n"

            content = f"*{author}*    {time}\n{done}> {message}\n.........."
            await to_channel.send(content)
            await asyncio.sleep(0.5)

    @commands.command()
    @use_roles
    async def clear(self, ctx: commands.Context, amount: int = 10, check: typing.Union[discord.Member, str] = None):
        """Clear the channel messages."""

        if not check:
            ch = None
        elif isinstance(check, discord.Member):
            ch = lambda m: m.author.id == check.id
        elif isinstance(check, str):
            ch = lambda m: m.content == check
        else:
            raise Exception(f"Unknown check type in clear command: {type(check)}")

        await ctx.channel.purge(limit=amount+1, check=ch)
        await self.bot.MessageManager.send(ctx, "clear", "done")


    @commands.command()
    @use_roles
    async def h(self, ctx:commands.Context, command_name:str):
        "Help for a command."
        command = self.bot.get_command(command_name)
        if not command:
            await self.bot.MessageManager.send(ctx, "h", "no_command", command=command_name)
            return
        if command.name not in annotations:
            await self.bot.MessageManager.send(ctx, "h", "not_in_annot", name=command.name, doc=command.help)
            return

        try:
            message = f"~{command.name}"
            for el in annotations[command.name]:
                if el == "ctx": continue
                el_type = str(annotations[command.name][el]).replace('class ', '').replace("'", '')
                message += f"  **{el}**: *{el_type}*"
            if command.name in self.bot.ConfigManager["func_roles"]:
                message += f"\nRole lvl: *{self.bot.ConfigManager['func_roles'][command.name]}*"
            else: message+= "\nRole lvl: *unknown*"
            message += f"\n`{command.help}`"
        except:
            message = self.bot.MessageManager.get_message("h", "fail")

        await ctx.send(message)

    @commands.command()
    @use_roles
    async def help(self, ctx: commands.Context, command:str=None):
        """Help for all of the commands."""
        if command: await self.h(ctx, command); return
        roles: dict = self.bot.ConfigManager["func_roles"]
        output = {}; longest = 0
        for func in roles:
            if type(roles[func]) is not int: continue
            if func not in self.bot.all_commands: continue
            if len(func) > longest: longest = len(func)
            if roles[func] not in output: output[roles[func]] = {}
            doc = self.bot.all_commands[func].help
            if doc is None: doc = self.bot.MessageManager.get_message("help", "no_doc")
            output[roles[func]][func] = doc

        message: discord.Embed = self.bot.MessageManager.get_embed("help", "embed")
        for role in set(output):
            value = ""
            for comm in output[role]:
                value += f"**`{comm}`** {'..'*(longest-len(comm)+4)} {output[role][comm]}\n"
            message.add_field(name=f"Level {role}", value=value, inline=False)
        message.add_field(name="Info", value=self.bot.MessageManager.get_message("help", "info")+"\nAuthor: Qmelint", inline=False)
        await ctx.send(embed=message)


    @commands.command()
    @use_roles
    async def configs(self, ctx: commands.Context):
        """List all conifig files."""
        configs = list(self.bot.ConfigManager.configs.keys())
        self.bot.LogManager.print(f"Configs command -> {configs}")
        await ctx.send('\n'.join(configs))

    @commands.command()
    @use_roles
    async def config(self, ctx: commands.Context, name:str=None, path:str=None):
        """Add/delete/refresh config."""
        if name is None: await self.configs(ctx); return
        try:
            if path and path.endswith(".json"):
                status = "Loaded"
                self.bot.ConfigManager.load(name, path)

            elif self.bot.ConfigManager[name]:
                if path:
                    status = "Refreshed"
                    self.bot.ConfigManager.refresh(name)
                else:
                    status = "Deleted"
                    del self.bot.ConfigManager[name]
            else: status = "Need a path to load"

            await ctx.send(f"{status} '{name}'.")
        except Exception as exc:
            self.bot.LogManager.print(f"Exception in 'conifg' func: {exc}")
            await ctx.send("Failed!")

    @commands.command()
    @use_roles
    async def user_roles(self, ctx: commands.Context):
        """List all users by their role value."""
        roles: dict = self.bot.ConfigManager["user_roles"]
        output = {}
        for user in roles:
            if type(roles[user]) is not int: continue
            if roles[user] not in output: output[roles[user]] = ""
            output[roles[user]] += f"<@{user}>\n"
        message = self.bot.MessageManager.get_embed("user_roles", "embed")
        for el in set(output.keys()):
            message.add_field(name=f"Level {el}", value=output[el])
        await ctx.send(embed=message)

    @commands.command()
    @use_roles
    async def functions(self, ctx: commands.Context):
        """List all functions by their role value."""
        roles: dict = self.bot.ConfigManager["func_roles"]
        output = {}
        for func in roles:
            if type(roles[func]) is not int: continue
            if func not in self.bot.all_commands:
                if "not usable" not in output: output["not usable"] = ""
                output["not usable"]+=func+"\n"; continue
            if roles[func] not in output: output[roles[func]] = ""
            output[roles[func]] += func+"\n"
        message = self.bot.MessageManager.get_embed("functions", "embed")
        for el in set(output.keys()):
            message.add_field(name=f"Level {el}", value=output[el])
        await ctx.send(embed=message)


    @commands.command()
    @use_roles
    async def user_role(self, ctx: commands.Context, member: discord.Member, value: int):
        """Change role value of the user."""
        if value < 1: value = 1

        member_id = str(member.id)
        self.bot.RoleManager.validate_user(member_id)
        member_role = self.bot.ConfigManager["user_roles"][member_id]

        if member_role == value:
            await self.bot.MessageManager.send(ctx, "user_role", "no_need", member=member.mention, value=value)
            return

        author_id = ctx.author.id
        self.bot.RoleManager.validate_user(str(author_id))
        author_role = self.bot.ConfigManager["user_roles"][str(author_id)]

        if (author_id in self.bot.develoopers) or (author_role < member_role and author_role < value):
            self.bot.ConfigManager["user_roles"][member_id] = value
            self.bot.ConfigManager.save("user_roles", True)
            await self.bot.MessageManager.send(ctx, "user_role", "done", member_mention=member.mention, value=value)
        else:
            await self.bot.MessageManager.send(ctx, "user_role", "can't", author=author_role, member=member_role, value=value)

    @commands.command()
    @use_roles
    async def func_role(self, ctx: commands.Context, func: str, value: int):
        """Change role value of the function."""
        if value < 0: value = 0

        if func not in self.bot.ConfigManager["func_roles"]:
            await self.bot.MessageManager.send(ctx, "func_role", "no_function", function=func)
            return
        func_role = self.bot.ConfigManager["func_roles"][func]

        if func_role == value:
            await self.bot.MessageManager.send(ctx, "func_role", "no_need", function=func, value=value)
            return

        author_id = ctx.author.id
        self.bot.RoleManager.validate_user(str(author_id))
        author_role = self.bot.ConfigManager["user_roles"][str(author_id)]

        if (author_id in self.bot.develoopers) or (author_role <= func_role and author_role <= value):
            self.bot.ConfigManager["func_roles"][func] = value
            self.bot.ConfigManager.save("func_roles", True)
            await self.bot.MessageManager.send(ctx, "func_role", "done", function=func, value=value)
        else:
            await self.bot.MessageManager.send(ctx, "func_role", "can't", author=author_role, function=func_role, value=value)



def setup(bot):
    bot.add_cog(Callables(bot))
    bot.LogManager.print("Callables were loaded!")

def teardown(bot):
    bot.LogManager.print("Callables were unloaded!")
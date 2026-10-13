import discord
from discord import app_commands
from discord.ext import commands

import embeds


class Send(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="send", description="Send a message as the bot")
    @app_commands.describe(
        message_type="Type of message to send",
        content="What you want the bot to send (use \\n for new lines)",
        channel="Where to send it",
        color="Hex color for embed, e.g. #ffc0cb",
    )
    @app_commands.choices(message_type=[
        app_commands.Choice(name="raw text", value="raw"),
        app_commands.Choice(name="embed", value="embed"),
        app_commands.Choice(name="containered", value="container"),
    ])
    @app_commands.checks.has_permissions(manage_messages=True)
    async def send(self, interaction: discord.Interaction, message_type: app_commands.Choice[str],
                   content: str, channel: discord.TextChannel = None, color: str = None):
        target = channel or interaction.channel
        perms = target.permissions_for(interaction.guild.me)
        if not (perms.send_messages and perms.view_channel):
            return await interaction.response.send_message(f"I can't send in {target.mention}", ephemeral=True)

        text = content.replace("\\n", "\n")
        accent = embeds.ACCENT
        if color:
            try:
                accent = discord.Color(int(color.lstrip("#"), 16))
            except ValueError:
                return await interaction.response.send_message("Invalid hex color", ephemeral=True)

        if message_type.value == "raw":
            await target.send(text)
        elif message_type.value == "embed":
            await target.send(embed=discord.Embed(description=text, color=accent))
        else:
            view = discord.ui.LayoutView()
            view.add_item(discord.ui.Container(discord.ui.TextDisplay(text)))
            await target.send(view=view)

        await interaction.response.send_message(f"Sent in {target.mention}", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Send(bot))
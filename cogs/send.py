import json
import os
import discord
from discord import app_commands
from discord.ext import commands

PATH = "data/sticky.json"


class Sticky(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = {}
        self.locks = {}
        if os.path.exists(PATH):
            with open(PATH) as f:
                self.data = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(PATH), exist_ok=True)
        with open(PATH, "w") as f:
            json.dump(self.data, f)

    def embed(self, content):
        return discord.Embed(description=content, color=discord.Color.blurple()).set_footer(text="sticky note")

    @app_commands.command(name="stick", description="Pin a sticky note to the bottom of a channel")
    @app_commands.describe(content="What the sticky note says", channel="Where to stick it")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def stick(self, interaction: discord.Interaction, content: str, channel: discord.TextChannel = None):
        target = channel or interaction.channel
        perms = target.permissions_for(interaction.guild.me)
        if not (perms.send_messages and perms.view_channel):
            return await interaction.response.send_message(f"I can't send in {target.mention}", ephemeral=True)
        old = self.data.get(str(target.id))
        if old:
            try:
                msg = await target.fetch_message(old["message_id"])
                await msg.delete()
            except discord.HTTPException:
                pass
        sent = await target.send(embed=self.embed(content))
        self.data[str(target.id)] = {"content": content, "message_id": sent.id}
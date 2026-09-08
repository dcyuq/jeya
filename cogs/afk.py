import discord
from discord import app_commands
from discord.ext import commands


class ChannelSelect(discord.ui.Select):
    def __init__(self, channels):
        options = [
            discord.SelectOption(label=c.name, value=str(c.id))
            for c in channels[:25]
        ]
        super().__init__(placeholder="pick a voice channel", options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.edit_message(content="joining...", view=None)
        channel = interaction.guild.get_channel(int(self.values[0]))
        vc = interaction.guild.voice_client
        try:
            if vc and vc.is_connected():
                await vc.move_to(channel)
            else:
                await channel.connect(self_deaf=True)
        except Exception as e:
            await interaction.edit_original_response(content=f"couldn't join: **{e}**")
            return
        await interaction.edit_original_response(
            content=f"joined **{channel.name}**, going afk"
        )


class ChannelView(discord.ui.View):
    def __init__(self, channels):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect(channels))


class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="joinvc", description="join a voice channel and stay afk")
    async def joinvc(self, interaction: discord.Interaction):
        channels = interaction.guild.voice_channels
        if not channels:
            await interaction.response.send_message("no voice channels here", ephemeral=True)
            return
        await interaction.response.send_message(
            "which channel should i join?",
            view=ChannelView(channels),
            ephemeral=True,
        )

    @app_commands.command(name="leavevc", description="disconnect the bot from voice")
    async def leavevc(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_connected():
            await vc.disconnect(force=True)
            await interaction.response.send_message("left the voice channel", ephemeral=True)
        else:
            await interaction.response.send_message("i'm not in a voice channel", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Voice(bot))
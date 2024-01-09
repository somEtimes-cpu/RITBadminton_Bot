import discord
from discord.ext import commands
from discord import app_commands
import os
import sys

class restart(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="restart")
    @commands.guild_only()
    @commands.is_owner()
    async def restart(self, interaction: discord.Interaction):
        await interaction.response.send_message("Restarting the bot...", ephemeral=True, silent=True)
        os.system("cls")
        os.execv(sys.executable, ['python'] + sys.argv)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(restart(bot))
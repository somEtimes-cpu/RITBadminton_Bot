import discord
from discord.ext import commands
from discord import app_commands

class shutdown(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name='shutdown')
    @commands.guild_only()
    @commands.is_owner()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("Shutting Down", ephemeral=True, silent=True)
        print("Closing")
        await(commands.Bot.close(self=self.bot))

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(shutdown(bot))
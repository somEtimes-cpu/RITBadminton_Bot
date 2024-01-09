import discord
from discord.ext import commands
from discord import app_commands
import Database.data_process as dp
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleAPICalls

class ResetConfirmation(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None


    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def NoButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Reset Cancelled"), delete_after=3 )

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray)
    async def YesButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await dp.set_all_paid_0()
        await interaction.response.edit_message(embed=discord.Embed(title="Reset Complete"), delete_after=30)

class CalibrateConfirmation(discord.ui.View):
    def __init__(self, googleAPIcreds: Credentials):
        super().__init__()
        self.value = None
        self.googleAPICreds = googleAPIcreds
    
    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def NoButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Calibrate Cancelled"), delete_after=3 )
    
    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def YesButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        gmail_client = build("gmail", "v1", credentials=self.googleAPICreds)
        progress_embed = discord.Embed(title="Calibrating")
        await interaction.response.send_message(embed=progress_embed, ephemeral=True, silent=True)
        all_names = await dp.get_all_verified_RIT_member_name()
        count = 0
        progress_embed.description = f"Calibrating: {count}/{len(all_names)}"
        await interaction.edit_original_response(embed=progress_embed)
        while count < len(all_names):
            current = all_names[count]
            due_paid = await googleAPICalls.is_due_paid(gmail_client=gmail_client, name=current)
            if due_paid:
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=1)
            else:
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=0)
            count += 1
            progress_embed.description = f"Calibrating: {count}/{len(all_names)}"
            await interaction.edit_original_response(embed=progress_embed)
        await interaction.edit_original_response(embed=discord.Embed(title="Calibrate Completed"))

class reset_all_paid_status(commands.Cog):
    def __init__(self, bot: commands.Bot, googleAPICreds: Credentials):
        self.bot = bot
        self.googleAPICreds = googleAPICreds
    
    @app_commands.command(name='reset_all_paid_status')
    @commands.guild_only()
    @commands.is_owner()
    async def reset_all_paid_status(self, interaction: discord.Interaction):
        Confirmation_embed = discord.Embed(title="Are you sure to reset all member's paid status?", description="Everybody's paid status will be set to 0")
        await interaction.response.send_message(embed=Confirmation_embed, view=ResetConfirmation(), ephemeral=True, delete_after=30, silent=True)
    
    @app_commands.command(name="members_paid_status_calibrate")
    @commands.guild_only()
    @commands.is_owner()
    async def members_paid_status_calibrate(self, interaction: discord.Interaction):
        Confirmation_embed = discord.Embed(title="Are you sure to check/update all member's paid status", description="This may take a while depend on the amount of members.")
        await interaction.response.send_message(embed=Confirmation_embed, view=CalibrateConfirmation(self.googleAPICreds), delete_after=20, ephemeral=True, silent=True)

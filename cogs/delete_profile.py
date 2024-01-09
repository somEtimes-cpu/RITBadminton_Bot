import discord
from discord.ext import commands
from discord import app_commands
import json
import datetime
import Database.data_process as dp

with open('private_files/discord_config.json', 'r') as f:
    data = json.load(f)
    registered_role = data["registered_role_name"].strip()
    username_verified_role = data["username_verified_role_name"].strip()
    paid_member_role = data["due_paid_role_name"].strip()
    general_roles = data["member_general_role_list"]
    pronoun_roles = data["member_pronoun_role_list"]

class Confirmation(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None


    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def NoButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Deletion Cancelled"), delete_after=3 )

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.gray)
    async def YesButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(embed=discord.Embed(title="Deleting Profile"), delete_after=30)
        member = interaction.guild.get_member(int(interaction.user.id))
        all_roles = general_roles + pronoun_roles
        all_roles.append(username_verified_role)
        all_roles.append(paid_member_role)
        all_roles.append(registered_role)
        for role in member.roles:
            if role.name != "@everyone" and (role.name in all_roles):
                await member.remove_roles(role)
        await dp.delete_profile(discord_id=interaction.user.id)
        await member.send(f"Your profile has been deleted at {datetime.datetime.now()}") 
        

    
class delete_profile(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name="delete_profile")
    @commands.guild_only()
    async def delete_profile(self, interaction: discord.Interaction):
        Confirmation_embed = discord.Embed(title="Are you sure to delete your existing profile", description="You will be removed from all roles and database")
        await interaction.response.send_message(embed=Confirmation_embed, view=Confirmation(), ephemeral=True, delete_after=30, silent=True)

async def setup(bot:commands.Bot) -> None:
    await bot.add_cog(delete_profile(bot))
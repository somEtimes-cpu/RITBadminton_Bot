import discord
from discord.ext import commands
from discord import app_commands
import discord.interactions
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import googleAPICalls
import asyncio
import Database.data_process as dp

with open('private_files/discord_config.json', 'r') as f:
    data = json.load(f)
    register_ChannelID = data["register_channel_ID"]
    registered_role = data["registered_role_name"].strip()
    username_verified_role = data["username_verified_role_name"].strip()
    paid_member_role = data["due_paid_role_name"].strip()
    register_button_cooldown = data["register_button_CoolDown_Seconds"]
    general_roles = data["member_general_role_list"]
    pronoun_roles = data["member_pronoun_role_list"]
    update_PaidStatus_Button_cooldown = data["update_PaidStatus_Button_cooldown_Seconds"]
    

class Register(discord.ui.View):
    def __init__(self, googleAPIcreds: Credentials):
        super().__init__(timeout=None)
        self.value = None
        self.cooldown = commands.CooldownMapping.from_cooldown(1, register_button_cooldown, commands.BucketType.member)
        self.googleAPIcreds = googleAPIcreds
    
    @discord.ui.button(label="Register", style=discord.ButtonStyle.green, custom_id="RegisterButton")
    async def registerButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        
        if retry:
            await interaction.user.send(f"Register Button on cool down for {round(retry,1)} seconds.")
            await interaction.response.defer()
        else:
            member = interaction.guild.get_member(int(interaction.user.id))
            if_already_exists_RIT_Student = await dp.get_Name(interaction.user.id)
            Username_Embed = discord.Embed(title="Paid Member RIT Username: ", description="Optional but the username is required for meeting check-in using Discord and LFG Channel")
            roles_Embed = discord.Embed(title="Select your desire roles to see corresponding channels", description="Note: LFG will only be accessible if you paid club dues")
            pronoun_Embed = discord.Embed(title="How do you want people to address you?")
            if if_already_exists_RIT_Student and if_already_exists_RIT_Student[0] != "None":
                RIT_Username = await dp.get_RIT_Username(discord_id=interaction.user.id)
                RIT_Username = RIT_Username[0]
                if_already_exists_RIT_Student = if_already_exists_RIT_Student[0]
                is_paid = await dp.get_paid_status(discord_id=interaction.user.id)
                Username_Embed = discord.Embed(title="RIT Info", description="Note: Update button has a cooldown of 3 minuets")
                Username_Embed.add_field(name="Name", value=if_already_exists_RIT_Student)
                Username_Embed.add_field(name="RIT Username", value=RIT_Username)
                Username_Embed.add_field(name="RIT Email", value=f"{RIT_Username}@rit.edu")
                Username_Embed.add_field(name="Current Term", value=(await googleAPICalls.get_current_term()))
                if is_paid[0] == 0:
                    Username_Embed.add_field(name="Purchased Member?", value="No")
                elif is_paid[0] == 1:
                    Username_Embed.add_field(name="Purchased Member?", value="Yes")
            await interaction.response.send_message(embed=Username_Embed, view=RIT_username(self.googleAPIcreds), ephemeral=True, silent=True)
            await interaction.followup.send(embed=roles_Embed, view=RoleSelectView(), ephemeral=True, silent=True)
            await interaction.followup.send(embed=pronoun_Embed, view=PronounSelectView(), ephemeral=True, silent=True)
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
            await dp.new_registered_member(discord_id=int(interaction.user.id), discord_name=interaction.user.name)


class RIT_username(discord.ui.View):
    def __init__(self, googleAPIcreds: Credentials):
        super().__init__(timeout=None)
        self.value = None
        self.googleAPIcreds = googleAPIcreds
        self.cooldown = commands.CooldownMapping.from_cooldown(1, update_PaidStatus_Button_cooldown, commands.BucketType.member)

    username_Embed = discord.Embed(title="RIT Info", description="Note: Update button has a cooldown of 3 minuets")
    username_Embed.add_field(name="Name", value="N/A")
    username_Embed.add_field(name="RIT Username", value="N/A")
    username_Embed.add_field(name="RIT Email", value="N/A")
    username_Embed.add_field(name="Current Term", value=asyncio.run(googleAPICalls.get_current_term()))
    username_Embed.add_field(name="Purchased Member?", value="N/A")
    
    @discord.ui.button(label="Edit", style=discord.ButtonStyle.green, custom_id="UsernameEditButton")
    async def editButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        if not (discord.utils.get(interaction.guild.roles, name=registered_role) in member.roles):
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
        await interaction.response.send_modal(RITusername_modal(self.googleAPIcreds, self.username_Embed))
    
    @discord.ui.button(label="Clear", style=discord.ButtonStyle.red, custom_id="UsernameClearButton")
    async def clearButton(self, interaction:discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        if not (discord.utils.get(interaction.guild.roles, name=registered_role) in member.roles):
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
        Username_Embed = discord.Embed(title="Paid Member RIT Username: ", description="Optional but the username is required for meeting check-in using Discord and LFG Channel")
        await interaction.response.edit_message(embed=Username_Embed)
        member = interaction.guild.get_member(int(interaction.user.id))
        await dp.delete_RIT_info(discord_id=interaction.user.id, discord_name=interaction.user.name)
        await member.remove_roles(discord.utils.get(interaction.guild.roles, name=paid_member_role))
        await member.remove_roles(discord.utils.get(interaction.guild.roles, name=username_verified_role))
        await member.send("Your registered RIT information has been deleted")

    @discord.ui.button(label="Update Purchase Status", style=discord.ButtonStyle.secondary, custom_id="UpdatePaidStatusButton")
    async def UpdatePaidStatusButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.guild.get_member(interaction.user.id)
        if not (discord.utils.get(interaction.guild.roles, name=registered_role) in member.roles):
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.user.send(f"Update Button on cool down for {round(retry,1)} seconds.")
            await interaction.response.defer()
        else:
            gmail_client = build("gmail", "v1", credentials=self.googleAPIcreds)            
            member = interaction.guild.get_member(int(interaction.user.id))
            name = await dp.get_Name(discord_id=interaction.user.id)
            if (not name) or (name[0] == "None") or (not any(role.name == username_verified_role for role in member.roles)):
                cannot_update_embed = discord.Embed(title="Please Register your RIT Information First")
                interaction.response.edit_message(embeds=cannot_update_embed)
                return
            RIT_Username = (await dp.get_RIT_Username(discord_id=interaction.user.id))[0]
            name = name[0]
            is_due_paid = await googleAPICalls.is_due_paid(gmail_client=gmail_client, name=name)
            self.username_Embed.set_field_at(index=0, name="Name", value=name)
            self.username_Embed.set_field_at(index=1, name="RIT Username", value=RIT_Username)
            self.username_Embed.set_field_at(index=2, name="RIT Email", value=f"{RIT_Username}@rit.edu")
            if is_due_paid:
                self.username_Embed.set_field_at(index=4, name="Purchased Member?", value="Yes")
                await member.add_roles(discord.utils.get(interaction.guild.roles, name=paid_member_role))
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=1)
            else:
                self.username_Embed.set_field_at(index=4, name="Purchased Member?", value="No")
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=0)
            await interaction.response.edit_message(embed=self.username_Embed)


class RITusername_modal(discord.ui.Modal):
    def __init__(self, googleAPIcreds: Credentials, username_Embed: discord.Embed):
        super().__init__(title="RIT Username")
        self.googleAPIcreds = googleAPIcreds
        self.username_Embed = username_Embed
    RIT_username = discord.ui.TextInput(label="What's your RIT username?", placeholder="Everything before @rit.edu, Ex: ji1082", max_length=10)

    async def on_submit(self, interaction: discord.Interaction):
        people_client = build("people", "v1", credentials=self.googleAPIcreds)
        gmail_client = build("gmail", "v1", credentials=self.googleAPIcreds)
        member = interaction.guild.get_member(int(interaction.user.id))
        is_Username_registered = await dp.is_Username_registered(RIT_Username=f"{self.RIT_username}", discord_id=interaction.user.id)
        if is_Username_registered:
            repeted_input = discord.Embed(title="RIT Info", description="This Username is already registered by another memeber")
            await interaction.response.edit_message(embed=repeted_input, view=RIT_username(self.googleAPIcreds))
            return

        isUsernameValid, names = await googleAPICalls.is_valid_RIT_username(people_client=people_client, ritUsername=self.RIT_username)
        if isUsernameValid and len(names) > 0:
            await dp.update_verified_username(discord_id=interaction.user.id, discord_name=interaction.user.name, RIT_username=self.RIT_username)
            await dp.update_name(discord_id=interaction.user.id, discord_name=interaction.user.name, name=names[0])
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=username_verified_role))
            self.username_Embed.set_field_at(index=0, name="Name", value=names[0])
            self.username_Embed.set_field_at(index=1, name="RIT Username", value=self.RIT_username)
            self.username_Embed.set_field_at(index=2, name="RIT Email", value=f"{self.RIT_username}@rit.edu")
            is_due_paid = await googleAPICalls.is_due_paid(gmail_client, names[0])
            if (is_due_paid):
                self.username_Embed.set_field_at(index=4, name="Purchased Member?", value="Yes")
                await member.add_roles(discord.utils.get(interaction.guild.roles, name=paid_member_role))
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=1)
            else:
                self.username_Embed.set_field_at(index=4, name="Purchased Member?", value="No")
                await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=0)
        elif isUsernameValid and len(names) < 1:
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=username_verified_role))
            await dp.update_verified_username(discord_id=interaction.user.id, RIT_username=self.RIT_username)
            await dp.update_name(discord_id=interaction.user.id, discord_name=interaction.user.name, name=names[0])
            await dp.update_paid_status(discord_id=interaction.user.id, discord_name=interaction.user.name, is_due_paid=0)
            self.username_Embed.title="Error in verification"
            self.username_Embed.description="Your RIT username is valid but we are unable to obtain your name to confirm your membership"
            self.username_Embed.set_field_at(index=1, name="RIT Username", value=self.RIT_username)
            self.username_Embed.set_field_at(index=2, name="RIT Email", value=f"{self.RIT_username}@rit.edu")

        else:
            self.username_Embed = discord.Embed(title="Error in verification", description="We are unable to verify your RIT username")

        await interaction.response.edit_message(embed=self.username_Embed, view=RIT_username(self.googleAPIcreds))

class RoleSelectMenu(discord.ui.Select):
    emojis = {"LFG":"🙌", "Equipments":"🏸", "Reservations":"🕰️"}
    def __init__(self):
        options = [discord.SelectOption(label="LFG", description="\"Looking for group\", discuss with others to play outside of club times!", emoji=self.emojis["LFG"]), 
                   discord.SelectOption(label="Equipments", description="Role for discussing purchasing equipment, recommendations, stringing settings, etc.", emoji=self.emojis["Equipments"]), 
                   discord.SelectOption(label="Reservations", description="Receive information on SLC reservations", emoji=self.emojis["Reservations"])]
        super().__init__(placeholder="What roles do you want?", options=options, max_values=len(options), custom_id="RoleSelectMenu")
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        if not (discord.utils.get(interaction.guild.roles, name=registered_role) in member.roles):
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
        if ("LFG" in self.values) and not (await dp.check_paid(interaction.user.id)):
            self.values.remove("LFG")
            roles_Embed = discord.Embed(title="Unable to join you to LFG", description="Makesure you have purchased Club Membership from Campus Group and Reselect your roles")
            msg = "LFG will only be accessible if you paid club dues, we joined you to other roles you chose: \n"
            for role in self.values:
                msg += f"{role} {self.emojis[role]}\n"
            roles_Embed.add_field(name="Notes", value=msg)
            await interaction.response.edit_message(embed=roles_Embed)
        else:
            await interaction.response.defer()

        for role in general_roles:
            if role in self.values:
                await member.add_roles(discord.utils.get(interaction.guild.roles, name=role))
            else:
                await member.remove_roles(discord.utils.get(interaction.guild.roles, name=role))

class RoleSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RoleSelectMenu())    

class PronounSelectMenu(discord.ui.Select):
    def __init__(self):
        options = [discord.SelectOption(label="He/Him", emoji="🔵"),
                   discord.SelectOption(label="She/Her", emoji="🔴"),
                   discord.SelectOption(label="They/Them", emoji="🟣"),
                   discord.SelectOption(label="Other Pronouns", emoji="⚪")]

        super().__init__(placeholder="Select your desired pronouns (Optional)", options=options, custom_id="PronounSelectMenu", min_values=0, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        if not (discord.utils.get(interaction.guild.roles, name=registered_role) in member.roles):
            await member.add_roles(discord.utils.get(interaction.guild.roles, name=registered_role))
        for role in pronoun_roles:
            if role in self.values:
                await member.add_roles(discord.utils.get(interaction.guild.roles, name=role))
                await dp.update_pronoun(discord_id=interaction.user.id, discord_name=interaction.user.name, pronoun=role)
            else:
                await member.remove_roles(discord.utils.get(interaction.guild.roles, name=role))
        if len(self.values) == 0:
            await dp.update_pronoun(discord_id=interaction.user.id, discord_name=interaction.user.name, pronoun=None)

        if "Other Pronouns" in self.values:
            pronoun_Embed = discord.Embed(title="How do you want people to address you?", description="We suggest you to specify your perferred pronouns in your profile")
            await interaction.response.edit_message(embed=pronoun_Embed)
        else:
            await interaction.response.defer()

class PronounSelectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(PronounSelectMenu())

class register(commands.Cog):
    def __init__(self, bot: commands.Bot, googleAPIcreds: Credentials):
        self.bot = bot
        self.googleAPIcreds = googleAPIcreds
        
    @app_commands.command(name="register_channel_setup")
    @commands.guild_only()
    async def register(self, interaction: discord.Interaction):
        channel = interaction.channel
        if channel.id != register_ChannelID:
            await interaction.response.send_message("This command is only allowed in the register channel", ephemeral=True)
            return
        await channel.purge(limit=100)
        setup_embed = discord.Embed(title="Click the button to start setting up your channels.", description="You can also edit or re-register your responses to make changes.\nNotes: The \"Register\" Button has a 5 minutes cooldown")
        await interaction.response.send_message(embed=setup_embed, view=Register(self.googleAPIcreds), silent=True)
    
    async def auto_setup(self):
        self.bot.add_view(Register(self.googleAPIcreds))
        self.bot.add_view(RIT_username(self.googleAPIcreds))
        self.bot.add_view(RoleSelectView())
        self.bot.add_view(PronounSelectView())


#no longer needed since we are adding the cog directly in the new_bot.py. Previous load.extention does not take parameters
"""async def setup(bot:commands.Bot, googleAPIcreds: Credentials) -> None:
    await bot.add_cog(register(bot, googleAPIcreds))"""
        
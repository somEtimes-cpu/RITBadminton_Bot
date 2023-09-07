import os
import sys
import discord
from discord import app_commands
from discord.ext import commands
import pytz
from datetime import datetime
import time
import asyncio
import database_process
from object_classes import Discord_Member
from object_classes import reserved_event


TOKEN = os.getenv("DISCORD_TOKEN")

def run_discord_bot():
    owners=[176022438281347072]
    Sign_in_channel_id = 1142172008017297408 #need to change to the correct channel ID

    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix='_', owner_ids=set(owners), description="Badminton Club Bot", intents=intents)

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        print('------')
        try:
            synced = await bot.tree.sync(guild=None)
            print(f"Synced {len(synced)} command(s)")
        except Exception as e:
            print(e)

    @bot.event
    async def on_command_error(ctx, error):
        if isinstance(error, commands.NoPrivateMessage):
            await ctx.send("This command can only be used within a guild.")

    @bot.tree.command(name="shutdown")
    @commands.guild_only()
    @commands.is_owner()
    async def shutdown(interaction: discord.Interaction):
        await interaction.response.send_message("Shutting Down", ephemeral=True)
        print("Closing")
        await(bot.close())

    @bot.tree.command(name="restart")
    @commands.guild_only()
    @commands.is_owner()
    async def restart(interaction: discord.Interaction):
        await interaction.response.send_message("Restarting the bot...", ephemeral=True)
        os.system("cls") 
        os.execv(sys.executable, ['python'] + sys.argv)

    async def register_reaction(channel, question: str, timeout: float, emojis: list):
        def check(reaction, user):
            return user != bot.user and reaction.message.id == sent.id and (str(reaction.emoji) in emojis)
        
        embed = discord.Embed(title=None, url=None, description=question, color=discord.Color.orange())
        sent = await channel.send(embed=embed)
        for emoji in emojis:
            await sent.add_reaction(emoji)
        reaction, user = await bot.wait_for("reaction_add", check=check, timeout=timeout)
        return reaction

    async def register_msg(channel, question: str, timeout: float):
        def check(m):
            return m.author != bot.user and m.channel == channel
        embed = discord.Embed(title=None, url=None, description=question, color=discord.Color.orange())
        await channel.send(embed=embed)
        response = await bot.wait_for("message", check=check, timeout=timeout)
        return response.content

    def log_info(member_discord_name: str, member_discord_id: str, is_RIT: discord.reaction.Reaction, first_name: str, last_name:str, Email: str, pronun:str,):
        is_RIT_str = 'False'
        pronoun_str = 'He/Him'
        if str(is_RIT) == '✅':
            is_RIT_str = 'True'

        if str(pronun) == '👧':
            pronoun_str = 'She/Her'
        elif str(pronun) == '🧑‍🦱':
            pronoun_str = 'They/Them'
            
        new_member = Discord_Member(Discrod_Name=member_discord_name, 
                                    Discord_ID=member_discord_id, 
                                    is_RIT=is_RIT_str,
                                    First_name=first_name,
                                    Last_name=last_name,
                                    Email=Email,
                                    pronoun=pronoun_str,
                                    is_Eboard='False',
                                    is_Former_Eboard='False')
        database_process.insert_member(new_member)
        print(database_process.get_all_members())
        
    async def register_info(interaction:discord.Interaction, member: discord.user):
        try:
            await interaction.followup.send("Please check your DM to continue the registration", ephemeral=True)
            #need to change to the correct role iD, registering / registered
            await member.add_roles(discord.utils.get(interaction.guild.roles, name='registering')) #need to change to the correct role
            dm_channel = await bot.create_dm(user= interaction.guild.get_member(int(interaction.user.id)))
            is_RIT = await register_reaction(dm_channel, "Are you a RIT student?", 120, ['✅', '❌'])
            print(is_RIT)
            first_name = await register_msg(dm_channel, "What is your first name?", 120)
            print(first_name)
            last_name = await register_msg(dm_channel, "What is your last name?", 120)
            print(last_name)
            pronoun = await register_reaction(dm_channel, "Select your pronoun: \n👧 = She/Her \n👦 = He/Him \n🧑‍🦱 = They/Them", 120, ['👧', '👦', '🧑‍🦱'])
            print(pronoun)
            Email = await register_msg(dm_channel, "What is your Email? (RIT school email perferred)", 120)
            print(Email)
            await dm_channel.send('You have succussfully been registered. You should received a new role as registered in the Discord Server')
            if member != interaction.guild.owner:
                await member.edit(nick=f"{first_name} {last_name}")
            else:
                await interaction.followup.send("Hi Boss, I'm unable to change server owner's nickname.", ephemeral=True)
            return is_RIT, first_name.capitalize(),last_name.capitalize(), pronoun, Email
        except asyncio.TimeoutError:
                await interaction.followup.send('Timed out, please start over', ephemeral=True)
                await dm_channel.send('Timed out, please start over')
                await member.remove_roles(discord.utils.get(interaction.guild.roles, name='registering')) #need to change to the correct role


    @bot.tree.command(name='register')
    @commands.guild_only()
    async def register(interaction: discord.Interaction):
        try:
            member = interaction.guild.get_member(int(interaction.user.id))
            await interaction.response.defer(ephemeral=True)
            if member != None and member != bot.user.id: 
                if (discord.utils.get(interaction.guild.roles, name='registering') not in member.roles) and (discord.utils.get(interaction.guild.roles, name='registered') not in member.roles) or len(database_process.find_member(member.id)) == 0: #need to change to the correct role names
                    is_RIT, first_name, last_name, pronoun, Email = await register_info(interaction, member)

                    await interaction.followup.send("You are registered!", ephemeral=True)
                    await member.remove_roles(discord.utils.get(interaction.guild.roles, name='registering')) #need to change to the correct role
                    time.sleep(0.1)
                    log_info(str(interaction.user), interaction.user.id, is_RIT, first_name, last_name, Email, pronoun)
                    await member.add_roles(discord.utils.get(interaction.guild.roles, name='registered')) #need to change to the correct role
                    return
                else:
                    await interaction.followup.send('It seems like you are already in the process of registering or already registered. If you like to restart, use the command /re_register', ephemeral=True)
                    return
            else:
                await interaction.followup.send("Seems like something is wrong, try again later or contact for help", ephemeral=True)
                return
        except Exception as e:
            print(e)
        
    @bot.tree.command(name='re_register')
    @commands.guild_only()
    async def re_register(interaction: discord.Interaction):
        try:
            member = interaction.guild.get_member(int(interaction.user.id))
            await interaction.response.defer(ephemeral=True)

            def check(m):
                return m.author == member and m.channel == interaction.channel
            embed1 = discord.Embed(title=None, description='Are you sure you want to re-register?\nEnter **Yes** or **No** to confirm.', url=None, color=discord.Color.orange())
            embed2 = discord.Embed(title=None, description='Action Cancelled', url=None, color=discord.Color.orange())
            embed3 = discord.Embed(title=None, description='Response not recognized, action cancelled', url=None, color=discord.Color.orange())

            await interaction.followup.send(embed=embed1, ephemeral=True)
            response = await bot.wait_for("message", check=check, timeout=120)
            await response.delete()
            if response.content.lower().strip() == 'yes':
                database_process.delete_member(member.id)
                await member.remove_roles(discord.utils.get(interaction.guild.roles, name='registered')) #need to change to the correct role
                is_RIT, first_name, last_name, pronoun, Email = await register_info(interaction, member)
                await member.remove_roles(discord.utils.get(interaction.guild.roles, name='registering')) #need to change to the correct role
                log_info(str(interaction.user), interaction.user.id, is_RIT, first_name, last_name, Email, pronoun)
                await interaction.followup.send("Information Updated", ephemeral=True)
                await member.add_roles(discord.utils.get(interaction.guild.roles, name='registered')) #need to change to the correct role
                return
            elif response.content.lower().strip() == 'no':
                await interaction.followup.send(embed=embed2, ephemeral=True)
                return
            else:
                await interaction.followup.send(embed=embed3, ephemeral=True)
                return
        except asyncio.TimeoutError:
            await interaction.followup.send('Timed out, please start over', ephemeral=True)
      
    
    bot.run(TOKEN)

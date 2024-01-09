import discord
from discord.ext import tasks, commands
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os
import cogs.register_channel_setup
import cogs.reset_all_paid_status


class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'),intents=discord.Intents().all())
        self.coglist = ["cogs.shutdown", "cogs.restart","cogs.register_channel_setup", "cogs.delete_profile", "cogs.reset_all_paid_status"]
        self.gmail_client = None
        self.people_client = None
        self.APIcreds = None
        self.SCOPE = ["https://www.googleapis.com/auth/contacts.readonly", 
                        "https://www.googleapis.com/auth/directory.readonly",
                        "https://www.googleapis.com/auth/gmail.settings.basic",
                        "https://www.googleapis.com/auth/gmail.modify"]
        self.setup_google_clients()
    
    def setup_google_clients(self):
            if os.path.exists("private_files/googleAPItoken.json"):
                self.APIcreds= Credentials.from_authorized_user_file("private_files/googleAPItoken.json", self.SCOPE)
            if not self.APIcreds or not self.APIcreds.valid:
                if self.APIcreds and self.APIcreds.expired and self.APIcreds.refresh_token:
                    self.APIcreds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file("private_files/client_secret.json", self.SCOPE)
                    self.APIcreds = flow.run_local_server(port=0)
                with open("private_files/googleAPItoken.json", "w") as f:
                    f.write(self.APIcreds.to_json())
    
    @tasks.loop(minutes=50)
    async def token_refresh(self):
        try:
            self.APIcreds.refresh(Request())
            with open("private_files/googleAPItoken.json", 'w') as f:
                f.write(self.APIcreds.to_json())
        except Exception as e:
            print(e)
    
    async def setup_hook(self):
        for ext in self.coglist:
            if ext == "cogs.register_channel_setup":
                await bot.add_cog(cogs.register_channel_setup.register(bot, self.APIcreds))
            elif ext == "cogs.reset_all_paid_status":
                await bot.add_cog(cogs.reset_all_paid_status.reset_all_paid_status(bot, self.APIcreds))       
            else:
                await self.load_extension(ext)
        register_cog = self.get_cog("register")
        await register_cog.auto_setup()
        self.token_refresh.start()
    
    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        synced = await self.tree.sync(guild=None)
        print(f"Synced {len(synced)} command(s)")


with open('private_files/discord_config.json', 'r') as f:
    data = json.load(f)
    TOKEN = data['TOKEN']

bot = Bot()

bot.run(TOKEN)
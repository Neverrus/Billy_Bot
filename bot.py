import discord
import os
from discord.ext import commands

"""
client = commands.Bot(command_prefix=".")

@client.event
async def on_ready():
           print("Billy is fucking coming!")

@client.event
async def hello(ctx):
          await ctx.send("Fuck you!")
"""
class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on ass', self.user)

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'hello':
            await message.channel.send('Fuck you!')

token = os.getenv("TOKEN")
client = MyClient()
client.run(token)
import discord
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

client = MyClient()
client.run("OTQwMjI3ODM1NTY4NzE3ODM1.YgEVaA.mXyv6GDx7tJBWzyW7v6v580xRg0")
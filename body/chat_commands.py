import discord
import os


class BillyCommands(discord.Client):

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == "hello":
            await message.channel.send("Fuck you!")
import os
from body.music import Music
import youtube_dl
from discord.ext import commands
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy


youtube_dl.utils.bug_reports_message = lambda: ""

"""
with open("SpotipyClientID.txt", "r") as scid:
    spotipy_id = scid.read().strip()
    scid.close()
with open("SpotipyClientSecret.txt", "r") as scs:
    spotipy_secret = scs.read().strip()
    scs.close()
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=spotipy_id, client_secret=spotipy_secret
    )
)
"""

spotipy_id = os.getenv("SpotipyClientID")

spotipy_secret = os.getenv("SpotipyClientSecret")

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=spotipy_id, client_secret=spotipy_secret
    )
)


bot = commands.Bot(command_prefix=".", case_insensitive=True)
bot.add_cog(Music(bot))


@bot.event
async def on_ready():
    print("Logged in ass:\n{0.user.name}\n{0.user.id}".format(bot))


@bot.command()
async def hello(ctx):
    await ctx.send("Fuck you!")


if __name__ == "__main__":
    token = os.getenv("TOKEN")
    bot.run(token)

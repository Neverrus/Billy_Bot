import math
from body.voicestate import VoiceState
import discord
from discord.ext import commands
from body.spotify import Spotify
from body.ytdl_source import YTDLSource, YTDLError
from body.song import Song


class VoiceError(Exception):
    pass


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, ctx: commands.Context):
        state = self.voice_states.get(ctx.guild.id)
        if not state or not state.exists:
            state = VoiceState(self.bot, ctx)
            self.voice_states[ctx.guild.id] = state

        return state

    def cog_unload(self):
        for state in self.voice_states.values():
            self.bot.loop.create_task(state.stop())

    def cog_check(self, ctx: commands.Context):
        if not ctx.guild:
            raise commands.NoPrivateMessage(
                "This command can't be used in DM channels."
            )

        return True

    async def cog_before_invoke(self, ctx: commands.Context):
        ctx.voice_state = self.get_voice_state(ctx)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        await ctx.send("An error occurred: {}".format(str(error)))

    @commands.command(name="join", invoke_without_subcommand=True)
    async def _join(self, ctx: commands.Context):
        """Joins a voice channel."""

        destination = ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()

    @commands.command(name="summon")
    @commands.has_permissions(manage_guild=True)
    async def _summon(
        self, ctx: commands.Context, *, channel: discord.VoiceChannel = None
    ):
        """Summons the bot to a voice channel.
        If no channel was specified, it joins your channel.
        """

        if not channel and not ctx.author.voice:
            raise VoiceError(
                "You are neither connected to a voice channel nor specified a channel to join."
            )

        destination = channel or ctx.author.voice.channel
        if ctx.voice_state.voice:
            await ctx.voice_state.voice.move_to(destination)
            return

        ctx.voice_state.voice = await destination.connect()
        await ctx.guild.change_voice_state(
            channel=destination, self_mute=False, self_deaf=True
        )

    @commands.command(name="leave", aliases=["disconnect"])
    @commands.has_permissions(manage_guild=True)
    async def _leave(self, ctx: commands.Context):
        """Clears the queue and leaves the voice channel."""

        if not ctx.voice_state.voice:
            return await ctx.send("Not connected to any voice channel.")

        await ctx.voice_state.stop()
        del self.voice_states[ctx.guild.id]

    @commands.command(name="volume")
    async def _volume(self, ctx: commands.Context, *, volume: int):
        """Sets the volume of the player."""

        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")

        if 0 > volume > 200:
            return await ctx.send("Volume must be between 0 and 200")

        ctx.voice_state.volume = volume / 200
        await ctx.send("Volume of the player set to {}%".format(volume))

    @commands.command(name="now", aliases=["current", "playing"])
    async def _now(self, ctx: commands.Context):
        """Displays the currently playing song."""
        embed = ctx.voice_state.current.create_embed()
        await ctx.send(embed=embed)

    @commands.command(name="pause", aliases=["pa"])
    @commands.has_permissions(manage_guild=True)
    async def _pause(self, ctx: commands.Context):
        """Pauses the currently playing song."""
        print(">>>Pause Command:")
        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_playing():
            ctx.voice_state.voice.pause()
            await ctx.message.add_reaction("???")

    @commands.command(name="resume", aliases=["re", "res"])
    @commands.has_permissions(manage_guild=True)
    async def _resume(self, ctx: commands.Context):
        """Resumes a currently paused song."""

        if ctx.voice_state.is_playing and ctx.voice_state.voice.is_paused():
            ctx.voice_state.voice.resume()
            await ctx.message.add_reaction("???")

    @commands.command(name="stop")
    @commands.has_permissions(manage_guild=True)
    async def _stop(self, ctx: commands.Context):
        """Stops playing song and clears the queue."""

        ctx.voice_state.songs.clear()

        if ctx.voice_state.is_playing:
            ctx.voice_state.voice.stop()
            await ctx.message.add_reaction("???")

    @commands.command(name="skip", aliases=["s"])
    async def _skip(self, ctx: commands.Context):
        """Skip current song"""

        if not ctx.voice_state.is_playing:
            return await ctx.send("Not playing any music right now...")

        if ctx.voice_state.is_playing:
            await ctx.message.add_reaction("???")
            ctx.voice_state.skip()

    @commands.command(name="queue")
    async def _queue(self, ctx: commands.Context, *, page: int = 1):
        """Shows the player's queue.
        You can optionally specify the page to show. Each page contains 10 elements.
        """

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        items_per_page = 10
        pages = math.ceil(len(ctx.voice_state.songs) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue = ""
        for i, song in enumerate(ctx.voice_state.songs[start:end], start=start):
            queue += "`{0}.` [**{1.source.title}**]({1.source.url})\n".format(
                i + 1, song
            )

        embed = discord.Embed(
            description="**{} tracks:**\n\n{}".format(len(ctx.voice_state.songs), queue)
        ).set_footer(text="Viewing page {}/{}".format(page, pages))
        await ctx.send(embed=embed)

    @commands.command(name="shuffle")
    async def _shuffle(self, ctx: commands.Context):
        """Shuffles the queue."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.shuffle()
        await ctx.message.add_reaction("???")

    @commands.command(name="remove")
    async def _remove(self, ctx: commands.Context, index: int):
        """Removes a song from the queue at a given index."""

        if len(ctx.voice_state.songs) == 0:
            return await ctx.send("Empty queue.")

        ctx.voice_state.songs.remove(index - 1)
        await ctx.message.add_reaction("???")

    @commands.command(name="loop")
    async def _loop(self, ctx: commands.Context):
        """Loops the currently playing song.
        Invoke this command again to unloop the song.
        """

        if not ctx.voice_state.is_playing:
            return await ctx.send("Nothing being played at the moment.")

        # Inverse boolean value to loop and unloop.
        ctx.voice_state.loop = not ctx.voice_state.loop
        await ctx.message.add_reaction("???")

    @commands.command(name="play", aliases=["p"])
    async def _play(self, ctx: commands.Context, *, search: str):
        # Checks if song is on spotify and then searches.
        if not ctx.voice_state.voice:
            await ctx.invoke(self._join)
        if (
            "https://open.spotify.com/playlist/" in search
            or "spotify:playlist:" in search
        ):
            async with ctx.typing():
                try:
                    trackcount = 0
                    process = await ctx.send(f"Processing. . .")
                    ids = Spotify.getPlaylistTrackIDs(self, search)
                    tracks = []
                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)
                    for track in tracks:
                        trackcount += 1
                        try:
                            source = await YTDLSource.create_source(
                                ctx, track, loop=self.bot.loop
                            )
                        except YTDLError as e:
                            await ctx.send(
                                "An error occurred while processing this request: {}".format(
                                    str(e)
                                )
                            )
                        else:
                            song = Song(source)
                            await ctx.voice_state.songs.put(song)
                except Exception as err:
                    await ctx.send("Error!")
                    print(err)
        elif "https://open.spotify.com/album/" in search or "spotify:album:" in search:
            async with ctx.typing():
                process = await ctx.send(f"Processing. . .")
                try:
                    ids = Spotify.getAlbum(self, search)
                    tracks = []
                    for i in range(len(ids)):
                        track = Spotify.getTrackFeatures(self, ids[i])
                        tracks.append(track)
                    for track in tracks:
                        try:
                            source = await YTDLSource.create_source(
                                ctx, track, loop=self.bot.loop
                            )
                        except YTDLError as e:
                            await ctx.send(
                                "An error occurred while processing this request: {}".format(
                                    str(e)
                                )
                            )
                        else:
                            song = Song(source)
                            await ctx.voice_state.songs.put(song)
                            await process.edit(content="Album Succesfully Grabbed.")
                except Exception as err:
                    await ctx.send("Error!")
                    print(err)
        elif "https://open.spotify.com/track/" in search or "spotify:track:" in search:
            async with ctx.typing():
                process = await ctx.send(f"Processing. . .")
                try:
                    ID = Spotify.getTrackID(self, search)
                    track = Spotify.getTrackFeatures(self, ID)
                    source = await YTDLSource.create_source(
                        ctx, track, loop=self.bot.loop
                    )
                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await process.edit(content="Track Succesfully Grabbed.")
                except Exception as err:
                    await ctx.send("Error!")
                    print(err)
        else:
            async with ctx.typing():
                try:
                    source = await YTDLSource.create_source(
                        ctx, search, loop=self.bot.loop
                    )
                except YTDLError as e:
                    await ctx.send(
                        "An error occurred while processing this request: {}".format(
                            str(e)
                        )
                    )
                else:
                    if not ctx.voice_state.voice:
                        await ctx.invoke(self._join)

                    song = Song(source)
                    await ctx.voice_state.songs.put(song)
                    await ctx.send("Enqueued {}".format(str(source)))

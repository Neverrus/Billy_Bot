import discord
from ytdl_source import YTDLSource


class Song:
    __slots__ = ("source", "requester")

    def __init__(self, source: YTDLSource):
        self.source = source
        self.requester = source.requester

    def create_embed(self):
        embed = discord.Embed(
            title="Now playing",
            description="```css\n{0.source.title}\n```".format(self),
            color=discord.Color.blurple(),
        )
        embed.add_field(name="Duration", value=self.source.duration)
        embed.add_field(name="Requested by", value=self.requester.mention)
        embed.add_field(
            name="Uploader",
            value="[{0.source.uploader}]({0.source.uploader_url})".format(self),
        )
        embed.add_field(name="URL", value="[Click]({0.source.url})".format(self))
        embed.set_thumbnail(url=self.source.thumbnail)
        embed.set_author(name=self.requester.name, icon_url=self.requester.avatar_url)
        return embed

from discord.message import Message
import discord
import asyncio
import ignore

from discord.ext import commands
from text2wav import text2wav
from Item import Item
import pyvcroid2

class VoiceroidTTSBot(commands.Cog):
    def __init__(self, bot, vc):
        self.bot: commands.Bot = bot
        self.vcroid: pyvcroid2.VcRoid2 = vc
        self.text_channel: discord.TextChannel = None
        self.voice_channel: discord.VoiceChannel = None
        self.voice_client: discord.VoiceClient = None

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # not doing anything for self.
        if message.author.bot:
            return

        # do not read any commands for akari
        if message.content.startswith('!'):
            return

        # play tts, when bot is connected to vc.
        if self.voice_client is not None:
            if self.voice_client.is_connected() is False:
                return

            if message.channel != self.text_channel:
                return

            # wait until finish playing sound when next sound is in queue.
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)

            # if started with words specified in ignore.json
            ignored_words_matched = [word for word in ignore.start_with if message.content.startswith(word)]
            if len(ignored_words_matched) != 0:
                return

            if message.content.find("～") != -1:
                message.content = message.content.replace("～", "ー")

            print(message.content)
            self.play_sound(message.content)

    def play_sound(self, content: str):
        source = discord.FFmpegPCMAudio(text2wav(self.vcroid, content))
        self.voice_client.play(source)

    @commands.command()
    async def akari(self, ctx: commands.Context, mode: str=None):
        if mode is None:
            await self.join_voice(ctx)
            return

        if mode == "bye":
            await self.leave_voice(ctx)
            return

    async def join_voice(self, ctx: commands.Context):
        command_author: Message.author = ctx.author
        if command_author.voice is None:
            await ctx.channel.send("呼んだ人がボイスチャットにいないよ！")
            return

        if self.voice_client is None:
            self.text_channel = ctx.channel
            self.voice_client = await ctx.author.voice.channel.connect()
            self.play_sound("あかりちゃんだよー")
            return

        if self.voice_client.is_connected():
            self.text_channel = ctx.channel
            await self.voice_client.move_to(ctx.author.voice.channel)
            return
        else:
            self.voice_client = None
            self.text_channel = None

    async def leave_voice(self, ctx: commands.Context):
        if self.voice_client is None:
                return

        if self.voice_client.is_connected():
            if ctx.channel is not self.text_channel:
                return

            self.play_sound("ばいばーい")
            await asyncio.sleep(2)
            await self.voice_client.disconnect()
            self.voice_client = None
            self.text_channel = None
            return

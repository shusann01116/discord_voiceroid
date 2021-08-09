from ui import SelectTextChannel, SelectVoiceChannel
import discord
import asyncio

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

        if message.content in ["!akarichan", "!akari"]:
            if message.author.voice is None:
                await message.channel.send("呼んだ人がボイスチャットにいないよ！")
                return

            if self.voice_client is None:
                self.text_channel = message.channel
                self.voice_client = await message.author.voice.channel.connect()
                await asyncio.sleep(0.1)
                self.play_sound("あかりちゃんだよー")
                return

            if self.voice_client.is_connected():
                self.text_channel = message.channel
                await self.voice_client.move_to(message.author.voice.channel)
                return
            else:
                self.voice_client = None
                self.text_channel = None

        if message.content in ["!bye"]:
            if self.voice_client is None:
                return

            if self.voice_client.is_connected():
                self.play_sound("ばいばーい")
                await asyncio.sleep(2)
                self.voice_client.disconnect()
                self.voice_client = None
                self.text_channel = None
                return

        # play tts, when bot is connected to vc.
        if self.voice_client is not None and self.voice_client.is_connected() is True:
            if message.channel == self.text_channel:
                # wait until finish playing when next sound is in queue.
                while self.voice_client.is_playing():
                    await asyncio.sleep(0.1)
                print(message.content)
                source = discord.FFmpegPCMAudio(text2wav(self.vcroid, message.content))
                self.voice_client.play(source)
                self.play_sound(message.content)

    def play_sound(self, content: str):
        source = discord.FFmpegPCMAudio(text2wav(self.vcroid, content))
        self.voice_channel.play(source)

    @commands.command()
    async def d(self, ctx: commands.Context):
        print(f"debug: {Item.text_channel, Item.voice_channel}")

from importlib.resources import contents
from pickletools import unicodestring1
from discord import VoiceChannel, embeds
from discord.message import Message
import discord
import asyncio
import ignore
import re

from discord.ext import commands
from text2wav import text2wav
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

        # return when a recieved message was not the channel to tts.
        if message.channel != self.text_channel:
            return

        # play tts, when bot is connected to vc.
        if self.voice_client is not None:
            if self.voice_client.is_connected() is False:
                return

            # wait until finish playing sound when next sound is in queue.
            while self.voice_client.is_playing():
                await asyncio.sleep(0.1)
                
            # encode content to shift_jis
            message.content = message.content.encode('shift_jis', 'ignore').decode('shift_jis')
            if len(message.content) == 0:
                return

            # if started with words specified in ignore.json
            ignored_words_matched = [
                word for word in ignore.start_with if message.content.startswith(word)]
            if len(ignored_words_matched) != 0:
                return

            # find and replace specific letters which occurre encoding error.
            if message.content.find("～") != -1:
                message.content = message.content.replace("～", "ー")

            print(message.content)
            self.play_sound(message.content)

    # generate and play voice on vc
    def play_sound(self, content: str):
        source = discord.FFmpegPCMAudio(text2wav(self.vcroid, content))
        self.voice_client.play(source)

    @commands.command()
    async def akari(self, ctx: commands.Context, mode: str = None, *args):
        # join to vc.
        if mode is None:
            await self.join_voice(ctx)
            return

        # leave vc.
        if mode in ["b", "bye"]:
            await self.leave_voice(ctx)
            return

        # show help.
        if mode in ["h", "help"]:
            await self.show_help(ctx)
            return

        # change voice parameter.
        if mode in ["v", "voice"]:
            # show voice parameter help and return
            # if arguments are not correct
            # it represents default when 2nd parameter is d.
            if len(args) != 2 and args.index(2) != 'd':
                self.show_voiceparameters_help()
                return

            await self.change_voiceparameters(ctx, *args)
            return

    async def join_voice(self, ctx: commands.Context):
        command_author: Message.author = ctx.author

        # when summoner of bot is not in vc.
        if command_author.voice is None:
            message: discord.Message = ctx.message
            embed = discord.Embed(title="呼んだ人がボイスチャットにいないよ！")
            await message.channel.send(embed=embed)
            return

        # when bot's connection is not established.
        if self.voice_client is None:
            await self.show_help(ctx)
            self.text_channel = ctx.channel
            self.voice_client = await ctx.author.voice.channel.connect()
            self.play_sound("あかりちゃんだよー")
            return

        # move to next chennel when connection is already established.
        if self.voice_client.is_connected():
            self.text_channel = ctx.channel
            await self.voice_client.move_to(ctx.author.voice.channel)
            return
        # otherwise delete pointers of instances.
        else:
            self.voice_client = None
            self.text_channel = None

    async def leave_voice(self, ctx: commands.Context):
        if self.voice_client is None:
            return

        if self.voice_client.is_connected():
            if ctx.channel is not self.text_channel:
                return
            if ctx.author.voice is None:
                message: discord.Message = ctx.message
                embed = embeds.Embed(title="VCに参加してからばいばいしてね:sob:")
                await message.channel.send(embed=embed)
                return

            self.play_sound("ばいばーい")
            await asyncio.sleep(2)
            await self.voice_client.disconnect()
            self.voice_client = None
            self.text_channel = None
            return

    async def show_help(self, ctx: commands.Context):
        message: discord.Message = ctx.message
        embed = embeds.Embed(title="あかりちゃんのへるぷ！")
        embed.add_field(name="参加してほしい時", value="ボイスチャットに参加して、読み上げてほしいチャンネルで`!akari`を送信してね！", inline=False)
        embed.add_field(name="帰ってほしい時 :sob:", value="`!akari bye`で帰るよ、悲しい :sob:", inline=False)
        embed.add_field(name="ボイスパラメータを変えたい時 :musical_note:", value="`!akari v {モード} {設定値}`を送信してね！\n詳しくは、`!akari v h`で見れるよ！", inline=False)
        await message.channel.send(embed=embed)
        return

    async def change_voiceparameters(self, ctx: commands.Context, param: str, value):
        value = float(value)
        message: discord.Message = ctx.message
        if param in ["d", "default"]:
            self.vcroid.param.speed = 1.0
            self.vcroid.param.pitch = 1.0
            embed = discord.Embed(title="パラメータせってい", description="スピードとピッチをデフォルトに戻したよ。")
            await message.channel.send(embed=embed)
            return

        if param in ["s", "speed"] and 0.5 <= value <= 4.0:
            self.vcroid.param.speed = value
            embed = discord.Embed(title="パラメータせってい", description=f"スピードを{value}にセットしたよ。")
            await message.channel.send(embed=embed)
            return

        if param in ["p", "pitch"] and 0.5 <= value <= 2.0:
            self.vcroid.param.pitch = value
            embed = discord.Embed(title="パラメータせってい", description=f"ピッチを{value}にセットしたよ。")
            await message.channel.send(embed=embed)
            return

        await self.show_voiceparameters_help(ctx)
        return

    async def show_voiceparameters_help(self, ctx: commands.Context):
        message: discord.Message = ctx.message
        embed = discord.Embed(title="パラメータコマンドのへるぷ！", description="`!akari v {設定項目} {値}`のように記載してね。")
        embed.add_field(name="設定項目", value="ピッチは`p`、スピードは`s`だよ。\nデフォルトに戻したいときは`d`を指定してね。\nスピードは0.5から4.0でピッチは0.5から2.0までだよ！", inline=False)
        embed.add_field(name="値", value="値は設定項目によって取りうる範囲が決まってるよ。\n~~そんなに早く喋れないんだからね！~~", inline=False)
        embed.add_field(name="例", value="`!akari v s 1.2`\nデフォルトに戻したいときは`!akari v d`でできるよ！")
        await message.channel.send(embed=embed)
        return

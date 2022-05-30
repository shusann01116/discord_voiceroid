import asyncio
import discord
from discord.ext import commands
import pyvcroid2
import time
import re

import private


class AkariVoice():
    def __init__(self) -> None:
        self.vcRoid = pyvcroid2.VcRoid2()
        self._initVcRoid()

    def _initVcRoid(self) -> pyvcroid2.VcRoid2:
        vcRoidParams = {
            'volume': 1.0,
            'speed': 1.0,
            'pitch': 1.0,
            'emphasis': 1.0,
            'pauseMiddle': 80,
            'pauseLong': 100,
            'pauseSentence': 20,
            'masterVolume': 1.0,
        }

        lang_list = self.vcRoid.listLanguages()
        if "standard" in lang_list:
            self.vcRoid.loadLanguage("standard")
        else:
            raise Exception("No language library")
        voice_list = self.vcRoid.listVoices()
        if 0 < len(voice_list):
            self.vcRoid.loadVoice(voice_list[0])
        else:
            raise Exception("No voice library")
        self.vcRoid.param.volume = vcRoidParams['volume']
        self.vcRoid.param.speed = vcRoidParams['speed']
        self.vcRoid.param.pitch = vcRoidParams['pitch']
        self.vcRoid.param.emphasis = vcRoidParams['emphasis']
        self.vcRoid.param.pauseMiddle = vcRoidParams['pauseMiddle']
        self.vcRoid.param.pauseLong = vcRoidParams['pauseLong']
        self.vcRoid.param.pauseSentence = vcRoidParams['pauseSentence']
        self.vcRoid.param.masterVolume = vcRoidParams['masterVolume']

    def generate_voice(self, text, filename="temp.wav") -> str:
        """Generate wav file and return its name."""

        speech, _ = self.vcRoid.textToSpeech(text)

        with open(filename, "wb") as f:
            f.write(speech)

        return filename


akariVoice = AkariVoice()


class Akari(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.channel: discord.channel = None
        self.voice_client: discord.VoiceClient = None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        """Is called when messages are posted"""
        # Do nothing when not connected
        if self.channel is None:
            return

        # Do nothing with command prefix
        if msg.content.startswith('!'):
            return

        # Ignore http
        pattern = r"https*://[0-9a-zA-Z&%#./?=_-]+"
        msg.content = re.sub(pattern, "", msg.content)

        # Ignore blank
        if msg.content == "":
            return

        voice = akariVoice.generate_voice(msg.content)
        source = discord.FFmpegPCMAudio(voice)

        # Wait Akari chan until finish speaking
        while self.voice_client.is_playing():
            await asyncio.sleep(0.1)

        self.voice_client.play(source)
        print(f"[{time.strftime('%H:%M:%S')}]\t{msg.content}")

    async def _isIgnore(content: str) -> bool:
        pass

    @commands.command()
    async def akari(self, ctx: commands.Context):
        """Joins a voice channel"""

        self.channel = ctx.author.voice.channel

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(self.channel)

        self.voice_client = await self.channel.connect()

    @commands.command()
    async def bye(self, ctx: commands.Context):
        """Disconnects the bot from voice"""

        self.channel = None
        self.voice_client = None
        await ctx.voice_client.disconnect()


intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("!"),
    description='Akarichan dayo',
    intents=intents,
)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('-----------')


async def main():
    async with bot:
        await bot.add_cog(Akari(bot))
        await bot.start(private.token)

asyncio.run(main())

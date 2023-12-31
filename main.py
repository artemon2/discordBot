import discord  # Добавьте эту строку
from discord.ext import commands
from youtube_dl import YoutubeDL
from Config import token

YDL_OPTIONS = {'format': '140', 'noplaylist': 'False', 'simulate': 'True', 'key': 'FFmpegExtractAudio'}

FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}

queues = {}

intents = discord.Intents.all()
intents.message_content = True
intents.typing = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

def check_queue(guild_id):
    if queues[guild_id] != []:
        voice = bot.get_guild(guild_id).voice_client
        song = queues[guild_id].pop(0)

        with YoutubeDL(YDL_OPTIONS) as ydl:
            if 'https://youtu.be' or 'http://youtube.com' in song:
                info = ydl.extract_info(song, download=False)
            else:
                info = ydl.extract_info(f"ytsearch:{song}", download=False)['entries'][0]
        link = info['formats'][0]['url']
        source = discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link,**FFMPEG_OPTIONS)  # Создаем новый source

        voice.play(source, after=lambda x=None: check_queue(guild_id))  # Используйте только guild_id



@bot.event
async def on_ready():
    print(f"Я вернулся из Небытия!")

@bot.event
async def on_disconnect():
    print(f"Ну почему тут нету ПОМООЩИ?")

@bot.command() # если хочешь вывод текста то сделай чтобы норм выводило!
async def test(ctx, *arg):
    await ctx.send(arg)

@bot.command()
async def hello(ctx):
    await ctx.send("Пошел нахуй, " + str(ctx.author.mention))

# @bot.command(pass_context = True)
# async def play(ctx, url):
#
#     if(ctx.author.voice):
#         if ctx.guild.voice_client:
#              await ctx.guild.voice_client.move_to(ctx.author.voice.channel)
#
#         else:
#             vc = await ctx.author.voice.channel.connect()
#
#         with YoutubeDL(YDL_OPTIONS) as ydl:
#             if 'https://' in url:
#                 info = ydl.extract_info(url, download=False)
#             else:
#                 info = ydl.extract_info(f"ytsearch:{url}", download=False)['entries'][0]
#         link = info['formats'][0]['url']
#
#         source = discord.FFmpegPCMAudio(executable="ffmpeg\\ffmpeg.exe", source=link, **FFMPEG_OPTIONS)
#
#         vc.play(source, after=lambda x=None: check_queue(ctx.guild.id))  # Передаем объект source
#     else:
#         await ctx.send("Ви не в голосовому каналі, ви повинні "
#                        "зайти в голосовий канал, щоб використати цю команду!")
@bot.command(pass_context = True)
async def play(ctx, url):
    if (ctx.author.voice):

        if ctx.guild.voice_client is None:
            await ctx.author.voice.channel.connect()

        song = url
        guild_id = ctx.message.guild.id

        if guild_id in queues:
            queues[guild_id].append(song)
        else:
            queues[guild_id] = [song]

        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if len(queues) == 1 and not voice.is_playing():
            check_queue(guild_id)
        else: await ctx.send("Додано до черги.")

    else: await ctx.send("Ви не в голосовому каналі, ви повинні зайти в голосовий канал, щоб використати цю команду!")



@bot.command(pass_context = True)
async def pause(ctx):
    voice = discord.utils.get(bot.voice_clients,guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("На даний момент я не граю жодного треку.")

@bot.command(pass_context = True)
async def resume(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("На даний момент не має призупинених пісень.")

@bot.command(pass_context=True)
async def stop(ctx):
    voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    voice.stop()

@bot.command(pass_context=True)
async def leave(ctx):
    if(ctx.voice_client):
        await ctx.guild.voice_client.disconnect()
        await ctx.send("Я покинув голосовий канал")
    else:
        await ctx.send("Я не в голосовому каналі")




bot.run(token)

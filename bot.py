import asyncio
from dotenv import load_dotenv
from youtubesearchpython import VideosSearch
import discord
from discord.ext import commands
import os
import pafy
from queue import Queue
from random import randint
import urllib.request
import json
import urllib

load_dotenv('env_variables.env')

bot_id = os.getenv('bot_id')
discord_token = os.getenv('discord_token')
bot = commands.Bot(command_prefix = '!')
FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5','options': '-vn'}
NUMBER_OF_SEARCHES = 10
SONG_CHOSEN = -1
skip = False
Q = Queue()



def get_greetings():
    greetings_array = []
    greet_string = os.getenv('GREETINGS') # dotenv reads only strings
    last = 1
    for i in range(len(greet_string)):
        if greet_string[i] == ',':
            greetings_array.append(greet_string[last:i-1])
            last = i+2
    return greetings_array

GREETINGS = get_greetings()


@bot.event
async def on_message(message):
    if message.author == bot.user:
        await bot.process_commands(message)
        return
    if message.content.startswith('Hello'):
        await message.channel.send('Lovely to see you!')

    global SONG_CHOSEN
    for i in range(1, NUMBER_OF_SEARCHES+1):
        if message.content.startswith(str(i)):
            SONG_CHOSEN = i
    await bot.process_commands(message)
            

@bot.command(name = 'join', help = 'Tells the bot to join the voice channel')
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send('{} is not connected to a voice channel'.format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()
    

@bot.command(name = 'leave', help = 'Tells the bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconnect()
    else:
        await ctx.send('The bot is not connected to a voice channel')


def convert_timestamp_to_seconds(time_stamp): # primitive function to convert timestamp to seconds
    n = len(time_stamp)
    multiplier = 1
    b = True
    time = 0
    for i in range(n-1, -1, -1):
        if time_stamp[i] == ':':
            continue
        
        if b:
            time += multiplier * int(time_stamp[i])
            b = False
        else:
            time += multiplier * 10 * int(time_stamp[i])
            b = True
            multiplier *= 60
    return time

@bot.command(name = 'p', help = 'Play a song')
async def play( ctx, *, song_name):
    
    if not ctx.message.author.voice:
        await ctx.send('{} is not connected to a voice channel'.format(ctx.message.author.name))
        return
    
    try:
        await join(ctx)
    except:
        pass
    
    global Q
    if song_name[:len('https://www.youtube.com/')] == 'https://www.youtube.com/': # play video from a url
        params = {'format': 'json', 'url': song_name}
        url = 'https://www.youtube.com/oembed'
        query_string = urllib.parse.urlencode(params)
        url = url + "?" + query_string
        with urllib.request.urlopen(url) as response:
            response_text = response.read()
            data = json.loads(response_text.decode())
            title = data['title']
    else:
        vid = VideosSearch(song_name, limit = 1) # search for the video in youtube
        title = vid.result()['result'][0]['title']
    
    async with ctx.typing():
        await ctx.send(title + ' added to queue')
    voice_client = ctx.message.guild.voice_client
    Q.put(song_name)
    
    if voice_client.is_playing() or voice_client.is_paused():
        return
    
    global skip
    while not Q.empty():

        now_play = Q.get()
        if now_play[:len('https://www.youtube.com/')] == 'https://www.youtube.com/':
            song = pafy.new(now_play)
            song_duration = song.duration
            audio = song.getbestaudio()
            source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
            voice_client.play(source)
        else:
            video = VideosSearch(now_play, limit = 1)
            song_link = video.result()['result'][0]['link']
            song_duration = video.result()['result'][0]['duration']
            song = pafy.new(song_link)
            audio = song.getbestaudio()
            source = discord.FFmpegPCMAudio(audio.url, **FFMPEG_OPTIONS)
            voice_client.play(source) 
        song_duration = convert_timestamp_to_seconds(song_duration)
        t = 0

        while t <= song_duration and not skip: 
            await asyncio.sleep(1)
            if voice_client.is_playing():
                t += 1
        
        try:
            skip = False
            await voice_client.stop()
        except:
            pass
    

@bot.command(name = 'pause', help = 'Pauses the current song')
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        try: # errors popped up so used try 
            await voice_client.pause()
        except:
            pass
    else:
        await ctx.send("I'm not playing anything at the moment")

@bot.command(name = 'resume', help = 'Resumes the song')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        try: # errors popped up so used try
            await voice_client.resume()
        except:
            pass
    else:
        await ctx.sent('No song is currently paused')

@bot.command(name = 'fs', help = 'Skips the current song')
async def force_skip(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing() or voice_client.is_paused():
        global skip
        skip = True
    else:
        await ctx.send("I'm playing nothing at the moment")

@bot.command(name = 'search', help = '10 top searches to choose from')
async def search(ctx, *, song_name):
    results = VideosSearch(song_name, limit = NUMBER_OF_SEARCHES)
    results = results.result()['result']
    text = ''
    for index in range(len(results)):
        text += str(index+1) + '.'
        text += '  '
        text += results[index]['title']
        text += '\t'
        if results[index]['duration'] is not None:
            text += results[index]['duration']
        else:
            text += 'None'
        text += '\n'
    
    async with ctx.typing():
        await ctx.send(text)
    
    global SONG_CHOSEN
    SONG_CHOSEN = -1
    time = 0
    while time < 120: # time to choose the number of a song
        await asyncio.sleep(1)
        if SONG_CHOSEN != -1:
            await play(ctx, song_name = results[SONG_CHOSEN - 1]['link'])
            break
        time += 1
    SONG_CHOSEN = -1



@bot.event
async def on_voice_state_update(member, before, after):
    
    if member.id != bot.user.id:

        if not before.channel and after.channel: # greet people joining the voice channel
            try:
                await after.channel.connect()
            except:
                pass
        
            voice_client = after.channel.guild.voice_client
            if not voice_client.is_playing():
                greeting = randint(0, len(GREETINGS) - 1)
                voice_client.play(discord.FFmpegPCMAudio(executable='ffmpeg.exe', source = GREETINGS[greeting]))
                await asyncio.sleep(6) # 6 sec is enough for short greetings
    

    if before.channel is None: ## disconnect when inactive
        voice = after.channel.guild.voice_client
        time = 0
        while True:
            await asyncio.sleep(1)
            time += 1
            if voice.is_playing() and not voice.is_paused():
                time = 0
            if time == 600:
                await voice.disconnect()
            if not voice.is_connected():
                break


bot.run(discord_token)
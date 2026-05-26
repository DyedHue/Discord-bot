import random
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
from games.game2048 import game2048

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

BIRBOPOLIS_GUILD_ID = discord.Object(id = 1067041754169221150)

def help_content(category):
    embed = discord.Embed(
            color=discord.Color.blue() 
        )
        
    if category == "general":
        embed.title = "Commands"
        embed.description="`.` is the prefix and is currently unchangable"

        embed.add_field(name="grape", value="Grape someone 🥀", inline=False)
        embed.add_field(name="howgay", value="Check how gay someone is 🏳️‍🌈", inline=False)
        embed.add_field(name="mimic", value="Copy what you say", inline=False)
        embed.add_field(name="game", value="Start playing a game\n `.help game` to see available games", inline=False)

        embed.set_footer(text="More features on the way!")

    elif category == "game":
        embed.title="Commands: Game"
        embed.description="`.game {gamename}` to start a game"

        embed.add_field(name="2048", value="Play 2048!", inline=False)

    return embed

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.tree.command(name="ping", description="Replies with pong", guild =BIRBOPOLIS_GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.context_menu(name = "capitalize")
async def capitalize_text(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(f"{message.content.upper()}")

@bot.event
async def on_message(message):
    lmsg = message.content.lower()

    if message.author == bot.user: return
    
    elif lmsg.startswith(".game"):
        gamename = message.content[6:]
        if not gamename:
            await message.channel.send(embed = help_content("game"))
            return
        
        elif gamename == "tictactoe":
            pass
        elif gamename == "2048":
            gameview = game2048(player=message.author)

        else:
            await message.channel.send(gamename + " is not an available game")
            return
        
        await message.channel.send(embed=gameview.get_game_display(), view = gameview)

    elif lmsg.startswith(".grape"):
        rand = random.randint(1, 100)
        if(rand <= 20):
            ext = "was brutally graped 😢🍇"
        elif(rand <= 60):
            ext = "got graped 🍇"
        elif(rand <= 80):
            ext = "barely escaped being graped 😅"
        elif(rand <= 95):
            ext = "fled from the graper 🏃‍♂️💨"
        else:
            ext = "kicked the graper in the balls ⚽⚽"
        await message.channel.send(message.content[7:] + " " + ext)

    elif lmsg.startswith(".howgay"):
        gayrate = random.randint(0, 100)
        await message.channel.send(f"{message.content[8:]} is {gayrate}% gay " + "[`" + round(gayrate/10)*"🏳️‍🌈" + (10-round(gayrate/10))*"⬛" + "`]")

    # elif "happy birthday" in lmsg:
    #     try:
    #         await message.add_reaction('🎉')
    #     except discord.HTTPException:
    #         print("Failed to add reaction.")

    elif lmsg.startswith(".mimic"):
        await message.channel.send(message.content[7:])
    
    elif lmsg.startswith(".help"):
        category = lmsg[6:]
        if not category:
            embcontent = help_content("general")
        elif category == "game":
            embcontent = help_content("game")

        await message.channel.send(embed=embcontent)

    await bot.process_commands(message)


@bot.command()
async def hello(ctx):
    await ctx.send(f"Throughout heaven and earth, I alone am the brainrotten one!")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
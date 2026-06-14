import random
import discord
from discord.ext import commands
from discord import app_commands
import logging
from dotenv import load_dotenv
import os
from games.game2048 import game2048
from games.tictactoe import GameStartView, TicTacToeGame
from typing import Literal
import hashlib

# 1. Load configuration and token
load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='.', intents=intents, help_command=None)
BIRBOPOLIS_GUILD_ID = discord.Object(id=1067041754169221150)

# 2. Helper functions
def help_content(category):
    embed = discord.Embed(color=discord.Color.blue())
        
    if category == "general":
        embed.title = "Commands"
        embed.description = "`.` is the prefix and is currently unchangable"
        # embed.add_field(name="grape", value="Grape someone 🥀", inline=False)
        embed.add_field(name="howgay", value="Check how gay someone is 🏳️‍🌈", inline=False)
        embed.add_field(name="mimic", value="Copy what you say", inline=False)
        embed.add_field(name="game", value="Start playing a game\n `.help game` to see available games", inline=False)
        embed.set_footer(text="More features on the way!")

    elif category == "game":
        embed.title = "Commands: Game"
        embed.description = "`.game {gamename}` to start a game"
        embed.add_field(name="2048", value="Play 2048!", inline=False)
        embed.add_field(name="tictactoe", value="Play Tic-Tac-Toe against the bot!", inline=False)

    return embed

def string_to_number(input_string: str) -> int:
    string_bytes = input_string.encode('utf-8')
    hash_object = hashlib.sha256(string_bytes)
    hash_string = hash_object.hexdigest()
    return int(hash_string, 16)

game_names = Literal["2048", "tictactoe"]
# 3. Bot Events
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user: 
        return
    
    lmsg = message.content.lower()
    
    if bot.user in message.mentions:
        await message.channel.send(embed=help_content("general"))

    await bot.process_commands(message)

# 4. Slash Commands & Context Menus
@bot.tree.command(name="ping", description="Replies with pong", guild=BIRBOPOLIS_GUILD_ID)
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("pong")

@bot.tree.context_menu(name="Capitalize")
async def capitalize_text(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.send_message(f"{message.content.upper()}")

# 5. Prefix Commands
@bot.hybrid_command()
async def hello(ctx):
    await ctx.send(f"Throughout heaven and earth, I alone am the brainrotten one!")

@bot.hybrid_command()
async def howgay(ctx, arg: discord.Member):
    gayrate = string_to_number(arg.display_name) % 101
    await ctx.send(f"{arg.mention} is {gayrate}% gay " + "[`" + round(gayrate/10)*"🏳️‍🌈" + (10-round(gayrate/10))*"⬛" + "`]")

# @bot.hybrid_command()
# async def grape(ctx, arg: discord.Member):
#     rand = random.randint(1, 100)
#     if rand <= 20:
#         ext = "was brutally graped 😢🍇"
#     elif rand <= 60:
#         ext = "got graped 🍇"
#     elif rand <= 80:
#         ext = "barely escaped being graped 😅"
#     elif rand <= 95:
#         ext = "fled from the graper 🏃‍♂️💨"
#     else:
#         ext = "kicked the graper in the balls ⚽⚽"
#     await ctx.send(arg.mention + " " + ext)

@bot.hybrid_command()
async def mimic(ctx, *, arg):
    await ctx.send(arg)

@bot.hybrid_command()
async def help(ctx, category: Literal["game"] | None = None):
    if not category:
        embcontent = help_content("general")
    else:
        embcontent = help_content(category.lower())
    await ctx.send(embed=embcontent)


@bot.hybrid_command()
@app_commands.choices(name=[
    app_commands.Choice(name=game, value=game) for game in game_names.__args__
])
async def game(ctx, name: str):
    if not name:
        await ctx.send(embed=help_content("game"))
        return

    gamename = name.lower()

    if gamename == "2048":
        gameview = game2048(player=ctx.author)

    elif gamename == "tictactoe":
        start_view = GameStartView(ctx.author.id)
        setup_msg = await ctx.send("Would you like to go first (X) or second (O)?\nYou can't win either way LOL", view=start_view)
        
        await start_view.wait()
        
        if start_view.choice is None:
            await setup_msg.edit(content="Game setup timed out.", view=None)
            return
            
        bot_goes_first = start_view.choice
        await setup_msg.delete()

        # Start the interactive Tic-Tac-Toe game loop
        game_instance = TicTacToeGame(ctx, bot_goes_first)
        await game_instance.start()
        return 

    else:
        await ctx.send(gamename + " is not an available game twin 🫩✌️\n\n`.help game` _for more info_")
        return
    
    await ctx.send(embed=gameview.get_game_display(), view=gameview)

# 6. Start the bot (This must be the very last line of the file)
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
import discord
from discord.ext import commands
import asyncio

# --- BUTTON AND VIEW CLASSES FOR THE GAME GRID ---

class TicTacToeButton(discord.ui.Button):
    def __init__(self, row: int, col: int):
        # row and col are 0-based index for button grid layout (0, 1, 2)
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=row)
        self.grid_row = row + 1  # Map to 1-based coordinates for your C++ logic
        self.grid_col = col + 1

    async def callback(self, interaction: discord.Interaction):
        # Only allow the user who started the game to interact
        if interaction.user.id != self.view.player_id:
            await interaction.response.send_message("This is not your game!", ephemeral=True)
            return
        
        # Defer and send the coordinate back to the main game loop
        await self.view.process_click(interaction, self.grid_row, self.grid_col)


class TicTacToeView(discord.ui.View):
    def __init__(self, player_id: int):
        super().__init__(timeout=120.0)
        self.player_id = player_id
        self.click_event = asyncio.Event()
        self.selected_row = None
        self.selected_col = None

        # Build 3x3 grid of buttons
        for r in range(3):
            for c in range(3):
                self.add_item(TicTacToeButton(r, c))

    async def wait_for_click(self):
        self.click_event.clear()
        await self.click_event.wait()
        return self.selected_row, self.selected_col

    async def process_click(self, interaction: discord.Interaction, row: int, col: int):
        self.selected_row = row
        self.selected_col = col
        self.click_event.set()
        await interaction.response.defer()


# --- INITIAL SETUP SELECTION VIEW ---

class GameStartView(discord.ui.View):
    def __init__(self, player_id: int):
        super().__init__(timeout=60.0)
        self.player_id = player_id
        self.choice = None  # True if bot goes first, False if player goes first

    @discord.ui.button(label="Play First (X)", style=discord.ButtonStyle.primary)
    async def play_first(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("This is not your session!", ephemeral=True)
            return
        self.choice = False
        await interaction.response.defer()
        self.stop()

    @discord.ui.button(label="Play Second (O)", style=discord.ButtonStyle.primary)
    async def play_second(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.player_id:
            await interaction.response.send_message("This is not your session!", ephemeral=True)
            return
        self.choice = True
        await interaction.response.defer()
        self.stop()


# --- MAIN GAME CLASS HANDLING PORTED C++ LOGIC ---

class TicTacToeGame:
    def __init__(self, ctx, bot_first: bool):
        self.ctx = ctx
        self.bot_first = bot_first
        self.game = [[' ' for _ in range(3)] for _ in range(3)]
        self.tgame = [[' ' for _ in range(3)] for _ in range(3)]
        self.win = -1
        self.r = 0
        self.im = 0
        self.x = -1
        self.y = -1
        self.view = TicTacToeView(player_id=ctx.author.id)
        self.message = None

    def tx(self, i, j, type_val):
        perm = self.r
        if self.im == 0:
            if type_val == 1:
                perm = 4 - self.r
            if perm == 0 or perm == 4:
                return i
            elif perm == 1:
                return 4 - j
            elif perm == 2:
                return 4 - i
            else:
                return j
        else:
            if perm == 0 or perm == 4:
                return j
            elif perm == 1:
                return i
            elif perm == 2:
                return 4 - j
            else:
                return 4 - i

    def ty(self, i, j, type_val):
        perm = self.r
        if self.im == 0:
            if type_val == 1:
                perm = 4 - self.r
            if perm == 0 or perm == 4:
                return j
            elif perm == 1:
                return i
            elif perm == 2:
                return 4 - j
            else:
                return 4 - i
        else:
            if perm == 0 or perm == 4:
                return i
            elif perm == 1:
                return 4 - j
            elif perm == 2:
                return 4 - i
            else:
                return j

    def o_play(self, i, j):
        self.tgame[i-1][j-1] = 'O'
        self.game[self.tx(i, j, 1)-1][self.ty(i, j, 1)-1] = 'O'

    def x_play(self, i, j):
        self.game[i-1][j-1] = 'X'
        self.tgame[self.tx(i, j, 0)-1][self.ty(i, j, 0)-1] = 'X'

    async def o_victory(self, i, j):
        self.o_play(i, j)
        return 'O'

    async def game_draw(self, i, j):
        self.o_play(i, j)
        await self.get_player_move()
        self.x_play(self.x, self.y)
        return 0

    async def opmove(self, i, j):
        self.o_play(i, j)
        await self.get_player_move()
        self.x_play(self.x, self.y)

    # --- PORTED C++ DECISION TREE PATHS ---

    async def play1(self):
        await self.opmove(1, 3)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(3, 1)
        else:
            await self.opmove(2, 1)
            if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(2, 3)
            else:
                return await self.game_draw(3, 3)

    async def play2(self):
        await self.opmove(1, 2)
        if self.tx(self.x, self.y, 0) != 3 and self.ty(self.x, self.y, 0) != 2:
            return await self.o_victory(3, 2)
        else:
            await self.opmove(2, 1)
            if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(2, 3)
            else:
                return await self.game_draw(3, 3)

    async def play3(self):
        await self.opmove(3, 2)
        if self.tx(self.x, self.y, 0) != 1 or self.ty(self.x, self.y, 0) != 2:
            return await self.o_victory(1, 2)
        else:
            await self.opmove(1, 3)
            if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
                return await self.o_victory(3, 1)
            else:
                return await self.game_draw(2, 1)

    async def play4(self):
        await self.opmove(3, 3)
        if self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 1:
            await self.opmove(3, 1)
            if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 2:
                return await self.o_victory(3, 2)
            else:
                return await self.o_victory(1, 3)
        else:
            if self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 2:
                await self.opmove(1, 3)
                if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
                    return await self.o_victory(3, 1)
                else:
                    return await self.game_draw(2, 1)
            elif self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 3:
                await self.opmove(1, 2)
                if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 2:
                    return await self.o_victory(3, 2)
                else:
                    return await self.game_draw(3, 1)
            elif self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 1:
                await self.opmove(2, 1)
                if (self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 2) or (self.tx(self.x, self.y, 0) == 1 and self.tx(self.x, self.y, 0) == 3):
                    return await self.game_draw(1, 2)
                else:
                    return await self.game_draw(1, 3)
            else:
                await self.opmove(3, 1)
                if self.tx(self.x, self.y, 0) != 1 or self.ty(self.x, self.y, 0) != 3:
                    return await self.o_victory(1, 3)
                else:
                    return await self.game_draw(1, 2)

    async def play5(self):
        await self.opmove(1, 3)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(3, 1)
        else:
            await self.opmove(3, 3)
            if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(2, 3)
            else:
                return await self.o_victory(1, 1)

    async def play6(self):
        await self.opmove(1, 1)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 3:
            return await self.o_victory(3, 3)
        else:
            await self.opmove(3, 1)
            if self.tx(self.x, self.y, 0) != 1 or self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(1, 3)
            else:
                return await self.game_draw(2, 3)

    async def play7(self):
        await self.opmove(3, 2)
        if self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 3:
            await self.opmove(3, 1)
            if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 1:
                return await self.o_victory(2, 1)
            else:
                return await self.o_victory(3, 3)
        else:
            if self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 1:
                await self.opmove(2, 3)
                if self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 1:
                    return await self.game_draw(1, 3)
                else:
                    return await self.game_draw(3, 1)
            elif self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 3:
                await self.opmove(2, 1)
                if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
                    return await self.o_victory(3, 1)
                else:
                    return await self.game_draw(1, 3)
            elif self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 1:
                await self.opmove(1, 3)
                if self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 1:
                    return await self.game_draw(2, 3)
                else:
                    return await self.game_draw(2, 1)
            else:
                await self.opmove(2, 1)
                if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
                    return await self.o_victory(3, 1)
                else:
                    return await self.game_draw(1, 3)

    async def play8(self):
        await self.opmove(3, 1)
        if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(2, 1)
        else:
            await self.opmove(2, 3)
            if self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 2:
                return await self.game_draw(3, 2)
            else:
                return await self.game_draw(1, 2)

    async def play9(self):
        await self.opmove(2, 1)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(3, 1)
        else:
            await self.opmove(1, 3)
            if self.tx(self.x, self.y, 0) != 1 or self.ty(self.x, self.y, 0) != 2:
                return await self.o_victory(1, 2)
            else:
                return await self.game_draw(3, 2)

    async def play10(self):
        await self.opmove(1, 3)
        if self.x != 1 or self.y != 2:
            return await self.o_victory(1, 2)
        else:
            await self.opmove(3, 2)
            if self.x == 2 and self.y == 1:
                return await self.game_draw(2, 3)
            else:
                return await self.game_draw(2, 1)

    async def play11(self):
        await self.opmove(1, 3)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(3, 1)
        else:
            await self.opmove(3, 3)
            if self.tx(self.x, self.y, 0) != 2 and self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(2, 3)
            else:
                return await self.o_victory(1, 1)

    async def play12(self):
        await self.opmove(1, 3)
        if self.tx(self.x, self.y, 0) != 3 or self.ty(self.x, self.y, 0) != 1:
            return await self.o_victory(3, 1)
        else:
            await self.opmove(2, 1)
            if self.tx(self.x, self.y, 0) != 2 or self.ty(self.x, self.y, 0) != 3:
                return await self.o_victory(2, 3)
            else:
                await self.opmove(3, 2)
                if self.tx(self.x, self.y, 0) != 1 or self.ty(self.x, self.y, 0) != 2:
                    return await self.o_victory(1, 2)
                else:
                    self.o_play(3, 3)
                    return 0

    # --- DRIVER LOGIC AND INTERACTIVE RETRIEVAL ---

    async def get_player_move(self):
        self.update_buttons()
        await self.message.edit(content="It is your turn! Place an 'X'", view=self.view)
        
        # Wait for the player to press a grid button
        self.x, self.y = await self.view.wait_for_click()

    def update_buttons(self):
        # Update the button visual styles and labels to represent the current board state
        for child in self.view.children:
            if isinstance(child, TicTacToeButton):
                r_idx = child.grid_row - 1
                c_idx = child.grid_col - 1
                cell_val = self.game[r_idx][c_idx]

                if cell_val == 'O':
                    child.label = 'O'
                    child.style = discord.ButtonStyle.danger
                    child.disabled = True
                elif cell_val == 'X':
                    child.label = 'X'
                    child.style = discord.ButtonStyle.success
                    child.disabled = True
                else:
                    child.label = "\u200b"
                    child.style = discord.ButtonStyle.secondary
                    child.disabled = False

    async def start(self):
        # Send initial board
        self.message = await self.ctx.send("Tic Tac Toe Match Initializing...", view=self.view)
        
        try:
            if self.bot_first:  # Case 1 (C++ equivalent)
                self.o_play(2, 2)
                await self.get_player_move()
                
                if ((self.x == 1 or self.x == 3) and self.y == 2) or (self.x == 2 and (self.y == 1 or self.y == 3)):
                    if self.x == 2 and self.y == 3:
                        self.r = 1
                    elif self.x == 3 and self.y == 2:
                        self.r = 2
                    elif self.x == 2 and self.y == 1:
                        self.r = 3
                    self.x_play(self.x, self.y)
                    self.win = await self.play11()
                else:
                    if self.x == 1 and self.y == 3:
                        self.r = 1
                    elif self.x == 3 and self.y == 3:
                        self.r = 2
                    elif self.x == 3 and self.y == 1:
                        self.r = 3
                    self.x_play(self.x, self.y)
                    self.win = await self.play12()
            else:  # Case 2 (C++ equivalent)
                await self.get_player_move()
                
                if self.x != 2 or self.y != 2:
                    if (self.x == 1 or self.x == 3) and (self.y == 1 or self.y == 3):
                        if self.x == 1 and self.y == 3:
                            self.r = 1
                        elif self.x == 3 and self.y == 3:
                            self.r = 2
                        elif self.x == 3 and self.y == 1:
                            self.r = 3
                        self.x_play(self.x, self.y)
                        self.game[1][1] = 'O'
                        self.tgame[1][1] = 'O'
                        await self.get_player_move()

                        if self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 2:
                            self.x_play(self.x, self.y)
                            self.win = await self.play1()
                        elif self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 1:
                            self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play1()
                        elif (self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 3) or (self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 1):
                            if self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 1:
                                self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play2()
                        elif self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 3:
                            self.x_play(self.x, self.y)
                            self.win = await self.play3()
                        elif (self.tx(self.x, self.y, 0) == 2 and self.ty(self.x, self.y, 0) == 3) or (self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 2):
                            if self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 2:
                                self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play4()

                    elif ((self.x == 1 or self.x == 3) and self.y == 2) or (self.x == 2 and (self.y == 1 or self.y == 3)):
                        if self.x == 2 and self.y == 3:
                            self.r = 1
                        elif self.x == 3 and self.y == 2:
                            self.r = 2
                        elif self.x == 2 and self.y == 1:
                            self.r = 3
                        self.x_play(self.x, self.y)
                        self.game[1][1] = 'O'
                        self.tgame[1][1] = 'O'
                        await self.get_player_move()

                        if (self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 1) or (self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 3):
                            if self.tx(self.x, self.y, 0) == 1 and self.ty(self.x, self.y, 0) == 3:
                                self.r += 1
                                self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play1()
                        elif self.tx(self.x, self.y, 0) == 3 and (self.ty(self.x, self.y, 0) == 1 or self.ty(self.x, self.y, 0) == 3):
                            if self.ty(self.x, self.y, 0) == 1:
                                self.r += 3
                            else:
                                self.r += 2
                                self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play4()
                        elif self.tx(self.x, self.y, 0) == 3 and self.ty(self.x, self.y, 0) == 2:
                            self.x_play(self.x, self.y)
                            self.win = await self.play5()
                        elif self.tx(self.x, self.y, 0) == 2 and (self.ty(self.x, self.y, 0) == 1 or self.ty(self.x, self.y, 0) == 3):
                            if self.ty(self.x, self.y, 0) == 3:
                                self.im = 1
                            self.x_play(self.x, self.y)
                            self.win = await self.play6()
                else:
                    self.x_play(self.x, self.y)
                    self.game[0][0] = 'O'
                    self.tgame[0][0] = 'O'
                    await self.get_player_move()

                    if (self.x == 1 and self.y == 2) or (self.x == 2 and self.y == 1):
                        if self.x == 2 and self.y == 1:
                            self.im = 1
                        self.x_play(self.x, self.y)
                        self.win = await self.play7()
                    elif (self.x == 1 and self.y == 3) or (self.x == 3 and self.y == 1):
                        if self.x == 3 and self.y == 1:
                            self.im = 1
                        self.x_play(self.x, self.y)
                        self.win = await self.play8()
                    elif (self.x == 2 and self.y == 3) or (self.x == 3 and self.y == 2):
                        if self.x == 3 and self.y == 2:
                            self.im = 1
                        self.x_play(self.x, self.y)
                        self.win = await self.play9()
                    else:
                        self.x_play(self.x, self.y)
                        self.win = await self.play10()

            await self.finish_game()
        except asyncio.TimeoutError:
            await self.handle_timeout()

    async def finish_game(self):
        # Disable all buttons and show final board with result
        for child in self.view.children:
            if isinstance(child, TicTacToeButton):
                r_idx = child.grid_row - 1
                c_idx = child.grid_col - 1
                cell_val = self.game[r_idx][c_idx]
                if cell_val == 'O':
                    child.label = 'O'
                    child.style = discord.ButtonStyle.danger
                elif cell_val == 'X':
                    child.label = 'X'
                    child.style = discord.ButtonStyle.success
                else:
                    child.label = "\u200b"
                    child.style = discord.ButtonStyle.secondary
                child.disabled = True

        if self.win == 0:
            result_msg = "🤝 Game Drawn!"
        else:
            result_msg = "💀 You Lost!"
        
        await self.message.edit(content=result_msg, view=self.view)
        self.view.stop()

    async def handle_timeout(self):
        for child in self.view.children:
            child.disabled = True
        await self.message.edit(content="⏱️ Match expired due to inactivity.", view=self.view)
        self.view.stop()


# --- COG WRAPPER ---

class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="tictactoe", aliases=["ttt"])
    async def tictactoe_command(self, ctx):
        """Starts a Tic Tac Toe game against the bot."""
        start_view = GameStartView(ctx.author.id)
        setup_msg = await ctx.send("Would you like to go first or second?", view=start_view)
        
        # Wait up to 60 seconds for choice
        await start_view.wait()
        
        if start_view.choice is None:
            await setup_msg.edit(content="Setup timed out.", view=None)
            return

        bot_goes_first = start_view.choice
        await setup_msg.delete()

        # Run main game loop
        game = TicTacToeGame(ctx, bot_goes_first)
        await game.start()


async def setup(bot):
    await bot.add_cog(TicTacToe(bot))
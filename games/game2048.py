import copy
import random
import discord

class game2048(discord.ui.View):
    def __init__(self, player: discord.User):
        super().__init__(timeout=60) # Buttons will disable automatically after 60 seconds
        self.player = player
        self.n = [[0, 0, 0, 0] for _ in range(4)]
        self.m = [[0, 0, 0, 0] for _ in range(4)]
        self.score = 0
        self.store = 0
        self.ht = 0
        self.turn = 1
        self.is_gameover = False

        self.spawn()
        self.pfpurl = self.player.display_avatar.url
        self.player_name = self.player.display_name

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.player:
            return False
        return True
    
    def get_game_display(self):
        frame = "```\n"
        frame += "_________________________\n"
        frame += "|     |     |     |     |\n"
        for i in range(4):
            for j in range(4):
                if j == 0: frame += "|"

                if self.n[i][j] == 0: frame += "     |"
                elif self.n[i][j] < 10:    frame += "  " + str(self.n[i][j]) + "  |"
                elif self.n[i][j] < 100:   frame += "  " + str(self.n[i][j]) + " |"
                elif self.n[i][j] < 1000:  frame += " " + str(self.n[i][j]) + " |"
                elif self.n[i][j] < 10000: frame += " " + str(self.n[i][j]) + "|"
                elif self.n[i][j] < 100000:frame += str(self.n[i][j]) + "|"
            frame += "\n|_____|_____|_____|_____|"

            if i != 3: frame += "\n|     |     |     |     |\n"
 
        frame += "```"

        embed = discord.Embed(
            title="🎮 2048 Game",
            description=frame,
            color=discord.Color.blue()
        )

        embed.set_author(
            name=f"{self.player_name}'s Session",
            icon_url=self.pfpurl
        )

        embed.add_field(name="Current Score", value=f"🏆 {self.score}", inline=True)
        embed.add_field(name="Highest Tile" + "⠀"*10, value=f"⭐ {self.ht}", inline=True)
        
        if self.is_gameover:
            embed.set_footer(text = "💀 Game Over! (Try to undo)")

        return embed

    def isSpace(self):
        for i in range(4):
            for j in range(4):
                if self.n[i][j] == 0:
                    return True
                    
        return False

    def gameover(self):
        for j in range(3):
            for i in range(3):
                if self.n[i][j] == self.n[i + 1][j] or self.n[i][j] == self.n[i][j + 1]: return 0

        for j in range(3):
            if self.n[3][j] == self.n[3][j + 1]: return 0

        for i in range(3):
            if self.n[i][3] == self.n[i + 1][3]: return 0

        return 1
    
    def make_move_and_spawn(self, c):
        self.store = 0
        newN = copy.deepcopy(self.n)
        locked = [[0, 0, 0, 0] for _ in range(4)]

        for i in range(4):
            for j in range(1, 4):
                ii = i; idir = 0; jj = j; jdir = 0
                if   c == 'u': jj = i; ii = j;   idir = -1
                elif c == 'd': jj = i; ii = 3-j; idir = 1
                elif c == 'l':           jdir = -1
                elif c == 'r': jj = 3-j; jdir = 1

                cnt = 0
                while cnt < j:
                    if newN[ii][jj] != 0 and newN[ii+ idir][jj + jdir] == 0:
                        newN[ii+ idir][jj + jdir] = newN[ii][jj]
                        newN[ii][jj] = 0
                    elif newN[ii][jj] == newN[ii + idir][jj + jdir] and newN[ii][jj] != 0 and locked[ii + idir][jj + jdir] + locked[ii][jj] == 0:
                        newN[ii+ idir][jj + jdir] += newN[ii][jj]
                        self.score += newN[ii + idir][jj + jdir]
                        self.store += newN[ii + idir][jj + jdir]
                        newN[ii][jj] = 0
                        locked[ii + idir][jj + jdir] = 1
                        if newN[ii + idir][jj + jdir] > self.ht: self.ht = newN[ii + idir][jj + jdir]
                    else:
                        break

                    cnt += 1
                    ii += idir
                    jj += jdir
        if self.n != newN:
            self.m = copy.deepcopy(self.n)
            self.n = copy.deepcopy(newN)
            self.spawn()

    def undo(self):
        self.score -= self.store
        self.n = copy.deepcopy(self.m)
    
    def spawn(self):
        num = 2 if random.random() < 0.9 else 4
        if self.turn == 1: self.ht = num; self.score = num

        b = 0
        c = 0
        x = 0

        for i in range(4):
            for j in range(4):
                if self.n[i][j] == 0: x+=1

        b = random.randint(1, x)

        for i in range(4):
            for j in range(4):
                if self.n[i][j] == 0:
                    c+=1
                    if b == c:
                        self.n[i][j] = num
                        break

    def play(self, arrow):
        if arrow != 'c': self.make_move_and_spawn(arrow);
        else: self.undo()
        self.turn = 0

        if(not self.isSpace() and self.gameover()):
            self.is_gameover = True

    @discord.ui.button(label="↩️", style=discord.ButtonStyle.success, row = 0)
    async def undo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.play('c')
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.success, row = 0)
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('u')
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)


    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.success, row = 1)
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('l')
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.success, row = 1)
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('d')
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.success, row = 1)
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('r')
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

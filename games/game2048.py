import random
import discord

class game2048(discord.ui.View):
    def __init__(self, player: discord.User):
        super().__init__(timeout=60) # Buttons will disable automatically after 60 seconds
        self.player = player
        self.n = [[0, 0, 0, 0] for _ in range(4)]
        self.m = [
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [0, 0, 0, 1]
        ]
        self.a = 0
        self.score = 0
        self.store = 0
        self.ht = 0
        self.arrow = ''
        self.moved = -1
        self.turn = 1
        self.is_gameover = False
        self.update()
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

    def comp(self, s="equal"):
        for i in range(4):
            for j in range(4):
                if (s == "equal" and self.m[i][j] != self.n[i][j]) or (s == "space" and self.n[i][j] == 0):
                    return True
                    
        return False
    
    def _pass(self):
        for i in range(4):
            for j in range(4):
                self.m[i][j] = self.n[i][j]

    def gameover(self):
        for j in range(3):
            for i in range(3):
                if self.n[i][j] == self.n[i + 1][j] or self.n[i][j] == self.n[i][j + 1]: return 1

        for j in range(3):
            if self.n[3][j] == self.n[3][j + 1]: return 1

        for i in range(3):
            if self.n[i][3] == self.n[i + 1][3]: return 1

        return 0
    
    def move(self, c):
        for _ in range(3):
            for j in range(4):
                for i in range(1, 4):
                    if c == 'u' and self.n[i][j] != 0 and self.n[i - 1][j] == 0:
                        self.moved = 1
                        self.n[i - 1][j] = self.n[i][j]
                        self.n[i][j] = 0

                    elif c == 'd' and self.n[4 - i][j] == 0 and self.n[4 - i - 1][j] != 0:
                        self.moved = 1
                        self.n[4 - i][j] = self.n[4 - i - 1][j]
                        self.n[4 - i - 1][j] = 0

                    elif c == 'l' and self.n[j][3 - (i - 1)] != 0 and self.n[j][3 - (i - 1) - 1] == 0:
                        self.moved = 1
                        self.n[j][3 - (i - 1) - 1] = self.n[j][3 - (i - 1)]
                        self.n[j][3 - (i - 1)] = 0

                    elif c == 'r' and self.n[j][i - 1] != 0 and self.n[j][i] == 0:
                        self.moved = 1
                        self.n[j][i] = self.n[j][i - 1]
                        self.n[j][i - 1] = 0
    
    def merge(self, c):
        for j in range(4):
            for i in range(3):
                if c == 'u' and self.n[i][j] == self.n[i + 1][j]:
                    self.moved = 1
                    self.n[i][j] += self.n[i + 1][j]
                    self.score += self.n[i][j]
                    self.store += self.n[i][j]

                    if self.n[i][j] > self.ht:
                        self.ht = self.n[i][j]

                    self.n[i + 1][j] = 0

                elif c == 'd' and self.n[4 - (i + 1)][j] == self.n[4 - (i + 1) - 1][j]:
                    self.moved = 1
                    self.n[4 - (i + 1)][j] += self.n[4 - (i + 1) - 1][j]
                    self.score += self.n[4 - (i + 1)][j]
                    self.store += self.n[4 - (i + 1)][j]

                    if self.n[4 - (i + 1)][j] > self.ht:
                        self.ht = self.n[4 - (i + 1)][j]

                    self.n[4 - (i + 1) - 1][j] = 0

                elif c == 'l' and self.n[j][i] == self.n[j][i + 1]:
                    self.moved = 1
                    self.n[j][i] += self.n[j][i + 1]
                    self.score += self.n[j][i]
                    self.store += self.n[j][i]
                    
                    if self.n[j][i] > self.ht:
                        self.ht = self.n[j][i]
                        
                    self.n[j][i + 1] = 0

                elif c == 'r' and self.n[j][3 - i] == self.n[j][3 - i - 1]:
                    self.moved = 1
                    self.n[j][3 - i] += self.n[j][3 - i - 1]
                    self.score += self.n[j][3 - i]
                    self.store += self.n[j][3 - i]

                    if self.n[j][3 - i] > self.ht:
                        self.ht = self.n[j][3 - i]

                    self.n[j][3 - i - 1] = 0

    def undo(self):
        self.score -= self.store
        for i in range(4):
            for j in range(4):
                self.n[i][j] = self.m[i][j]
    
    def spawn(self, num):
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

    def update(self):
        if self.comp() == 1:
            a = 2
            if random.randint(1, 10) == 1:
                a += 2

            self.spawn(a)
            
            self.is_gameover = False
            if self.comp("space") == 0 and self.gameover() == 0:
                self.is_gameover = True

    def play(self, arrow):
        if arrow != 'c':
            self._pass()
            self.store = 0
            self.move(arrow)
            self.merge(arrow)
            self.move(arrow)

        else:
            if self.turn != 1:
                self.undo()
            else:
                self._pass()
        
        self.turn = 0
        self.moved = 0

    @discord.ui.button(label="↩️", style=discord.ButtonStyle.success, row = 0)
    async def undo_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.play('c')
        self.update()
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="⬆️", style=discord.ButtonStyle.success, row = 0)
    async def up_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('u')
        self.update()
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)


    @discord.ui.button(label="⬅️", style=discord.ButtonStyle.success, row = 1)
    async def left_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('l')
        self.update()
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="⬇️", style=discord.ButtonStyle.success, row = 1)
    async def down_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('d')
        self.update()
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

    @discord.ui.button(label="➡️", style=discord.ButtonStyle.success, row = 1)
    async def right_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.is_gameover: return
        self.play('r')
        self.update()
        await interaction.response.edit_message(embed=self.get_game_display(), view=self)

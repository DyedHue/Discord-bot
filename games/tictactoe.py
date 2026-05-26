import discord

class TicTacToeButton(discord.ui.Button):
    def __init__(self, index: int, row: int):
        # Initial state: empty label, gray button color (Secondary)
        super().__init__(style=discord.ButtonStyle.secondary, label=" ", row=row)
        self.index = index

    

class tictactoe(discord.ui.View):
    def __init__(self, player: discord.User):
        super().__init__(timeout=60) # Buttons will disable automatically after 60 seconds
        self.player = player
        self.game = [[' ', ' ',' ', ' '] for _ in range(3)]
        self.tgame = self.game
        self.win = -1
        self.movecnt = 0
        self.x = -1
        self.y = -1
        self.r = 0
        self.im = 0
        self.opt = -1

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.player:
            return False
        return True
    
    def get_game_display(self, s):
        v = '│'
        h = '─'
        c = '┼'

        board = self.game[0][0] + v + self.game[0][1] + v + self.game[0][2] + "\n"
        board += h + c + h + c + h + "\n"
        board += self.game[1][0] + v + self.game[1][1] + v + self.game[1][2] + "\n"
        board += h + c + h + c + h + "\n"
        board += self.game[2][0] + v + self.game[2][1] + v + self.game[2][2] + "\n"

        return board
    
    def setgame(self):
        self.r=0
        self.im=0;
        for i in range(3):
            for j in range(3):
                self.game[i][j]=' '
                self.tgame[i][j]=' '
        # title();
    
    def refresh():
        pass
    # {
    #     system("CLS");
    #     title();
    #     board();
    #     cout<<"\nEnter Coordinates: ";
    #     cin>>x>>y;
    #     if(x>3 || x<1 || y>3 || y<1 || game[x-1][y-1]!=' ' )
    #     {
    #         refresh();
    #     }
    # }

    def tx(self, i, j, type):
        perm=self.r;
        if self.im==0:
            if type==1:
                perm=4-self.r;
            if perm==0 or perm==4:
                return i;
            elif perm==1:
                return 4-j;
            elif perm==2:
                return 4-i;
            else: return j;
        
        else:
            if perm==0 or perm==4:
                return j;
            elif perm==1:
                return i;
            elif perm==2:
                return 4-j;
            else: return 4-i;

    def ty(self, i, j, type):
        perm=self.r
        if self.im==0:
            if type==1:
                perm=4-self.r
            
            if perm==0 or perm==4:
                return j
            elif perm==1:	
                return i
            elif perm==2:
                return	4-j
            else: return 4-i	

        else:
            if perm==0 or perm==4:
                return i
            elif(perm==1):
                return 4-j
            elif(perm==2):
                return 4-i
            else: return j

    def Oplay(self, i, j):
        self.tgame[i-1][j-1]='O'
        self.game[self.tx(i, j, 1)-1][self.ty(i,j,1)-1]='O'

    def Xplay(self, i, j):
        self.game[i-1][j-1]='X'
        self.tgame[self.tx(i,j,0)-1][self.ty(i,j,0)-1]='X'

    def Ovictory(self, i, j):
        self.Oplay(i,j)
        # system("CLS")
        # board()
        return 'O'

    def gamedraw(self, i, j):
        self.Oplay(i,j)
        # self.refresh()
        self.Xplay(self.x,self.y)
        # system("CLS")
        # board()
        return 0

    def opmove(self, i, j):
        self.Oplay(i,j)
        # self.refresh()
        self.Xplay(self.x,self.y)

    def play1(self):
        self.opmove(1,3)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(3,1)
        else:
            self.opmove(2,1)
            if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(2, 3)
            else:
                return self.gamedraw(3,3)
        
    def play2(self):
        self.opmove(1,2)
        if(self.tx(self.x,self.y,0)!=3 and self.ty(self.x,self.y,0)!=2):
            return self.Ovictory(3,2)
        else:
            self.opmove(2,1)
            if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(2,3)
            else:
                return self.gamedraw(3,3)
        
    def play3(self):
        self.opmove(3,2)
        if(self.tx(self.x,self.y,0)!=1 or self.ty(self.x,self.y,0)!=2):
            return self.Ovictory(1,2)
        else:
            self.opmove(1,3)
            if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
                return self.Ovictory(3,1)
            else:
                return self.gamedraw(2,1)
            
    def play4(self):
        self.opmove(3,3)
        if(self.tx(self.x,self.y,0)==2 and self.ty(self.x,self.y,0)==1):
            self.opmove(3,1)
            if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=2):
                return self.Ovictory(3,2)
            else: return self.Ovictory(1,3)
        
        else:
            if(self.tx(self.x,self.y,0)==1 and self.ty(self.x,self.y,0)==2):
                self.opmove(1,3)
                if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
                    return self.Ovictory(3,1)
                else: return self.gamedraw(2,1)
            
            elif(self.tx(self.x,self.y,0)==1 and self.ty(self.x,self.y,0)==3):
                self.opmove(1,2)
                if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=2):
                    return self.Ovictory(3,2)
                else: return self.gamedraw(3,1)
            
            elif(self.tx(self.x,self.y,0)==3 and self.ty(self.x,self.y,0)==1):
                self.opmove(2,1)
                if((self.tx(self.x,self.y,0)==3 and self.ty(self.x,self.y,0)==2) or (self.tx(self.x,self.y,0)==1 and self.tx(self.x,self.y,0)==3)):
                    return self.gamedraw(1,2)
                else: return self.gamedraw(1,3)
            
            else:
                self.opmove(3,1)
                if(self.tx(self.x,self.y,0)!=1 or self.ty(self.x,self.y,0)!=3):
                    return self.Ovictory(1,3)
                else: return self.gamedraw(1,2)

    def play5(self):
        self.opmove(1,3)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(3,1)
        else:
            self.opmove(3,3)
            if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(2,3)
            else: return self.Ovictory(1,1)

    def play6(self):
        self.opmove(1,1)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=3):
            return self.Ovictory(3,3)
        else:
            self.opmove(3,1)
            if(self.tx(self.x,self.y,0)!=1 or self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(1,3)
            else: return self.gamedraw(2,3)

    def play7(self):
        self.opmove(3,2)
        if(self.tx(self.x,self.y,0)==1 and self.ty(self.x,self.y,0)==3):
            self.opmove(3,1)
            if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=1):
                return self.Ovictory(2,1)
            else: return self.Ovictory(3,3)
        
        else:
            if(self.tx(self.x,self.y,0)==2 and self.ty(self.x,self.y,0)==1):
            
                self.opmove(2,3)
                if(self.tx(self.x,self.y,0)==3 and self.ty(self.x,self.y,0)==1):
                    return self.gamedraw(1,3)
                else: return self.gamedraw(3,1)
            
            elif(self.tx(self.x,self.y,0)==2 and self.ty(self.x,self.y,0)==3):
            
                self.opmove(2,1)
                if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
                    return self.Ovictory(3,1)
                else: return self.gamedraw(1,3)
            
            elif(self.tx(self.x,self.y,0)==3 and self.ty(self.x,self.y,0)==1):
            
                self.opmove(1,3)
                if(self.tx(self.x,self.y,0)==2 and self.ty(self.x,self.y,0)==1):
                    return self.gamedraw(2,3)
                else: return self.gamedraw(2,1)
            
            else:
                self.opmove(2,1)
                if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
                    return self.Ovictory(3,1)
                else: return self.gamedraw(1,3)
		
	

    def play8(self):
        self.opmove(3,1)
        if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(2,1)
        else:
            self.opmove(2,3)
            if(self.tx(self.x,self.y,0)==1 and self.ty(self.x,self.y,0)==2):
                return self.gamedraw(3,2)
            else: return self.gamedraw(1,2)
        

    def play9(self):
        self.opmove(2,1)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(3,1)
        else:
            self.opmove(1,3)
            if(self.tx(self.x,self.y,0)!=1 or self.ty(self.x,self.y,0)!=2):
                return self.Ovictory(1,2)
            else: return self.gamedraw(3,2)
        

    def play10(self):
        self.opmove(1,3)
        if(self.x!=1 or self.y!=2):
            return self.Ovictory(1,2)
        else:
            self.opmove(3,2)
            if(self.x==2 and self.y==1):
                return self.gamedraw(2,3)
            else: return self.gamedraw(2,1)
        

    def play11(self):
        self.opmove(1,3)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(3,1)
        else :
            self.opmove(3,3)
            if(self.tx(self.x,self.y,0)!=2 and self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(2,3)
            else: return self.Ovictory(1,1)
        

    def play12(self):
        self.opmove(1,3)
        if(self.tx(self.x,self.y,0)!=3 or self.ty(self.x,self.y,0)!=1):
            return self.Ovictory(3,1)
        else:
            self.opmove(2,1)
            if(self.tx(self.x,self.y,0)!=2 or self.ty(self.x,self.y,0)!=3):
                return self.Ovictory(2,3)
            else:
                self.opmove(3,2)
                if(self.tx(self.x,self.y,0)!=1 or self.ty(self.x,self.y,0)!=2):
                    return self.Ovictory(1,2)
                else:
                    self.Oplay(3,3)
                    return 0
                
    # int main()

	# win=-1,movecnt=0,x=-1,y=-1
	# title()
	# while(opt==-1)
	
	# 	cout<<"1. Play first\n2. Play second\n"
	# 	cout<<"Choose option: "
	# 	cin>>opt
	# 	setgame()
	
	# switch(opt)
	
	# 	case 1:
	# 		Oplay(2,2)
	# 		refresh()
	# 		if(((x==1 or x==3) and y==2) or (x==2 and (y==1 or y==3)))
			
	# 			if(x==2 and y==3)
	# 				r=1
	# 			elif(x==3 and y==2)
	# 				r=2
	# 			elif(x==2 and y==1)
	# 				r=3
	# 			Xplay(x,y)
	# 			win=play11()
			
	# 		else
			
	# 			if(x==1 and y==3)
	# 				r=1
	# 			elif(x==3 and y==3)
	# 				r=2
	# 			elif(x==3 and y==1)
	# 				r=3
	# 			Xplay(x,y)
	# 			win=play12()
			
	# 		break
	# 	case 2:
	# 		refresh()
	# 		if(x!=2 or y!=2)
			
	# 			if((x==1 or x==3) and (y==1 or y==3))
				
	# 				if(x==1 and y==3)
	# 					r=1
	# 				elif(x==3 and y==3)
	# 					r=2
	# 				elif(x==3 and y==1)
	# 					r=3
	# 				Xplay(x,y)
	# 				game[1][1]='O',tgame[1][1]='O'
	# 				refresh()
	# 				if(tx(x,y,0)==1 and ty(x,y,0)==2)
					
	# 					Xplay(x,y)
	# 					win=play1()
					
	# 				elif(tx(x,y,0)==2 and ty(x,y,0)==1)
					
	# 					im=1
	# 					Xplay(x,y)
	# 					win=play1()
					
	# 				elif((tx(x,y,0)==1 and ty(x,y,0)==3) or (tx(x,y,0)==3 and ty(x,y,0)==1))
					
	# 					if((tx(x,y,0)==3 and ty(x,y,0)==1))
	# 						im=1
	# 					Xplay(x,y)
	# 					win=play2()
					
	# 				elif((tx(x,y,0)==3 and ty(x,y,0)==3))
					
	# 					Xplay(x,y)
	# 					win=play3()
					
	# 				elif((tx(x,y,0)==2 and ty(x,y,0)==3) or (tx(x,y,0)==3 and ty(x,y,0)==2))
					
	# 					if((tx(x,y,0)==3 and ty(x,y,0)==2))
	# 						im=1
	# 					Xplay(x,y)
	# 					win=play4()
					
				
	# 			elif(((x==1 or x==3) and y==2) or (x==2 and (y==1 or y==3)))
				
	# 				if(x==2 and y==3)
	# 					r=1
	# 				elif(x==3 and y==2)
	# 					r=2
	# 				elif(x==2  and y==1)
	# 					r=3
	# 				Xplay(x,y)
	# 				game[1][1]='O',tgame[1][1]='O'
	# 				refresh()
	# 				if((tx(x,y,0)==1 and ty(x,y,0)==1) or ((tx(x,y,0)==1 and ty(x,y,0)==3)))
					
	# 					if((tx(x,y,0)==1 and ty(x,y,0)==3))
						
	# 						r++
	# 						im=1
						
	# 					Xplay(x,y)
	# 					win=play1()
					
	# 				elif(tx(x,y,0)==3 and (ty(x,y,0)==1 or ty(x,y,0)==3))
					
	# 					if(ty(x,y,0)==1)
	# 						r+=3
	# 					else 
						
	# 						r+=2
	# 						im=1	
						
	# 					Xplay(x,y)
	# 					win=play4()
					
	# 				elif(tx(x,y,0)==3 and ty(x,y,0)==2)
					
	# 					Xplay(x,y)
	# 					win=play5()
					
	# 				elif(tx(x,y,0)==2 and (ty(x,y,0)==1 or ty(x,y,0)==3))
					
	# 					if(ty(x,y,0)==3)
	# 						im=1
	# 					Xplay(x,y)
	# 					win=play6()
					
				
			
	# 		else
			
	# 			Xplay(x,y)
	# 			game[0][0]='O',tgame[0][0]='O'
	# 			refresh()
	# 			if(x==1 and y==2 or (x==2 and y==1))
				
	# 				if(x==2 and y==1)
	# 					im=1
	# 				Xplay(x,y)
	# 				win=play7()
				
	# 			elif(x==1 and y==3 or (x==3 and y==1 ))
				
	# 				if(x==3 and y==1 )
	# 					im=1
	# 				Xplay(x,y)
	# 				win=play8()
				
	# 			elif(x==2 and y==3 or (x==3 and y==2))
				
	# 				if(x==3 and y==2)
	# 					im=1
	# 				Xplay(x,y)
	# 				win=play9()
				
	# 			else
				
	# 				Xplay(x,y)
	# 				win=play10()
					
			
	# 		break
	
	# system("CLS")
	# title()
	# board()
	# if(win==0)
	
	# 	cout<<"GAME DRAWN\n"
	
	# else cout<<"YOU LOST\n"	
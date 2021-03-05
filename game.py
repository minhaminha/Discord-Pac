import numpy as np
import discord
from level import Basic, Emojis, Extra
from chara import Character

class Game:

    def __init__(self, highscore=0):
        self.grid = Basic.copy()
        self.emojigrid = []
        self.gameview = []
        self.score = 0
        self.lives = 3

        row = []
        display = []

        for x in Basic:
            for y in x:
                row.append(Emojis[y])
            self.emojigrid.append(row)
            self.gameview.append(''.join(row)+'\n')
            row = []

        sections = [[0,7],[8,15],[16,23],[24,30]]
        for x in sections:
            display.append(''.join(self.gameview[x[0]:x[1]]))

        self.game = discord.Embed(title="Lives:3")
        self.game.add_field(name="PAC-MAN: Discord", value=display[0], inline=False)
        self.game.add_field(name=self.gameview[7], value=display[1], inline=False)
        self.game.add_field(name=self.gameview[15], value=display[2], inline=False)
        self.game.add_field(name=self.gameview[23], value=display[3], inline=False)
        self.game.add_field(name=f"Score: 0, High score: {highscore}", value="Next Moves:", inline=False)

        self.Pac = Character("pac", Extra[0], [23,13], "\U000025B6", "begin")
        #starts going right immediately
        
        ghost = Character(3, Extra[3], [14,11], "\U0001F53C", "random", [1,1], 0, 12)
        alien = Character(4, Extra[4], [14,12], "\U0001F53C", "random", [1,25], 3, 9)
        invader = Character(5, Extra[5], [14, 14], "\U0001F53C", "random",[29,1], 7, 5)
        robot = Character(6, Extra[6], [14,15], "\U0001F53C", "random", [29,25], 10, 2)

        self.Ghosts = [ghost, alien, invader, robot]

    def __del__(self):
        print("Current game destroyed")

    def Pacmove(self, char, direction):

        x = char.coord[1] #column
        y = char.coord[0] #row

        w = self.grid[y-1, x]
        a = self.grid[y, x-1]
        s = self.grid[y+1, x]
        d = self.grid[y, x+1]

        coords = [w,a,s,d]

        dirchange = False
        again = [False, 0, False, char.state]

        #dont change movespeed
        #BUT interesting: ghosts apparently stop at corners before moving on
        
        if char.direction != direction:
            result = self.directionCheck(direction, coords, char)
            if result[0]:
                dirchange = True
                again = self.PacgameCheck(coords[result[1]])
        if char.direction == direction or result[0] == False:
            result = self.directionCheck(char.direction, coords, char)
            if result[0]:
                again = self.PacgameCheck(coords[result[1]])
    
        return [dirchange, again[0], again[1], again[2], again[3]]

    #change to a loop?
    def directionCheck(self, direction, coords, chara):
        if direction == Extra[15] and coords[0] != 1: #w
            chara.coord[0] -= 1
            return [True, 0]
        elif direction == Extra[14] and coords[1] != 1: #a
            chara.coord[1] -= 1
            return [True, 1] 
        elif direction == Extra[16] and coords[2] != 1: #s
            chara.coord[0] += 1
            return [True, 2]
        elif direction == Extra[13] and coords[3] != 1: #d
            chara.coord[1] += 1
            return [True, 3]
        return [False, 0]

    def PacgameCheck(self, coord):
        ate = False
        score = 0
        statechange = False
        state = ""
        x = self.Pac.coord[1]
        
        if coord == 0:
            ate = True
            score = 5
        elif coord == 2: #fruit collision
            ate = True
            score = 200
            #SOMETHING TO INDICATE FRUIT NEEDS TO DIE
        elif coord == 4:
            if x > 10:
                self.Pac.coord[1] = 1
            else:
                self.Pac.coord[1] = 25
        elif coord == 6: #instadeath when colliding with ghost gate
            statechange = True
            state = "dead"
        elif coord == 7:
            ate = True
            statechange = True
            state = "powerup"
            self.Pac.cooldown = 15    
        elif self.Pac.state == "powerup" and self.Pac.cooldown <= 0:
            statechange = True
            state = "begin"

        self.Pac.cooldown -= 1

        return [ate, score, statechange, state]
    

    def Ghostmove(self, ghost, pac):
        x = ghost.coord[1] #column
        y = ghost.coord[0] #row

        w = self.grid[y-1, x]
        a = self.grid[y, x-1]
        s = self.grid[y+1, x]
        d = self.grid[y, x+1]

        coords = [w,a,s,d]
        other = [False, False, ghost.state]
        move = True
        
        if ghost.state == "random":
            poss = self.GhostTarget(ghost, ghost.corner, x, y)
        elif ghost.state == "chase":
            poss = self.GhostTarget(ghost, pac.coord, x, y)
        elif ghost.state == "run":
            pacinvert = [30-pac.coord[0], 26-pac.coord[1]]
            poss = self.GhostTarget(ghost, pacinvert, x, y)
            #THIS NEEDS TWEAKING, COULD RUN STRAIGHT INTO PAC
            #REALL NEED TO INVERT THE SHIT
            #ITS OWN PARAMETER?
        elif ghost.state == "dead":
            if ghost.coord == ghost.origin:
                move = False
            else:
                poss = self.GhostTarget(ghost, ghost.origin, x, y)

        if move:
            for x in poss[0]:
                result = self.directionCheck(x, coords, ghost)
                if result[0]:
                    ghost.direction = x
                    break
        
        other = self.GhostgameCheck(ghost, pac)

        return other

    def GhostTarget(self, ghost, target, x, y):
        
        directions = []
        #find opposite direction:
        for a in range(4):
            if ghost.direction == Extra[13+a]:
                if (13+a)%2 == 0:
                    opposite = Extra[13+a-1]
                else:
                    opposite = Extra[13+a+1]
                break
        
        rowdiff = target[0] - y
        coldiff = target[1] - x

        notsame = True

        #if same distance, prefer vertical movement first
        if abs(rowdiff) >= abs(coldiff):
            big = rowdiff
            small = coldiff
            order = [16,15,13,14]
        elif abs(coldiff) > abs(rowdiff):
            big = coldiff
            small = rowdiff
            order = [13,14,16,15]
        elif abs(coldiff) == 0 and abs(rowdiff) ==0:
            #currently at target
            directions = ["\U00002796", "\U000025FB", "\U00002B1B", "\U00002B1B"]
            directions.remove(opposite)
            notsame = False


        if notsame:
            thirdtry = ["\U000025B6", "\U000025C0", "\U0001F53C", "\U0001F53D"]
            thirdtry.remove(opposite)
            #first trial
            if big > 0 and Extra[order[0]] != opposite: #down or right
                directions.append(Extra[order[0]])
                thirdtry.remove(Extra[order[0]])
            elif big < 0 and Extra[order[1]] != opposite: #up or left
                directions.append(Extra[order[1]])
                thirdtry.remove(Extra[order[1]])
            #second trial
            if small > 0 and Extra[order[2]] != opposite: #down or right
                directions.append(Extra[order[2]])
                thirdtry.remove(Extra[order[2]])
            elif small < 0 and Extra[order[3]] != opposite: #up or left
                directions.append(Extra[order[3]])
                thirdtry.remove(Extra[order[3]])
            elif small == 0:
                if Extra[order[2]] != opposite: 
                    directions.append(Extra[order[2]])
                    thirdtry.remove(Extra[order[2]])
                if Extra[order[3]] != opposite:
                    directions.append(Extra[order[3]])
                    thirdtry.remove(Extra[order[3]])
            #third trial
            for x in thirdtry:
                directions.append(x)
            
        return directions, opposite

    def GhostgameCheck(self, ghost, pac):
        collided = False
        score = 0
        statechange = True
        state = ghost.state

        if ghost.coord == pac.coord or ghost.coord == pac.prevspace or ghost.prevspace == pac.coord:
            collided = True
            #this doesn't account for corner touches - still needs tweaking/better solution
            if pac.state == "powerup":
                state = "dead"
                score = 200
        elif ghost.state != "run" and ghost.state != "dead" and pac.state == "powerup":
            state = "run"
        elif ghost.state == "run" and pac.state == "begin":
            state = "random"
            ghost.cooldown = 10
        elif ghost.state == "run":
            statechange = False
            ghost.counter = 1
        elif ghost.state == "random" and ghost.cooldown <= 0:
            state = "chase"
            ghost.cooldown = 10
        elif ghost.state == "chase" and ghost.cooldown <= 0:
            state = "random"
            ghost.cooldown = 10
        elif ghost.state == "dead" and ghost.coord == ghost.origin:
            state = "random"
            ghost.cooldown = 10
            ghost.counter = 10
        elif self.grid[ghost.coord[0], ghost.coord[1]+1] == 4 or self.grid[ghost.coord[0], ghost.coord[1]-1] == 4:
            if ghost.coord[1] > 10:
                ghost.coord[1] = 1
            else:
                ghost.coord[1] = 25
        else:
            statechange = False

        ghost.cooldown -= 1

        return [collided, statechange, state, score]

    #handling moving emojis around, swapping for states etc.
    def emojiupdate(self, charlist, prevlist, notreset=True):

        rows = []
        for z in prevlist:
            x, y = z[0], z[1]
            self.emojigrid[x][y] = Emojis[self.grid[x,y]]
            rows.append(x)

        if notreset:
            for z in charlist:
                x, y = z.coord[0], z.coord[1]
                self.emojigrid[x][y] = z.display
                rows.append(x)

        blocks = []
        rows = list(set(rows)) #gets rid of duplicates
        for row in rows:
            self.gameview[row] = ''.join(self.emojigrid[row]) + '\n'
            if row < 7:
                blocks.append(1)
            elif row >= 7 and row < 15:
                blocks.append(2)
            elif row >= 15 and row < 23:
                blocks.append(3)
            elif row >= 23:
                blocks.append(4)

        blocks = list(set(blocks))
        
        for block in blocks:
            if block == 1:
                newblock = ''.join(self.gameview[:7])
                self.game.set_field_at(0, name="PAC-MAN: DISCORD", value=newblock, inline=False)
            elif block == 2:
                newblock = ''.join(self.gameview[8:15])
                self.game.set_field_at(1, name=self.gameview[7], value=newblock, inline=False)
            elif block == 3:
                newblock = ''.join(self.gameview[16:23])
                self.game.set_field_at(2, name=self.gameview[15], value=newblock, inline=False)
            elif block == 4:
                newblock = ''.join(self.gameview[24:])
                self.game.set_field_at(3, name=self.gameview[23], value=newblock, inline=False)     


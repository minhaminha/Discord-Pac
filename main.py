import discord
import numpy
import asyncio
import time
from game import Game
from level import Extra

client = discord.Client()
started = False
topscore = 0
topscoreplayer = "no one yet"
nextmoves = []
player = 0
single = True

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    global started
    global topscore
    global nextmoves
    global single
    global topscoreplayer
    
    if message.author == client.user:
        return

    #gotta be able to delete these tfffffff
    
    if message.content.startswith('$help'):
        await message.delete(delay=2)
        helpmsg = sendHelp()
        await message.channel.send(embed=helpmsg, delete_after=60)

    elif message.content.startswith('$instructions'):
        await message.delete(delay=2)
        msg = sendInstruct()
        await message.channel.send(embed=msg, delete_after=45)

    elif message.content.startswith('$pacplay') and not started: #CHANGE TO $PACPLAY
        startmsg = discord.Embed(title="Let's play!")
        await message.channel.send(embed=startmsg, delete_after=5)
        await message.delete(delay=2)
        started = True
        nextmoves = []
        maingame = Game(topscore)

        await message.channel.send(embed=maingame.game, delete_after=3)

        if single:
            player = message.author
        #eventually create scoreboard

        await gameloop(message, maingame, player)

    elif message.content.startswith('$stop') and started:
        started = False
        await message.delete(delay=2)

    elif message.content.startswith('$topscore') and not started:
        await message.delete(delay=2)
        best = discord.Embed(title=f"This channel's top score: {topscore}, by {topscoreplayer}!")
        await message.channel.send(embed=best)

    elif message.content.startswith('$single') and not started:
        await message.delete(delay=2)
        single = True
        mode = discord.Embed(title="Discord-Pac is now in Single Player mode")
        await message.channel.send(embed=mode, delete_after=45)

    elif message.content.startswith('$multi') and not started:
        await message.delete(delay=2)
        single = False
        mode = discord.Embed(title="Discord-Pac is now in Channel Wide mode")
        await message.channel.send(embed=mode, delete_after=45)

    #checks if in single mode and if right person sent the message
    elif started and len(nextmoves) < 3:
        if message.content.startswith('w'):
            nextmoves.append(Extra[15])
            await message.delete(delay=2)

        elif message.content.startswith('a'):
            nextmoves.append(Extra[14])
            await message.delete(delay=2)

        elif message.content.startswith('s'):
            nextmoves.append(Extra[16])
            await message.delete(delay=2)

        elif message.content.startswith('d'):
            nextmoves.append(Extra[13])
            await message.delete(delay=2)


aboutText = """
            Thanks for playing Discord-Pac!

            This bot was built by Minha using the discord.py library and NumPy, as practice for building more complex bots in the future.
            It lacks a lot of feature originally planned and will contain bugs since this is a work in progress!
            There are plans to continue development and polishing when time allows!

            For any problems or questions, you can contact me at: minhalee999@gmail.com
            """
helpText = """
            $instructions = a guide to this version of the game! (recommended before playing)
            $pacplay = start a round of Pac-man!
            $stop = stop the game at any time!
            $single = changes to single player mode! (Default)
            $multi = changes to channel-wide mode!
            $topscore = shows this channel's high score!
            $help = view list of commands, information about the bot, etc.\n
            More features to come!
            """

instructText = """
                This game is in semi-real-time.*
                You control \U0001F60F!
                Look out for: \U0001F47B \U0001F47D \U0001F47E \U0001F916!
                Collect dots ("\U000025AB") to increase you score!
                Powerups ("\U000025FB") make you temporarily invincible and allow you to eat your enemies for more points!.\n
                Change the direction of Pac by sending a new messages:
                "w" (up)
                "a" (left)
                "s" (down)
                "d" (right)
                and the game will record up to 3 next turns which will execute when possible.
                These turns cannot be changed so choose wisely!
                
                Good luck!
                """

def sendHelp():
    helpmsg = discord.Embed(title="Discord-Pac, a Pac-Man rebuild in Discord!", description="Built by really big dog :) (Minha)")
    helpmsg.add_field(name="Commands", value=helpText, inline=False)
    helpmsg.add_field(name="About Discord-Pac", value=aboutText, inline=False)
    helpmsg.add_field(name="I'm also currently looking for work! Email me your career opportunities!", value="Enjoy Discord-Pac!", inline=False)

    return helpmsg

def sendInstruct():
    instructmsg = discord.Embed(title="Thanks for playing Pac-Man!")
    instructmsg.add_field(name="HOW TO PLAY:", value=instructText, inline=False)
    instructmsg.set_footer(text="*moves may take up to 1-2 frames for the game to register, I'm working on fixing this!")

    return instructmsg

#this is the only thing that interfaces between the class and main
async def gameloop(message, maingame, player):
    global started
    global topscore
    global single
    global topscoreplayer
    
    """
    To Implementing:

    Random fruit drops
    Scoreboard
    """

    testtime = [0, 0]
    while started:
        start = time.time()

        await asyncio.gather(
            moveshit(maingame),
            boardupdate(maingame),
            waittime(1)
            )
        await message.channel.send(embed=maingame.game, delete_after=2)
        end = time.time()
        testtime[0] += (end - start)
        testtime[1] += 1

        if maingame.Pac.state == "dead":
            if maingame.lives > 1:
                maingame.lives -= 1
                await asyncio.gather(
                    message.channel.send(f"You died! Lives left: {maingame.lives}", delete_after=5),
                    waittime(5),
                    resetpos(maingame)
                    )
            else:
                highscore = ""
                if maingame.score > topscore:
                    topscore = maingame.score
                    highscore = "A new Top Score!"
                    topscoreplayer = player
                started = False
                seconds = int(testtime[0])%60
                minutes = int((int(testtime[0])-seconds)/60)
                desc = f"Your score was {maingame.score}, achieved in {minutes} minutes and {seconds} seconds! "
                gameover = discord.Embed(title="Game Over!", description=desc+highscore)
                #stats = """You ate: these things etc"""
                #gameover.add_field(name="Stats",
                contact = "For any problems or questions, you can contact me at minhalee999@gmail.com."
                gameover.add_field(name="Thanks for playing!", value=contact, inline=False)
                await message.channel.send(embed=gameover)

    print(f"Avg time: {testtime[0]/testtime[1]}")
            
    started = False

async def moveshit(main):
    global nextmoves

    prevspaces = []
    prevspaces.append(main.Pac.coord.copy())
    
    if len(nextmoves)>=1:
        move = nextmoves[0]
        if main.Pac.direction == move: #just in case same direction doesnt get popped immediately
            nextmoves.pop(0)
    else:
        move = main.Pac.direction

    main.Pac.prevspace = main.Pac.coord.copy()
    changes = main.Pacmove(main.Pac, move)

    if len(nextmoves) >= 1 and prevspaces[0] == main.Pac.coord:
        nextmoves.pop(0)

    if changes[0]: #direction changed
        main.Pac.direction = nextmoves[0]
        nextmoves.pop(0)

    if changes[1]: #ate something
        main.score += changes[2]
        main.grid[main.Pac.coord[0], main.Pac.coord[1]] = 5

    if changes[3]: #statechanged
        main.Pac.changeemoji(changes[4])

    #ghost updates
    for ghost in main.Ghosts:
        if ghost.counter == 0:
            prevspaces.append(ghost.coord.copy())
            ghost.prevspace = ghost.coord.copy()
            ghostmove = main.Ghostmove(ghost, main.Pac)
            
            if ghostmove[0]: #collide with Pac
                if main.Pac.state == "powerup":
                    main.score += ghostmove[3]
                else:
                    main.Pac.state = "dead"

            if ghostmove[1]: #state changed
                ghost.changeemoji(ghostmove[2])
        else:
            ghost.counter -= 1

    if main.Pac.state == "dead":
        main.Pac.changeemoji("dead")

    charlist = [main.Ghosts[0], main.Ghosts[1], main.Ghosts[2], main.Ghosts[3], main.Pac]
    
    #random chance for fruit to be added to matrix (only adds)

    #fruit check is done in PacgameCheck now
    #update GHOSTS in parallel?
    
    main.emojiupdate(charlist, prevspaces)

async def boardupdate(main):
    global nextmoves
    global topscore

    nextturns = ''

    if len(nextmoves)>0:
        nextturns = ''.join(nextmoves)

    #if pac is dead?
    #main.game.title = f"Lives: {main.lives}"
    main.game.set_field_at(4, name=f"Score: {main.score}, High score: {topscore}", value=f"Next moves: {nextturns}", inline=False)     

async def waittime(time):
    await asyncio.sleep(time)

async def resetpos(main):

    chars = [main.Pac]
    clearlist = [main.Pac.coord]
    for ghost in main.Ghosts:
        chars.append(ghost)
        clearlist.append(ghost.coord)

    main.emojiupdate(chars, clearlist, False)
    
    main.Pac.coord = main.Pac.origin
    main.Pac.direction = "\U000025B6"
    main.Pac.state = "begin"
    main.Pac.changeemoji(main.Pac.state)

    for ghost in main.Ghosts:
        ghost.coord = ghost.origin
        ghost.direction = "\U0001F53C"
        ghost.state = "random"
        ghost.changeemoji(ghost.state)

#SWAP THIS OUT BEFORE UPLOADING TO GITHUB/BLANK FOR OTHERS TO PUT THEIR SHIT IN
client.run('ODA2NzAwODg3MjcwODgzMzU4.YBtQvw.N7ATi5TFXsI7wVyrWy65wUBAJdU')

"""Endless turn-based, grid-based, fantasy-themed, strategy game

You must ascend Goblin Tower and reach as high a level as possible.
"""
#TO-DO:
#Write Dungeon class to handle:
#    - Randomly generating map layouts and player and goblin spawns
#                                                   (staggered/instant)
#
#Write Player and Goblin subclasses, they will:
#    - Handle keyboard input (use ord(getch()) - cursor/direct no.)
#    and call damage(), move(), item() (use 8 spaces between options)
#    (getch works in terminal but not IDLE)
#    - Handle levelling up stats and giving items (Player only)
#      Classes include: Paladin - high health, low power
#                       Fighter - medium health, medium power
#                       Rogue - low health, high power
#    - Handle enemy AI (Goblin only)
#    - Contain move(), move_valid() and spawn()
#
#Write an Item class to handle:
#    - Printing inventory (use list_generator.py for numbered list
#    - Processing number input into calling item subclass method
#Write subclasses for seperate item types (eg. grenade, potion)
#
#Edit entity status based on actions(eg:walking, idle, in combat)
#
#Use variable to store no. of enemies left; decrease with kill and whem 0, activate stairs
#
#To improve player experience add:
#    - Context messages
#    - Sleep delays
#    - Music and sound effects (via vlc.MediaPlayer)
#    - More ASCII art
#    - "You are the nth adventurer to enter Goblin Tower" msg using
#      a text file to store n

from time import sleep
from random import randint, shuffle, choice
from msvcrt import getch
from vlc import MediaPlayer

class Entity(object):
    """Base class for all entities in game."""
    invent = []
    
    def __init__(self, health, max_health, power, status, name,
                 descript, role, sym):
        self.health = health
        self.max_health = max_health
        self.power = power
        self.status = status
        self.name = name
        self.descript = descript
        self.role = role
        self.sym = sym

    def isalive(self):
        """Return True if alive, False if not."""
        return (not self.health <= 0)
    
    def damage(self, board, enemy):
        """Run damage sequence including exiting on player death and level up check on goblin death."""
        enemy.health -= self.power
        if not enemy.isalive():
            enemy.status = "Dead"
        a = self.stats()
        b = enemy.stats()
        print("""
{} attacks {} for {} damage!""".format(self.name, enemy.name,
                                       self.power))
        sleep(2)
        print(a, '\n', b)
        if player.status == "Dead":
            player.health = 0
            print("""
You died! - GAME OVER""")
            sleep(3)
            with open("text_sources/hall_of_fame.txt",
                      "a") as hall:
                hall.write(player.stats() + '\n')
            with open("text_sources/hall_of_fame.txt",
                      "r") as hall:
                print("""
HALL OF FAME
{}""".format(hall.read()))
            input("Press ENTER to quit")
            exit()
        elif enemy.status == "Dead":
            player.exp += 1
            x = enemy.getx(board)
            y = enemy.gety(board)
            board.board[y][x] = 'O'
            print("""
You slayed {}!""".format(enemy.name))
            if player.exp % 5 == 0:
                player.level_up()

    def stats(self):
        """Return formatted stats for the entity."""
        a = """
Name: {}
Class: {}
Health: {}/{}
Power: {}
Status: {}
Description: {}""".format(self.name, self.role, self.health,
                          self.max_health, self.power,
                          self.status, self.descript)
        return a

    def getx(self, board):
        """Return the x coordinate of the entity, else return -1 if not on board."""
        for n in range(board.size):
            for i, c in enumerate(board.board[n]):
                if c == self.sym:
                    return i
        return -1

    def gety(self, board):
        """Return the y coordinate of the entity, else return -1 if not on board."""
        for n in range(board.size):
            for c in board.board[n]:
                if c == self.sym:
                    return n
        return -1

    def spawn(self, board, x, y):
        """Replaces the given coordinate in board with self.sym."""
        board.board[y][x] = self.sym

    def remove(self, board):
        """Replaces the entity in the board with 'O'."""
        x = self.getx(board)
        y = self.gety(board)
        board.board[y][x] = 'O'

    def move_valid(self, board, direction, n):
        """If move is valid return True. else return False."""
        x = self.getx(board)
        y = self.gety(board)
        if direction == 'left' or direction == 'up':
            if direction == 'left':
                y -= n
            elif direction == 'up':
                x -= n
            if x or y < 0:
                return False
            else:
                return True
        else:
            if direction == 'right':
                y += n
            elif direction == 'down':
                x += n
            try:
                board.board[x][y]
            except IndexError:
                return False
            else:
                return True

    def move(self, board, direction, n):
        """Moves self.sym on board in direction by n spaces."""
        original_x = self.getx(board)
        original_y = self.gety(board)
        if direction == 'left':
            board.board[original_x][original_y - n] = self.sym
        elif direction == 'right':
            board.board[original_x][original_y + n] = self.sym
        elif direction == 'up':
            board.board[original_x - n][original_y] = self.sym
        elif direction == 'down':
            board.board[original_x + n][original_y] = self.sym
        board.board[original_x][original_y] = 'O'


class Player(Entity):
    """Subclass of Entity for player object"""
    def __init__(self, health, max_health, power, status, name,
                 descript, role, sym, level, floor):
        self.exp = 0
        self.health = health
        self.max_health = max_health
        self.power = power
        self.status = status
        self.name = name
        self.descript = descript
        self.role = role
        self.sym = sym
        self.level = level
        self.floor = floor

    def stats(self):
        """Return formatted stats for player character."""
        a = """
Name: {}
Level: {}
Class: {}
Floor: {}
Health: {}/{}
Power: {}
Status: {}
Description: {}""".format(self.name, self.level, self.role,
                          self.floor, self.health,
                          self.max_health, self.power,
                          self.status, self.descript)
        return a

    def level_up(self):
        """Initiates level up sequence."""
        print(self.stats())
        print("""
LEVEL UP! - Add 1 point to health or power?

1.Health        2.Power""")
        self.level += 1
        while True:
            a = ord(getch())
            if a == 49:
                self.health += 1
                self.max_health += 1
                break
            elif a == 50:
                self.power += 1
                break
            elif a == 3:
                raise KeyboardInterrupt
        print(self.stats())


class Dungeon(object):
    """Base class to create, format and print list of lists 'board' on which gameplay takes place."""
    board = []
    
    def __init__(self, size):
        self.size = size     
        for n in range(self.size):
            self.board.append(['O'] * self.size)

    def print_board(self):
        """Print board in clean, front-end grid form"""
        for row in self.board:
            print(' '.join(row))


print(r"""
   ____          __    _  __        __    _____                           ___  ___ _______
  / __/__ ____ _/ /__ / |/ /__ ___ / /_  / ___/__ ___ _  ___ ___   ____  |_  |/ _ <  /_  /
 / _// _ `/ _ `/ / -_)    / -_|_-</ __/ / (_ / _ `/  ' \/ -_|_-<  /___/ / __// // / / / / 
/___/\_,_/\_, /_/\__/_/|_/\__/___/\__/  \___/\_,_/_/_/_/\__/___/       /____/\___/_/ /_/  
         /___/                                                                            

****************************************************************************

  ________      ___.   .__  .__         ___________                         
 /  _____/  ____\_ |__ |  | |__| ____   \__    ___/_____  _  __ ___________ 
/   \  ___ /  _ \| __ \|  | |  |/    \    |    | /  _ \ \/ \/ // __ \_  __ \
\    \_\  (  <_> ) \_\ \  |_|  |   |  \   |    |(  <_> )     /\  ___/|  | \/
 \______  /\____/|___  /____/__|___|  /   |____| \____/ \/\_/  \___  >__|   
        \/           \/             \/                             \/       

****************************************************************************

Press ENTER to start""")
input()

#Db
player = Player(20, 20, 5, "Idle", "Player", "A test player",
                "Fighter", 'P', 1, 1)
goblin1 = Entity(5, 5, 10, "Idle", "Trixy", "A goblin minion",
                 "Minion", 'T')
level1 = Dungeon(5)

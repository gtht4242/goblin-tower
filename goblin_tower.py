"""Endless turn-based, grid-based, fantasy-themed, strategy game

You must ascend Goblin Tower and reach as high a floor as possible."""
# TODO
# Implement graphics and music/sfx via pygame:
#   - Test if msvcrt still works, if not, rewrite input (1.e. detect keyboard snippets) to use pygame keyboard/mouse input
#   - Rewrite output to read board list and convert to grid of 2D images
#   - Display appropriate text (e.g stats)
#   - Configure window icon and caption
#
# Write Item class to handle:
#   - Printing/returning inventory (use list_generator.py for numbered list)
#   - Processing number input into calling item subclass method (or put this in player turn loop instead)
#   - Subclasses for seperate item types? (eg. grenade, potion)
# 
# Write Save class to handle:
#   - Saving relevant variables and attributes at start of round into file with inputted name
#     (including option to overwrite existing file)
#   - Option to load from file at boot up
# 
# To improve player experience:
#   - Print player name in blue and enemy names in red (both with white background)
#   - Add more context print messages
#   - Adjust sleep delays
#   - Add more ASCII art
#   - Add "You are the nth adventurer to enter Goblin Tower" message using a text file to store n
#   - Write proper start and gameloop functions so game can return to start screen on death
#
# To improve developer experience:

import os
from itertools import count
from msvcrt import getch
from random import choice, randint
from sys import exit
from time import sleep

import colorama
import pygame
from profanity import profanity
from pygame.locals import *
from termcolor import colored, cprint

colorama.init()

BACKGROUND_COLOUR = "on_white"
PLAYER_COLOUR = "cyan"
GOBLIN_COLOUR = "red"
EMPTY_CHAR = colored("O", "grey", BACKGROUND_COLOUR)

class_continue = True
player_continue = True

def round_up(n, round_to):
    """Rounds n up to nearest multiple of round_to (including if already multiple)."""
    for n in count(n + 1):
        if n % round_to == 0 and not n < 0:
            return n

def init_floor():
    """Initialise variables for new floor."""
    global board, goblin1, goblin2, goblin3, goblins, goblin_count, turn
    board = Dungeon(10)
    low_health = randint(1, 5)
    med_health = randint(3, 7)
    high_health = randint(5, 9)
    low_power = randint(1, 2)
    med_power = randint(3, 4)
    high_power = randint(5, 6)
    name1 = choice(names) + ' the ' + choice(titles)
    name2 = choice(names) + ' the ' + choice(titles)
    name3 = choice(names) + ' the ' + choice(titles)
    goblin1 = Goblin(low_health, low_health, high_power, "Ready", name1,
                     "A fast and silent killer armed with a dagger", "Assassin",
                     colored('A', GOBLIN_COLOUR, BACKGROUND_COLOUR))
    goblin2 = Goblin(med_health, med_health, med_power, "Ready", name2,
                     "A skilled swordsman loyal to the Goblin King", "Knight",
                     colored('K', GOBLIN_COLOUR, BACKGROUND_COLOUR))
    goblin3 = Goblin(high_health, high_health, low_power, "Ready", name3,
                     "A heavily armoured sentinel equipped with a mace", "Champion",
                     colored('C', GOBLIN_COLOUR, BACKGROUND_COLOUR))
    goblins = (goblin1, goblin2, goblin3)
    player.rand_spawn(board)
    goblin1.rand_spawn(board)
    goblin2.rand_spawn(board)
    goblin3.rand_spawn(board)
    for goblin in goblins:
        goblin.reset_destination(board)
    goblin_count = 3
    turn = 1

class Entity(object):
    """Base class for all entities in the game."""

    def __init__(self, health, max_health, power, status, name, descript, role, sym):
        self.health = health
        self.max_health = max_health
        self.power = power
        self.status = status
        self.name = name
        self.descript = descript
        self.role = role
        self.sym = sym

    def is_alive(self):
        """If alive return True, else False."""
        return (not self.health <= 0)
    
    def damage(self, board, target):
        """Run damage sequence including exiting on player death and updating game state on goblin death."""
        global goblin_count
        self.status = "Attacking"
        target.status = "Defending"
        target.health -= self.power
        if not target.is_alive():
            target.status = "Dead"
            target.health = 0
        cprint(f"""
{self.name} attacks {target.name} for {self.power} damage!""")
        sleep(2)
        cprint(self.stats())
        cprint(target.stats())
        if player.status == "Dead":
            cprint("""
You died! - GAME OVER""")
            sleep(3)
            clear = os.system('cls')
            with open("text/hall_of_fame.txt", "a") as hall:
                hall.write(player.stats() + '\n')
            with open("text/hall_of_fame.txt", "r") as hall:
                cprint(f"""HALL OF FAME
{hall.read()}
*******************
""")
            input("Press ENTER to quit")
            exit()
        elif target.status == "Dead":
            player.exp += 1
            goblin_count -= 1
            target.remove(board)
            cprint(f"""
You slayed {target.name}!""")
            if player.exp % 5 == 0:
                player.level_up()
        player.status = "Ready"
        target.status = "Ready"

    def stats(self):
        """Return formatted stats for the entity."""
        return f"""
Name: {self.name}
Class: {self.role}
Health: {self.health}/{self.max_health}
Power: {self.power}
Status: {self.status}
Description: {self.descript}"""

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

    def adjacent(self, board, entity):
        """True if self is adjacent to entity on board, else false."""
        self_adjacent = []
        if self.getx(board) + 1 < board.size:
            self_adjacent.append(board.board[self.gety(board)][self.getx(board) + 1])
        if self.gety(board) + 1 < board.size:
            self_adjacent.append(board.board[self.gety(board) + 1][self.getx(board)])
        if self.getx(board) - 1 > -1:
            self_adjacent.append(board.board[self.gety(board)][self.getx(board) - 1])
        if self.gety(board) - 1 > -1:
            self_adjacent.append(board.board[self.gety(board) - 1][self.getx(board)])
        return entity.sym in self_adjacent

    def get_adjacent(self, board):
        """Return list of adjacent characters (None if empty) starting from the top and going clockwise."""
        self_adjacent = []
        if self.gety(board) - 1 > -1:
            self_adjacent.append(board.board[self.gety(board) - 1][self.getx(board)])
        else:
            self_adjacent.append(None)
        if self.getx(board) + 1 < board.size:
            self_adjacent.append(board.board[self.gety(board)][self.getx(board) + 1])
        else:
            self_adjacent.append(None)
        if self.gety(board) + 1 < board.size:
            self_adjacent.append(board.board[self.gety(board) + 1][self.getx(board)])
        else:
            self_adjacent.append(None)
        if self.getx(board) - 1 > -1:
            self_adjacent.append(board.board[self.gety(board)][self.getx(board) - 1])
        else:
            self_adjacent.append(None)
        return self_adjacent

    def spawn(self, board, x, y):
        """Replaces the given space in board with the entity's symbol."""
        board.board[y][x] = self.sym

    def rand_spawn(self, board):
        """Replaces a random empty space in board with the entity's symbol."""
        while True:
            x = randint(0, board.size - 1)
            y = randint(0, board.size - 1)
            if board.board[y][x] == EMPTY_CHAR:
                board.board[y][x] = self.sym
                break

    def remove(self, board):
        """Replaces the entity in the board with 'O'."""
        board.board[self.gety(board)][self.getx(board)] = EMPTY_CHAR

    def move_valid(self, board, direction, n):
        """If move is valid return True. else False."""
        x = self.getx(board)
        y = self.gety(board)
        if direction == 'left' or direction == 'up':
            if direction == 'up':
                y -= n
            elif direction == 'left':
                x -= n
            if x < 0 or y < 0 or board.board[y][x] != EMPTY_CHAR:
                return False
            else:
                return True
        else:
            if direction == 'down':
                y += n
            elif direction == 'right':
                x += n
            if x >= board.size or y >= board.size or board.board[y][x] != EMPTY_CHAR:
                return False
            else:
                return True

    def move(self, board, direction, n):
        """Moves entity on board in given direction by n spaces."""
        original_x = self.getx(board)
        original_y = self.gety(board)
        if direction == 'up':
            board.board[original_y - n][original_x] = self.sym
        elif direction == 'down':
            board.board[original_y + n][original_x] = self.sym
        elif direction == 'left':
            board.board[original_y][original_x - n] = self.sym
        elif direction == 'right':
            board.board[original_y][original_x + n] = self.sym
        board.board[original_y][original_x] = EMPTY_CHAR
    
    def teleport(self, board, x, y):
        """Removes current entity char on board and spawns it in space referenced by x and y."""
        self.remove(board)
        self.spawn(board, x, y)


class Player(Entity):
    """Subclass of Entity for player object including unique stats formatter and level up sequence."""
    level = 1

    def __init__(self, health, max_health, power, status, name, descript, role, sym, exp, floor):
        self.health = health
        self.max_health = max_health
        self.power = power
        self.status = status
        self.name = name
        self.descript = descript
        self.role = role
        self.sym = sym
        self.exp = exp
        self.floor = floor

    def stats(self):
        """Return formatted stats for player character."""
        return f"""
Floor: {self.floor}
Name: {self.name}
Class: {self.role}
Level: {self.level}
Exp. points: {self.exp}/{round_up(self.exp, 5)}
Health: {self.health}/{self.max_health}
Power: {self.power}
Status: {self.status}
Description: {self.descript}"""

    def level_up(self):
        """Initiates level up sequence."""
        self.level += 1
        cprint(self.stats())
        cprint("""
LEVEL UP! - Add 1 point to health or power?

1. Health
2. Power""")
        while True:
           key = ord(getch())
           if key == 49:
                self.health += 1
                self.max_health += 1
                break
           elif key == 50:
                self.power += 1
                break
           elif key == 3:
                raise KeyboardInterrupt
        cprint(self.stats())


class Goblin(Entity):
    """Subclass of Entity for goblin objects including enemy AI move generator."""
    destination_x = None
    destination_y = None
    direction = ''
    directions = []

    def set_direction(self, board):
        """Sets direction of movement based on own position and destination coordinates"""
        self.directions = []
        x_distance = self.getx(board) - self.destination_x
        y_distance = self.gety(board) - self.destination_y
        if self.gety(board) != self.destination_y:
            if y_distance == abs(y_distance):
                self.directions.append('up')
            else:
                self.directions.append('down')
        if self.getx(board) != self.destination_x:
            if x_distance == abs(x_distance):
                self.directions.append('left')
            else:
                self.directions.append('right')
        if len(self.directions) == 1:
            self.direction = self.directions[0]
        else:
            if abs(x_distance) > abs(y_distance):
                self.direction = self.directions[0]
            elif abs(x_distance) < abs(y_distance):
                self.direction = self.directions[1]
            else:
                self.direction = choice(self.directions)
    
    def reset_destination(self, board):
        """Resets destination coordinates to player coordinates."""
        self.destination_x = player.getx(board)
        self.destination_y = player.gety(board)

class Dungeon(object):
    """Base class to create, format and print board."""

    def __init__(self, size):
        self.size = size
        self.board = []
        for n in range(self.size):
            self.board.append([EMPTY_CHAR] * self.size)

    def print_board(self):
        """Print board in formatted, front-end grid form."""
        for row in self.board:
            cprint(colored(' ', 'grey', BACKGROUND_COLOUR).join(row))

    def return_board(self):
        """Return board in formatted, front-end grid form."""
        new_board = ''
        for i, row in enumerate(self.board):
            new_board += colored(' ', 'grey', BACKGROUND_COLOUR).join(row)
            if i < self.size - 1:
                new_board += '\n'
        return new_board


# Initialise lists of possible goblin names and titles
names = ['Antonio', 'Elliot', 'Amina', 'Un', 'Ezra', 'Erin', 'Willetta', 'Anisa', 'Zackary', 'Dede', 'Joye',
'Eric', 'Marybelle', 'Cleveland', 'Hank', 'Ashanti', 'Saturnina', 'Gidget', 'Felicidad', 'Annalee', 'Palmira',
'Franklin', 'Cristobal', 'Leif', 'Johnny', 'Merrill', 'Deon', 'Freddy', 'Julene', 'Maryln', 'Kattie', 'Chase',
'Barrett', 'Luanna', 'Cameron', 'Monserrate', 'Chauncey', 'Marcelo', 'Jerry', 'Kiana', 'Denver', 'Eusebio',
'Boris', 'Earl', 'Gretta', 'Ricky', 'Ed', 'Vannesa', 'Gilbert', 'Jae', 'Lyle', 'Jesse', 'Agueda', 'Jolie',
'Zachery', 'Korey', 'Kyle', 'Javier', 'Anya', 'Farah', 'Norbert', 'Jolyn', 'Cassi', 'Paul', 'Gerard', 'Frida',
'Raeann', 'Burton', 'Otha', 'Elroy', 'Freddie', 'Lucius', 'Gary', 'Jc', 'Tona', 'Noah', 'Dannette',
'Nathaniel', 'Rolf', 'Jen', 'Minta', 'Linsey', 'Chan', 'Lovella', 'Dann', 'Amberly', 'Pedro', 'Annalisa',
'Belia', 'Stefan', 'Dante', 'Jaye', 'Cyndy', 'Enola', 'Ehtel', 'Jim', 'Larae', 'Theo', 'Raphael', 'Barbera',
'Kraig', 'Forest', 'Elliott', 'Stacey', 'Kiesha', 'Latrisha', 'Jamar', 'Isidro', 'Temika', 'Joshua', 'Man',
'Tyrell', 'Brandon', 'Chi', 'Rodney', 'Cristopher', 'Keven', 'Ellamae', 'Crystle', 'Librada', 'Faustina',
'Gearldine', 'Merlin', 'Oswaldo', 'Ashli', 'Florinda', 'Susann', 'Pamella', 'Bettyann', 'Lynna', 'Loree',
'Winford', 'Marvis', 'Faustino', 'Isiah', 'Salena', 'Edmond', 'Trevor', 'Corrin', 'Leigh', 'Britni',
'Shaniqua', 'Corrinne', 'Brice', 'Lamar', 'Diego', 'Domonique', 'Domingo', 'Cecille', 'Romeo', 'Shannon',
'Maryalice', 'Eustolia', 'Magdalen', 'Bernetta', 'Alfonso', 'Charley', 'Dane', 'Eli', 'Charlott', 'Vincenzo',
'Dierdre', 'Isaac', 'Katerine', 'Jordan', 'Chae', 'Warner', 'Esteban', 'Codi', 'Carl', 'Lanora', 'Kristle',
'Andrew', 'Latoyia', 'Annice', 'Lucio', 'Santiago', 'Fletcher', 'Karisa', 'Alex', 'Lucas', 'Derrick', 'Erik',
'Patience', 'Ardelia', 'Silas', 'Caroll', 'Ernest', 'Rickey', 'Reinaldo', 'Jarred', 'Evita', 'Britta',
'Royce', 'Denis', 'Tobie', 'Raisa']
titles = ["Able", "Accepting", "Adventurous", "Aggressive", "Ambitious", "Annoying", "Arrogant", "Articulate",
"Athletic", "Awkward", "Boastful", "Bold", "Bossy", "Brave", "Bright", "Busy", "Calm", "Careful", "Careless",
"Caring", "Cautious", "Cheerful", "Clever", "Clumsy", "Compassionate", "Complex", "Conceited", "Confident",
"Considerate", "Cooperative", "Courageous", "Creative", "Curious", "Dainty", "Daring", "Dark", "Defiant",
"Demanding", "Determined", "Devout", "Disagreeable", "Disgruntled", "Dreamer", "Eager", "Efficient",
"Embarrassed", "Energetic", "Excited", "Expert", "Fair", "Faithful", "Fancy", "Fighter", "Forgiving",
"Free", "Friendly", "Friendly", "Frustrated", "Fun-loving", "Funny", "Generous", "Gentle", "Giving",
"Gorgeous", "Gracious", "Grouchy", "Handsome", "Happy", "Hard-working", "Helpful", "Honest", "Hopeful",
"Humble", "Humorous", "Imaginative", "Impulsive", "Independent", "Intelligent", "Inventive", "Jealous",
"Joyful", "Judgmental", "Keen", "Kind", "Knowledgeable", "Lazy", "Leader", "Light", "Light-hearted",
"Likeable", "Lively", "Lovable", "Loving", "Loyal", "Manipulative", "Materialistic", "Mature", "Melancholy",
"Merry", "Messy", "Mischievous", "Naïve", "Neat", "Nervous", "Noisy", "Obnoxious", "Opinionated", "Organized",
"Outgoing", "Passive", "Patient", "Patriotic", "Perfectionist", "Personable", "Pitiful", "Plain", "Pleasant",
"Pleasing", "Poor", "Popular", "Pretty", "Prim", "Proper", "Proud", "Questioning", "Quiet", "Radical",
"Realistic", "Rebellious", "Reflective", "Relaxed", "Reliable", "Religious", "Reserved", "Respectful",
"Responsible", "Reverent", "Rich", "Rigid", "Rude", "Sad", "Sarcastic", "Self-confident", "Self-conscious",
"Selfish", "Sensible", "Sensitive", "Serious", "Short", "Shy", "Silly", "Simple", "Simple-minded", "Smart",
"Stable", "Strong", "Stubborn", "Studious", "Successful", "Tall", "Tantalizing", "Tender", "Tense",
"Thoughtful", "Thrilling", "Timid", "Tireless", "Tolerant", "Tough", "Tricky", "Trusting", "Ugly",
"Understanding", "Unhappy", "Unique", "Unlucky", "Unselfish", "Vain", "Warm", "Wild", "Willing",
"Wise", "Witty"]
clear = os.system('cls')
cprint(r"""
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
clear = os.system('cls')
name = profanity.censor(input("""Hello adventurer!

What is your name?
"""))
while True:
    class_continue = True
    clear = os.system('cls')
    cprint("""One fateful night, you find yourself lost in the deep forests of Yaagnok during a violent
lightning storm. You are at least a day from town and are quickly running out of supplies. You spot a old, 
run-down tower through a clearing in the trees. The storm picks up and you are left with no choice but to
take shelter in the tower.

What kind of adventurer are you?

1. Paladin (high health, low power)
2. Fighter (medium health, medium power)
3. Rogue (low health, high power)

DB:
4. GOD MODE
5. PLAYER DEATH""")
    while True:
        key = ord(getch())
        if key == 49:
            player = Player(20, 20, 2, "Ready", name, "A noble warrior loyal to his faith and clergy",
                            "Paladin", colored("P", PLAYER_COLOUR, BACKGROUND_COLOUR), 0, 1)
            break
        elif key == 50:
            player = Player(15, 15, 4, "Ready", name, "A master of the martial arts from young",
                            "Fighter", colored("F", PLAYER_COLOUR, BACKGROUND_COLOUR), 0, 1)
            break
        elif key == 51:
            player = Player(10, 10, 6, "Ready", name, "A cunning lone wolf thief who trusts no one",
                            "Rogue", colored("R", PLAYER_COLOUR, BACKGROUND_COLOUR), 0, 1)
            break
        elif key == 52:
            player = Player(10000, 10000, 1000, "Ready", name, "For debugging",
                            "GOD MODE", colored("G", PLAYER_COLOUR, BACKGROUND_COLOUR), 4, 1)
            break
        elif key == 53:
            player = Player(0, 10000, 0, "Ready", name, "For debugging",
                            "PLAYER DEATH", colored("D", PLAYER_COLOUR, BACKGROUND_COLOUR), 0, 1)
            break
        elif key == 3:
            raise KeyboardInterrupt
    clear = os.system('cls')
    cprint(f"""As soon as you step inside, the rusty iron door slams shut behind you, as if pushed by some
magical force. A shrill cackle fills the air as you scan your surroundings. As the first goblins step out
of the darkness, you ready your weapon, unaware of the dangers that lie ahead.
{player.stats()}

Press ENTER to start climbing Goblin Tower

(or press ESC to return to class selection screen)""")
    while True:
        key = ord(getch())
        if key == 13:
            break
        elif key == 27:
            class_continue = False
            break
        elif key == 3:
            raise KeyboardInterrupt
    if not class_continue:
        continue
    else:
        break
while True:
    init_floor()
    while goblin_count > 0:
        # Player turn
        player_continue = True
        clear = os.system('cls')
        round_screen = f"""ROUND {turn}

PLAYER TURN - {player.role.upper()}

{board.return_board()}
{player.stats()}"""
        cprint(round_screen)
        cprint("""
1. Move             Db:
2. Attack           4. Teleport
3. Examine          5. Reset""")
        while player_continue:
            key = ord(getch())
            if key == 49:
                # Move
                while player_continue:
                    clear = os.system('cls')
                    cprint(round_screen)
                    cprint("""
Select a direction with the ARROW KEYS. (ESC to go back)""")
                    while player_continue:
                        key = ord(getch())
                        if key == 72:
                            direction = 'up'
                            break
                        elif key == 80:
                            direction = 'down'
                            break
                        elif key == 75:
                            direction = 'left'
                            break
                        elif key == 77:
                            direction = 'right'
                            break
                        elif key == 27:
                            player_continue = False
                        elif key == 3:
                            raise KeyboardInterrupt
                    if player_continue:
                        if player.move_valid(board, direction, 1):
                            player.move(board, direction, 1)
                            for goblin in goblins:
                                goblin.reset_destination(board)
                            break
                        else:
                            cprint("""
That move is not valid!""")
                            sleep(3)
                break
            elif key == 50:
                # Attack
                while player_continue:
                    for goblin in goblins:
                        if goblin.adjacent(board, player):
                            break
                    else:
                        cprint("""
There is no one in range!""")
                        sleep(3)
                        player_continue = False
                    if player_continue:
                        attack_num = 1
                        attack_order = {}
                        for goblin in goblins:
                            if goblin.adjacent(board, player):
                                attack_order[attack_num] = goblin
                                attack_num += 1                               
                        clear = os.system('cls')
                        cprint(round_screen)
                        cprint("""
Select a target with the NUMBER KEYS. (ESC to go back)
""")
                        for enemy in attack_order:
                            cprint(f'{enemy}. {attack_order[enemy].role}')
                        while player_continue:
                            key = ord(getch())
                            if key == 49 and 1 in attack_order:
                                attack_target = 1
                                break
                            elif key == 50 and 2 in attack_order:
                                attack_target = 2
                                break
                            elif key == 51 and 3 in attack_order:
                                attack_target = 3
                                break
                            elif key == 27:
                                player_continue = False
                            elif key == 3:
                                raise KeyboardInterrupt
                        if player_continue:
                            clear = os.system('cls')
                            cprint(round_screen)
                            player.damage(board, attack_order[attack_target])
                            sleep(5)
                            break
                break
            elif key == 51:
                # Examine
                while player_continue:
                    clear = os.system('cls')
                    cprint(round_screen)
                    cprint("""
Select a target with the NUMBER KEYS. (ESC to go back)
""")
                    examine_num = 1
                    examine_order = {}
                    for goblin in goblins:
                        if goblin.is_alive():
                            examine_order[examine_num] = goblin
                            cprint(f'{examine_num}. {goblin.role}')
                            examine_num += 1
                    while player_continue:
                        key = ord(getch())
                        if key == 49 and 1 in examine_order:
                            examine_target = 1
                            break
                        elif key == 50 and 2 in examine_order:
                            examine_target = 2
                            break
                        elif key == 51 and 3 in examine_order:
                            examine_target = 3
                            break
                        elif key == 27:
                            player_continue = False
                        elif key == 3:
                            raise KeyboardInterrupt
                    if player_continue:
                        clear = os.system('cls')
                        cprint(round_screen)
                        cprint(examine_order[examine_target].stats() + '\n' * 2 + "Press ENTER to continue.")
                        input()
                        break
                break
            elif key == 52:
                # Teleport - Db
                clear = os.system('cls')
                cprint(round_screen)
                cprint("""
Choose target.

1. Player
2. Assassin
3. Knight
4. Champion""")
                while True:
                    key = ord(getch())
                    if key == 49:
                        target = player
                        break
                    elif key == 50:
                        target = goblin1
                        break
                    elif key == 51:
                        target = goblin2
                        break
                    elif key == 52:
                        target = goblin3
                        break
                    elif key == 27:
                        player_continue = False
                        break
                    elif key == 3:
                        raise KeyboardInterrupt
                if player_continue:
                    while True:
                        destination = input(f"""
x = {target.getx(board)}
y = {target.gety(board)}

Enter x and y coordinates of destination separated by a space.

""")
                        teleport_x = int(destination[0])
                        teleport_y = int(destination[-1])
                        destination_char = board.board[teleport_y][teleport_x]
                        if destination_char == EMPTY_CHAR or target == player and destination_char == player.sym:
                            break
                        else:
                            cprint("""
Destination is non-empty space!""")
                    target.teleport(board, teleport_x, teleport_y)
                    if target == player:
                        for goblin in goblins:
                            goblin.reset_destination(board)
                    else:
                        target.reset_destination(board)
                    player_continue = False
            elif key == 53:
                # Reset - Db
                clear = os.system('cls')
                cprint(round_screen)
                cprint("""
Press any key to confirm floor reset.""")
                while True:
                    key = ord(getch())
                    if key == 27:
                        player_continue = False
                        break
                    elif key == 3:
                        raise KeyboardInterrupt                
                    else:
                        init_floor()
                        player_continue = False
                        break
            elif key == 3:
                raise KeyboardInterrupt
        if not player_continue:
            continue
        round_screen = f"""ROUND {turn}

PLAYER TURN - {player.role.upper()}

{board.return_board()}
{player.stats()}"""
        clear = os.system('cls')
        cprint(round_screen)
        sleep(3)
        # Goblin turn
        for goblin in goblins:
            if goblin.is_alive():
                round_screen = f"""ROUND {turn}

GOBLIN TURN - {goblin.role.upper()}

{board.return_board()}
{player.stats()}

Db:
destination_x = {goblin.destination_x}
destination_y = {goblin.destination_y}"""
                clear = os.system('cls')
                cprint(round_screen)
                if goblin.adjacent(board, player):
                    # Attack
                    goblin.reset_destination(board)
                    goblin.damage(board, player)
                    sleep(5)
                else:
                    # Move
                    block_num = 0
                    if goblin.getx(board) == goblin.destination_x and goblin.gety(board) == goblin.destination_y:
                        goblin.reset_destination(board)
                    while True:
                        if block_num > 3:
                            goblin.reset_destination(board)
                            break
                        goblin.set_direction(board)
                        if goblin.move_valid(board, goblin.direction, 1):
                            goblin.move(board, goblin.direction, 1)
                            break
                        else:
                            goblin.reset_destination(board)
                            if block_num == 1:
                                if goblin.direction == 'up' or goblin.direction == 'down':
                                    goblin.destination_y = player.gety(board) - 1
                                elif goblin.direction == 'left' or goblin.direction == 'right':
                                    goblin.destination_x = player.getx(board) - 1
                            elif block_num == 2:
                                if goblin.direction == 'up' or goblin.direction == 'down':
                                    goblin.destination_y = player.gety(board) + 1
                                elif goblin.direction == 'left' or goblin.direction == 'right':
                                    goblin.destination_x = player.getx(board) + 1
                            else:
                                if goblin.direction == 'up' or goblin.direction == 'down':
                                    if player.get_adjacent(board)[3] == EMPTY_CHAR:
                                        goblin.destination_x = player.getx(board) - 1
                                    elif player.get_adjacent(board)[1] == EMPTY_CHAR:
                                        goblin.destination_x = player.getx(board) + 1
                                elif goblin.direction == 'left' or goblin.direction == 'right':
                                    if player.get_adjacent(board)[0] == EMPTY_CHAR:
                                        goblin.destination_y = player.gety(board) - 1
                                    elif player.get_adjacent(board)[2] == EMPTY_CHAR:
                                        goblin.destination_y = player.gety(board) + 1
                            block_num += 1
                round_screen = f"""ROUND {turn}

GOBLIN TURN - {goblin.role.upper()}

{board.return_board()}
{player.stats()}

Db:
destination_x = {goblin.destination_x}
destination_y = {goblin.destination_y}"""
                clear = os.system('cls')
                cprint(round_screen)
                sleep(3)
        #End of round
        turn += 1
    else:
        cprint("""
FLOOR UP!""")
        player.floor += 1
        sleep(3)

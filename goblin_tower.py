"""Endless turn-based, grid-based, fantasy-themed, strategy game

You must ascend Goblin Tower and reach as high a floor as possible.
"""
#TO-DO:
#Write Player and Goblin subclasses, they will:
#    - Handle keyboard input (use ord(getch()) and call damage(), move(), item())
#      (or maybe just do this in the player turn loop)
#    - Handle enemy AI (Goblin only)
#
#Write an Item class to handle:
#    - Printing inventory (use list_generator.py for numbered list)
#    - Processing number input into calling item subclass method
#Write subclasses for seperate item types (eg. grenade, potion)
#
#To improve player experience add:
#    - Context messages
#    - Sleep delays
#    - Screen clears
#    - Music and sound effects (via vlc.MediaPlayer)
#    - More ASCII art
#    - "You are the nth adventurer to enter Goblin Tower" msg using
#      a text file to store n

from os import system
from random import choice, randint
from sys import exit
from time import sleep

import colorama
from profanity import profanity
from termcolor import colored, cprint
from vlc import MediaPlayer

from msvcrt import getch


colorama.init()
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
        """Return True if alive, False if not."""
        return (not self.health <= 0)
    
    def damage(self, board, enemy):
        """Run damage sequence including exiting on player death and updating values on goblin death."""
        self.status = "Attacking"
        enemy.status = "Attacking"
        enemy.health -= self.power
        if not enemy.is_alive():
            enemy.status = "Dead"
        a = self.stats()
        b = enemy.stats()
        cprint("""
{} attacks {} for {} damage!""".format(self.name, enemy.name,
                                       self.power))
        sleep(2)
        cprint(a, '\n', b)
        if player.status == "Dead":
            player.health = 0
            cprint("""
You died! - GAME OVER""")
            sleep(3)
            with open("text_sources/hall_of_fame.txt", "a") as hall:
                hall.write(player.stats() + '\n')
            with open("text_sources/hall_of_fame.txt", "r") as hall:
                cprint("""
HALL OF FAME
{}""".format(hall.read()))
            input("Press ENTER to quit")
            exit()
        elif enemy.status == "Dead":
            player.exp += 1
            goblin_count -= 1
            enemy.remove(board)
            cprint("""
You slayed {}!""".format(enemy.name))
            if player.exp % 5 == 0:
                player.level_up()
        player.status = "Ready"
        enemy.status = "Ready"

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
        """Replaces the given coordinate in board with the entity's symbol."""
        board.board[y][x] = self.sym

    def rand_spawn(self, board):
        """Replaces a random empty space in board with the entity's symbol."""
        while True:
            x = randint(0, board.size - 1)
            y = randint(0, board.size - 1)
            if board.board[y][x] == colored('O', 'grey', 'on_white'):
                board.board[y][x] = self.sym
                break

    def remove(self, board):
        """Replaces the entity in the board with 'O'."""
        x = self.getx(board)
        y = self.gety(board)
        board.board[y][x] = colored('O', 'grey', 'on_white')

    def move_valid(self, board, direction, n):
        """If move is valid return True. else return False."""
        x = self.getx(board)
        y = self.gety(board)
        if direction == 'left' or direction == 'up':
            if direction == 'up':
                y -= n
            elif direction == 'left':
                x -= n
            if x < 0 or y < 0 or board.board[y][x] != colored('O', 'grey', 'on_white'):
                return False
            else:
                return True
        else:
            if direction == 'down':
                y += n
            elif direction == 'right':
                x += n
            if x >= board.size or y >= board.size or board.board[y][x] != colored('O', 'grey', 'on_white'):
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
        board.board[original_y][original_x] = colored('O', 'grey', 'on_white')


class Player(Entity):
    """Subclass of Entity for player object including unique stats formatter and level up sequence."""
    def __init__(self, health, max_health, power, status, name, descript, role, sym, level, floor):
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
        self.exp = 0

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
    """Subclass of Entity for goblin objects including AI move generators."""


class Dungeon(object):
    """Base class to create, format and print list of lists 'board' on which gameplay takes place."""

    def __init__(self, size):
        self.size = size     
        self.board = []
        for n in range(self.size):
            self.board.append([colored('O', 'grey', 'on_white')] * self.size)

    def print_board(self):
        """Print board in formatted, front-end grid form."""
        for row in self.board:
            cprint(colored(' ', 'grey', 'on_white').join(row))

    def return_board(self):
        """Return board in formatted, front-end grid form."""
        new_board = ''
        for i, row in enumerate(self.board):
            new_board += colored(' ', 'grey', 'on_white').join(row)
            if i < self.size - 1:
                new_board += '\n'
        return new_board


#Db
player = Player(20, 20, 5, "Ready", "Player", "A test player", "Fighter", colored('P', 'cyan', 'on_white'), 1, 1)
goblin1 = Goblin(5, 5, 20, "Ready", "Trixy", "A goblin minion", "Minion", colored('G', 'red', 'on_white'))
board = Dungeon(10)

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
clear = system('cls')
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
clear = system('cls')
name = profanity.censor(input("""Hello adventurer!

What is your name?
"""))
clear = system('cls')
cprint("""One fateful night, you find yourself lost in the deep forests of Yaagnok during a violent
lightning storm. You are at least a day from town and are quickly running out of supplies. You spot a old, 
run-down tower through a clearing in the trees. The storm picks up and you are left with no choice but to
take shelter in the tower.

What kind of adventurer are you?

1. Paladin (high health, low power)
2. Fighter (medium health, medium power)
3. Rogue (low health, high power)""")
while True:
    key = ord(getch())
    if key == 49:
        player = Player(20, 20, 2, "Ready", name, "A noble warrior loyal to his faith and clergy",
                        "Paladin", colored("P", 'cyan', 'on_white'), 1, 1)
        break
    elif key == 50:
        player = Player(15, 15, 4, "Ready", name, "A master of the martial arts from young",
                        "Fighter", colored("F", 'cyan', 'on_white'), 1, 1)
        break
    elif key == 51:
        player = Player(10, 10, 6, "Ready", name, "A cunning lone wolf thief who trusts no one",
                        "Rogue", colored("R", 'cyan', 'on_white'), 1, 1)
        break
    elif key == 3:
        raise KeyboardInterrupt
clear = system('cls')
cprint("""As soon as you step inside, the rusty iron door slams shut behind you, as if pushed by some
magical force. A shrill cackle fills the air as you scan your surroundings. As the first goblins step out
of the darkness, you ready your weapon, unaware of the dangers that lie ahead.
{}

Press ENTER to start climbing Goblin Tower""".format(player.stats()))
input()
while True:
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
                     "A fast and silent killer armed with a dagger", "Assassin", colored('A', 'red', 'on_white'))
    goblin2 = Goblin(med_health, med_health, med_power, "Ready", name2,
                     "A skilled swordsman loyal to the Goblin King", "Knight", colored('K', 'red', 'on_white'))
    goblin3 = Goblin(high_health, high_health, low_power, "Ready", name3,
                     "A heavily armoured sentinel equipped with a mace", "Champion", colored('C', 'red', 'on_white'))
    player.spawn(board, 1, 1)
    goblin1.spawn(board, 0, 1)
    goblin2.rand_spawn(board)
    goblin3.rand_spawn(board)
    goblin_count = 3
    turn = 1
    while goblin_count > 0:
        #Write player and goblin turn loop here
        clear = system('cls')
        player_continue = True
        round_screen = """ROUND {}

PLAYER TURN

{}
{}""".format(turn, board.return_board(), player.stats())
        cprint(round_screen)
        cprint("""
1. Move
2. Attack""")
        while player_continue:
            key = ord(getch())
            if key == 49:
                while player_continue:
                    clear = system('cls')
                    cprint(round_screen)
                    cprint("""
What direction?""")
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
                            break
                        else:
                            cprint("""
That move is not valid!""")
                            sleep(3)
                break
            elif key == 50:
                while player_continue:
                    empty = colored('O', 'grey', 'on_white')
                    original_x = player.getx(board)
                    original_y = player.gety(board)
                    check = []
                    try:
                        check.append(board.board[original_y][original_x + 1] == empty)
                    except IndexError:
                        pass
                    try:
                        check.append(board.board[original_y][original_x - 1] == empty)
                    except IndexError:
                        pass
                    try:
                        check.append(board.board[original_y + 1][original_x] == empty)
                    except IndexError:
                        pass
                    try:
                        check.append(board.board[original_y - 1][original_x] == empty)
                    except IndexError:
                        pass
                    if all(check):
                        cprint("""
There is no one in range!""")
                        sleep(3)
                        player_continue = False
                    else:
                        adjacent = []
                        if original_x + 1 < board.size:
                            adjacent.append(board.board[original_y][original_x + 1])
                        if original_y + 1 < board.size:
                            adjacent.append(board.board[original_y + 1][original_x])
                        if original_x - 1 > -1:
                            adjacent.append(board.board[original_y][original_x - 1])
                        if original_y - 1 > -1:
                            adjacent.append(board.board[original_y - 1][original_x])
                        attack_prompt = """
Select your target.
"""
                        attack_num = 1
                        for char in adjacent:
                            if char == goblin1.sym:
                                attack_prompt += '\n' + "{}. {}".format(attack_num, goblin1.role)
                                attack_num += 1
                            elif char == goblin2.sym:
                                attack_prompt += '\n' + "{}. {}".format(attack_num, goblin2.role)
                                attack_num += 1
                            elif char == goblin3.sym:
                                attack_prompt += '\n' + "{}. {}".format(attack_num, goblin3.role)
                                attack_num += 1
                        clear = system('cls')
                        cprint(round_screen)
                        cprint(attack_prompt)
                        while player_continue:
                            key = ord(getch())
                            if key == 49 and '1' in attack_prompt:
                                break
                            elif key == 50 and '2' in attack_prompt:
                                break
                            elif key == 51 and '3' in attack_prompt:
                                break
                            elif key == 27:
                                player_continue = False
                            elif key == 3:
                                raise KeyboardInterrupt
                        if player_continue:
                            #Call damage() on selected enemy
                            exit() #Db
                break
            elif key == 3:
                raise KeyboardInterrupt
        if not player_continue:
            continue
        round_screen = """ROUND {}

PLAYER TURN

{}
{}""".format(turn, board.return_board(), player.stats())
        clear = system('cls')
        print(round_screen)
        #Goblin turn starts here
        turn += 1
        exit() #Db

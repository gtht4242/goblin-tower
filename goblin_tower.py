"""Endless turn-based, grid-based, fantasy-themed, strategy game

You must ascend Goblin Tower and reach as high a floor as possible."""
# TO-DO:
# Goblin class to handle enemy AI (use direction attribute)
#   - All goblins attack player if adjacent
#   - Else if in same row or column and path is clear, move in direction of player
#   - Else move towards player, preferably away from other goblins
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
#   - Add more context print messages
#   - Adjust sleep delays
#   - Add music (Divinity: Orginal Sin?) and SFX (via multiple instances of vlc.MediaPlayer)
#   - Add more ASCII art
#   - Add "You are the nth adventurer to enter Goblin Tower" message using a text file to store n
#   - Write proper start and gameloop functions so game can return to start screen on death
#
# To improve developer experience:
#   - Add debug tools (e.g. teleportation, quick reset of board)

from msvcrt import getch
from os import system
from random import choice, randint
from sys import exit
from time import sleep

import colorama
from profanity import profanity
from termcolor import colored, cprint
from vlc import MediaPlayer

colorama.init()
empty_char = colored('O', 'grey', 'on_white')

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
            with open("text/hall_of_fame.txt", "a") as hall:
                hall.write(player.stats() + '\n')
            with open("text/hall_of_fame.txt", "r") as hall:
                cprint(f"""
HALL OF FAME
{hall.read()}""")
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

    def spawn(self, board, x, y):
        """Replaces the given space in board with the entity's symbol."""
        board.board[y][x] = self.sym

    def rand_spawn(self, board):
        """Replaces a random empty space in board with the entity's symbol."""
        while True:
            x = randint(0, board.size - 1)
            y = randint(0, board.size - 1)
            if board.board[y][x] == empty_char:
                board.board[y][x] = self.sym
                break

    def remove(self, board):
        """Replaces the entity in the board with 'O'."""
        board.board[self.gety(board)][self.getx(board)] = empty_char

    def move_valid(self, board, direction, n):
        """If move is valid return True. else False."""
        x = self.getx(board)
        y = self.gety(board)
        if direction == 'left' or direction == 'up':
            if direction == 'up':
                y -= n
            elif direction == 'left':
                x -= n
            if x < 0 or y < 0 or board.board[y][x] != empty_char:
                return False
            else:
                return True
        else:
            if direction == 'down':
                y += n
            elif direction == 'right':
                x += n
            if x >= board.size or y >= board.size or board.board[y][x] != empty_char:
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
        board.board[original_y][original_x] = empty_char
    
    def teleport(self, board, x, y):
        """Removes current entity char on board and spawns it in space referenced by x and y."""
        self.remove(board)
        self.spawn(board, x, y)


class Player(Entity):
    """Subclass of Entity for player object including unique stats formatter and level up sequence."""
    exp = 0

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

    def stats(self):
        """Return formatted stats for player character."""
        return f"""
Name: {self.name}
Level: {self.level}
Class: {self.role}
Floor: {self.floor}
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
    """Subclass of Entity for goblin objects including enemy AI move generators."""
    direction = ''


class Dungeon(object):
    """Base class to create, format and print board."""
    board = []

    def __init__(self, size):
        self.size = size     
        for n in range(self.size):
            self.board.append([empty_char] * self.size)

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
3. Rogue (low health, high power)

DB:
4. GOD MODE
5. PLAYER DEATH""")
while True:
    key = ord(getch())
    if key == 49:
        player = Player(20, 20, 2, "Ready", name, "A noble warrior loyal to his faith and clergy",
                        "Paladin", colored("P", "cyan", "on_white"), 1, 1)
        break
    elif key == 50:
        player = Player(15, 15, 4, "Ready", name, "A master of the martial arts from young",
                        "Fighter", colored("F", "cyan", "on_white"), 1, 1)
        break
    elif key == 51:
        player = Player(10, 10, 6, "Ready", name, "A cunning lone wolf thief who trusts no one",
                        "Rogue", colored("R", "cyan", "on_white"), 1, 1)
        break
    elif key == 52:
        player = Player(1000, 1000, 1000, "Ready", name, "For debugging",
                        "GOD MODE", colored("G", "cyan", "on_white"), 4, 1)
        break
    elif key == 53:
        player = Player(0, 1000, 1000, "Ready", name, "For debugging",
                        "PLAYER DEATH", colored("D", "cyan", "on_white"), 1, 1)
        break
    elif key == 3:
        raise KeyboardInterrupt
clear = system('cls')
cprint(f"""As soon as you step inside, the rusty iron door slams shut behind you, as if pushed by some
magical force. A shrill cackle fills the air as you scan your surroundings. As the first goblins step out
of the darkness, you ready your weapon, unaware of the dangers that lie ahead.
{player.stats()}

Press ENTER to start climbing Goblin Tower""")
input()
while True:
    # Initialise variables for new floor
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
    goblins = (goblin1, goblin2, goblin3)
    player.rand_spawn(board)
    goblin1.rand_spawn(board)
    goblin2.rand_spawn(board)
    goblin3.rand_spawn(board)
    goblin_count = 3
    turn = 1
    while goblin_count > 0:
        # Player turn
        clear = system('cls')
        player_continue = True
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
                    clear = system('cls')
                    cprint(round_screen)
                    cprint("""
Select a direction with the arrow keys.""")
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
                        clear = system('cls')
                        cprint(round_screen)
                        cprint("""
Select a target.
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
                        clear = system('cls')
                        cprint(round_screen)
                        player.damage(board, attack_order[attack_target])
                        sleep(5)
                        break
                break
            elif key == 51:
                # Examine
                while player_continue:
                    clear = system('cls')
                    cprint(round_screen)
                    cprint("""
Select a target.
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
                        clear = system('cls')
                        cprint(round_screen)
                        cprint(examine_order[examine_target].stats())
                        input()
                        break
                break
            elif key == 52:
                while True:
                    clear = system('cls')
                    cprint(round_screen)
                    destination = input("""
Enter x and y coordinates of destination separated by a space.

""")
                    teleport_x = int(destination[0])
                    teleport_y = int(destination[-1])
                    destination_char = board.board[teleport_y][teleport_x]
                    if destination_char == empty_char or destination_char == player.sym:
                        break
                    else:
                        cprint("""
Destination is non-empty space!""")
                        sleep(3)
                player.teleport(board, teleport_x, teleport_y)
                player_continue = False
            elif key == 3:
                raise KeyboardInterrupt
        if not player_continue:
            continue
        round_screen = f"""ROUND {turn}

PLAYER TURN - {player.role.upper()}

{board.return_board()}
{player.stats()}"""
        clear = system('cls')
        cprint(round_screen)
        sleep(3)
        # Goblin turn
        for goblin in goblins:
            goblin_attack = False
            if goblin.is_alive():
                round_screen = f"""ROUND {turn}

GOBLIN TURN - {goblin.role.upper()}

{board.return_board()}
{player.stats()}"""
                clear = system('cls')
                cprint(round_screen)
                if goblin.adjacent(board, player):
                    goblin.damage(board, player)
                    goblin_attack = True
                    sleep(5)
                elif goblin.getx(board) == player.getx(board):
                    if goblin.gety(board) - player.gety(board) == abs(goblin.gety(board) - player.gety(board)):
                        goblin.direction = 'up'
                    else:
                        goblin.direction = 'down'
                elif goblin.gety(board) == player.gety(board):
                    if goblin.getx(board) - player.getx(board) == abs(goblin.getx(board) - player.getx(board)):
                        goblin.direction = 'left'
                    else:
                        goblin.direction = 'right'
                # Check move_valid here first?
                else:
                    # Get lengths of the two closest paths to get to same row/column as player
                    # If override, take longer path and if path lengths are equal, reset override to false
                    # Else, take shortest, clear path
                    pass
                if not goblin_attack:
                    # Check if move is valid then move
                    # If not valid, rotate direction by 90 degrees away from other entities until valid and set override to true
                    pass
                round_screen = f"""ROUND {turn}

GOBLIN TURN - {goblin.role.upper()}

{board.return_board()}
{player.stats()}"""
                clear = system('cls')
                cprint(round_screen)
                sleep(3)
        #End of round
        turn += 1

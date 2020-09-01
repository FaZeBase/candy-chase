# -*- coding: utf-8 -*-
# author: CVE-random.randint(0, 65536)


import random
import datetime
import sqlite3
from pygame import mixer

class Player :
    
    keyboard_key = {'z':(-1,0),
                    'q':(0,-1),
                    's':(1,0),
                    'd':(0,1),
                    'p':(0,0)}
    
    def __init__(self, name, enemy, points = 0, start = (0,0)):
        self.name = name
        self.points = points
        self.position = start
        self.enemy = enemy
        self.time_to_pause = datetime.timedelta(seconds=0)
        self.end = datetime.timedelta(seconds=0)

    def move (self) :    
        key = input("Mouvement (z,q,s,d) ou p pour pause : ")
        while key not in Player.keyboard_key.keys() :
            key = input("Mouvement (z,q,s,d)ou p pour pause : ")
        if key == "p" :
            begin = datetime.datetime.today()
            self.time_to_pause = Game.pause_time(begin)
        else :
            move = Player.keyboard_key[key]
            self.position = (self.position[0] + move[0], self.position[1] + move[1])
        




class Game :
    
    def __init__(self, player, music=None, database=None, size=10):
        self.player = player
        self.music = music
        self.database = database
        self.board_size = size
        self.candies = []
        self.bonus_candies = []
        self.time_candies = []
        
    # Dessine le plateau
    def draw(self):
        for line in range(self.board_size):
            for col in range(self.board_size):
                if (line,col) == self.player.enemy.position :
                    print("X",end=" ")
                elif (line,col) in self.candies :
                    print("*",end=" ")
                elif (line,col) in self.bonus_candies :
                    print("B",end=" ")
                elif (line,col) in self.time_candies :
                    print("T",end=" ")
                elif (line,col) == self.player.position :
                    print("O",end=" ")
                else : 
                    print(".",end=" ")
            print()
            
    # Fait apparaitre un bonbon et choisit le type
    def pop_candy(self):
        new_candy = (random.SystemRandom().choice(range(self.board_size)), \
        random.SystemRandom().choice(range(self.board_size)))
        candy_type = random.SystemRandom().randint(0,8)
        if new_candy not in self.candies and new_candy not in self.bonus_candies \
        and new_candy not in self.time_candies :
            self.candy_type_chooser(candy_type, new_candy)

    def candy_type_chooser(self, candy_type, new_candy):
        if 0 <= candy_type <= 4 :
            self.candies.append(new_candy)
        elif 5 <= candy_type <= 7 :
            self.bonus_candies.append(new_candy)
        else :
            self.time_candies.append(new_candy)
            
    # Regarde s'il y a un bonbon à prendre (et le prend)
    def check_candy(self):
        if self.player.position in self.candies:
            point_award = random.SystemRandom().randint(0,3)
            self.player.points += point_award
            self.candies.remove(self.player.position)
            print("+" + str(point_award) + " points")
        elif self.player.position in self.bonus_candies:
            self.bonus_candy_powerup()
        elif self.player.position in self.time_candies:
            self.time_candy_powerup()

    def bonus_candy_powerup(self):
        i = 0
        while i < 4:  
            self.pop_candy()
            i += 1
        self.bonus_candies.remove(self.player.position)
        sound = mixer.Sound('Sound/noice.ogg')
        sound.play()
        print("Noice")

    def time_candy_powerup(self) :
        bonus = datetime.timedelta(minutes=0, seconds=10)
        self.player.end += bonus
        self.time_candies.remove(self.player.position)
        sound = mixer.Sound('Sound/rewind_time.ogg')
        sound.play()
        print("+10 secondes")


        
    # Joue une partie complète
    def play(self):    
        self.music.play()
        
        print("--- Début de la partie ---")
        self.draw()
        
        self.player.end = Game.end_time(1,0)
        now = datetime.datetime.today()
        try:

            while now < self.player.end \
            and not self.out_of_bounds(self.player.position) \
            and not self.killed():
                self.enemy_turn()
                self.player.move()
                self.time_commit()
                self.check_candy()

                if random.SystemRandom().randint(1,3) == 1 :
                    self.pop_candy()

                self.draw()
	
                now = datetime.datetime.today()

            if self.out_of_bounds(self.player.position) :
                print("T'as essayé mais t'as perdu !")
                self.player.points = 0
            
            if self.killed():
                print(self.player.enemy.name + " t'a tué. La malchance...")

            if self.database != None:
                self.database.leaderboard()
                for player, score in self.database.query():
                    print("Joueur : " + player + " | Score : " + str(score))
            
        except KeyboardInterrupt: #Facon amicale de dire au revoir
            print("Merci de jouer à mon jeu. Au revoir.")
        
        finally:
            music.stop()
            print("----- Terminé -----")
            print("Vous avez", self.player.points, "points")



    @staticmethod
    # Retourne le moment où le jeu est censé être fini
    def end_time(delta_minute, delta_second):
        delta = datetime.timedelta(minutes=delta_minute, seconds=delta_second)
        end = datetime.datetime.today() + delta
        return end

    @staticmethod
    def pause_time(begin) :
        dummy_waiter = input('Jeu en pause. Appuyez sur "Enter" pour continuer ')
        cheat = datetime.timedelta(seconds=0)
        if dummy_waiter == "dad joke" :
            joke_nb = random.SystemRandom().randint(0, 2)
            if joke_nb == 0 :
                print("Quelle est la différence entre toi et une photo ?")
                print("La photo, elle, elle est développée.")
            elif joke_nb == 1 :
                print("Quel est le comble pour un prof de musique ?")
                print("C'est qu'un élève s'appelle Rémi !")
            else :
                print("Comment appelle-t-on un squelette bavard ?")
                print("Un os-parleur !")
        elif dummy_waiter == "i like memes" :
            cheat = datetime.timedelta(seconds=4206942069)
        elif dummy_waiter == "i want to die" : #Utile pour sauvegarder le score ;)
            cheat = datetime.timedelta(seconds=-4206942069)
        elif dummy_waiter == "I want to die" : #Choisis bien le code
            self.position = (-1, -1) 
        now = datetime.datetime.today()
        if cheat != datetime.timedelta(seconds=0) :
            diff = now - begin + cheat
        else:
            diff = now - begin
        return diff

    # Pour prevenir un exploit après la pause (resette à 0)
    def time_commit(self): 
        self.player.end += self.player.time_to_pause
        self.player.time_to_pause = datetime.timedelta(seconds=0)

    
    def killed(self) :
        return self.player.position == self.player.enemy.position
    
    def out_of_bounds(self, position) :    
        return position[0] < 0 \
               or position[0] > self.board_size - 1 \
               or position[1] < 0 \
               or position[1] > self.board_size - 1


    def enemy_turn(self) :
        keys = ["z","q","s","d"]
        choice = random.SystemRandom().choice(keys)
        self.player.enemy.move(choice)
        if self.out_of_bounds(self.player.enemy.position) :
            i = 0
            while self.out_of_bounds(self.player.enemy.position) \
                  and i < 3 :
                choice = random.SystemRandom().choice(keys)
                self.player.enemy.move(choice)
                i += 1
            else :
                self.player.enemy.position = (random.SystemRandom().randint(1,4), \
                random.SystemRandom().randint(1,4))
                i = 0

class Database:

    def __init__(self, game, sqlite_file="game_db.sqlite", table_name="SCORE", \
                 player_column="player", score_column="score"):
        self.sqlite_file = sqlite_file
        self.table_name = table_name
        self.player_column = player_column
        self.score_column = score_column
        self.name_type = 'TEXT'
        self.score_type = 'INTEGER'
        self.game = game
        self.player_name = self.game.player.name
        self.player_score = self.game.player.points
        
    def leaderboard(self):
        # Connection au BD et ouverture du "terminal"
        connection = sqlite3.connect(self.sqlite_file)
        term = connection.cursor()
        self.player_score = self.game.player.points
        # Creation et mise en leaderboard du joueur
        term.execute("""CREATE TABLE IF NOT EXISTS {tn}
                ({pc} {nt} PRIMARY KEY, {sc} {st})""" \
                .format(tn=self.table_name, pc=self.player_column, nt=self.name_type, \
                        sc=self.score_column, st=self.score_type))
        term.execute("INSERT OR REPLACE INTO {tn} VALUES('{pn}', {ps})" \
                .format(tn=self.table_name, pn=self.player_name, ps=self.player_score))


        # Sauvegarde et fermeture de la connection
        connection.commit()
        connection.close()

    def query(self):
        connection = sqlite3.connect(self.sqlite_file)
        term = connection.cursor()
        
        term.execute(("SELECT * FROM {tn} ORDER BY {sc} DESC LIMIT 10") \
                     .format(tn=self.table_name, sc=self.score_column))
        return term.fetchall()

        connection.commit()
        connection.close()


class Music: # Classe interface de PyGame Mixer

    def __init__(self, filename, loop=False):
        self.filename = filename
        self.loop = loop
        mixer.init()
        mixer.music.load(self.filename)

    def play(self):
        
        if self.loop:
            mixer.music.play(loops=-1)
        else:
            mixer.music.play()

    def stop(self, fade_time=500):
        mixer.music.fadeout(fade_time)
        
class Enemy (Player):
        
                    
        def __init__(self, name="Jeff"):
            self.position = (random.SystemRandom().randint(1,4), \
            random.SystemRandom().randint(1,4))
            self.name = name
        
        def move(self, choice):
            move = Player.keyboard_key[choice]
            self.position = (self.position[0] + move[0], \
            self.position[1] + move[1])
        
    
if __name__ == "__main__" :
    try:
        music = Music("Sound/background.mp3", True)
        name = input("Votre nom s'il vous plaît : ")
        while not name:
            name = input("Votre nom s'il vous plaît : ")
        enemy = Enemy()
        player = Player(name, enemy)
        game = Game(player)
        db = Database(game)
        size = int(input("La taille du tableau de jeu :"))
        while not 5 <= size <= 20:
            size = int(input("La taille du tableau de jeu :"))
        game = Game(player, music, db, size) 
        game.play()
    except KeyboardInterrupt:
        print("Merci pour le vent...")

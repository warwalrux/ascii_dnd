#!/usr/bin/env python3

from random import randint, choice
import subprocess
import platform
import time
import os
import pprint
import json
import argparse
import yaml
import functools
import logging
import sys

logging.basicConfig(level=logging.DEBUG, filename="ascii_dnd.log")

ASCII_DND_DIR = os.environ['ASCII_DND_DIR']
pp = pprint.PrettyPrinter()

# Map things
class MapGenerator():
    """ Draws a map of a given height and width """
    def __init__(self):
        """ New room instance """
    
    def draw_grid(self, room, player_locs, width=2):
        print(player_locs)
        for y in range(room.data["height"]):
            for x in range(room.data["width"]):
                if (x, y) in room.walls:
                    symbol = "^"
                elif (x, y) in player_locs:
                    symbol = "@"
                elif (x, y) in room.exits:
                    symbol = "#"
                elif (x, y) in room.loot:
                    symbol = "$"
                elif (x, y) in room.enemies:
                    symbol = "&"
                else:
                    symbol = "."
                print("%%-%ds" % width % symbol, end="")
            print()
    
    def clear(self):
        subprocess.Popen("cls" if platform.system() == "Windows" else "clear", shell=True)
        time.sleep(0.01)

class Room():
    data = {}
    loot = {}
    walls = {}
    exits = {}
    enemies = {}

    def __init__(self, room_data):
        logging.debug("generating room: %s", room_data["name"])
        self.data = room_data
        self.loot = self.__gen_loot()
        self.walls = self.__gen_walls()
        self.exits = self.__gen_exits()
        self.enemies = self.__gen_enemies()

    def __gen_loot(self, pct=0.25):
        logging.debug("generating loot.")
        retval = []
        for loot in self.data["loot"]:
            x = randint(1, self.data["width"] - 2)
            y = randint(1, self.data["height"] - 2)
            retval.append((x, y))
        return retval
    
    def __gen_enemies(self, pct=0.25):
        if "enemies" in self.data:
            logging.debug("generating enemies.")
            retval = []
            for enemy in self.data["enemies"]:
                x = randint(1, self.data["width"] - 2)
                y = randint(1, self.data["height"] - 2)
                retval.append((x, y))
            return retval
        else:
            return None
    
    def __gen_walls(self, pct=0.25):
        logging.debug("generating walls.")
        retval = []
        for i in range(int(self.data["height"] * self.data["width"] * pct) // 2):

            x = randint(1, self.data["width"] - 2)
            y = randint(1, self.data["height"] - 2)

            retval.append((x, y))
            retval.append((x + choice([-1, 0, 1]), y + choice([-1, 0, 1])))
        return retval

    def __gen_exits(self):
        retval = []
        for exit in self.data["exits"]:
            if "north" in exit:
                x = randint(1, self.data["width"] -2)
                y = 0
                retval.append((x, y))
            if "south" in exit:
                x = randint(1, self.data["width"] -2)
                y = self.data["height"]
                retval.append((x, y))
            if "east" in exit:
                x = 0
                y = randint(1, self.data["heigh"] -2)
            if "west" in exit:
                x = self.data["height"]
                y = randint(1, self.data["heigh"] -2)
                retval.append((x, y))

        return retval

class Character():
    data = None
    player_pos = None
    def __init__(self, data, player_pos=(0, 0)):
        self.data = data
        self.player_pos = player_pos
   
class Game():
    def __init__(self, game_data):
        logging.info("loading game data...")
        self.game_data = game_data
        self.players = self.__load_players()
        self.rooms = self.__load_rooms()

    def __load_players(self):
        logging.debug("loading players from file")
        players = []
        for player in self.game_data["players"]:
            player_data = json.load(open(os.path.join(ASCII_DND_DIR, "characters", "%s.json" % player), "r"))
            players.append(Character(player_data))
        return players
    

    def __load_rooms(self):
        logging.info("loading dungeon...")
        retval = []
        for room in self.game_data["rooms"]:
            retval.append(Room(room))
        return retval

    def take_turn(self, stage, room, player):
        ap = int(player.data["sheet_data"]["jsondata"]["speed"])
        name = player.data["sheet_data"]["jsondata"]["name"]
        p_ref = self.players.index(player)

        def __retry():
            self.take_turn(stage, room, player)

        def __draw_screen(room, player_locs, messages=None):
            stage.clear()
            stage.draw_grid(room, player_locs)
            if messages:
                print()
                for message in messages:    
                    print(message)
                    print()

        def __prompt_move(ap):
            while ap >= 1:
                logging.debug("prompting for move")
                logging.debug("player current_pos: %s", str(player.player_pos))
                __draw_screen(room, [ p.player_pos for p in self.players ], [ "%s -- %s" % (name, ap) ])
                direction = input("WASD to move, enter to submit: ")
                
                x = self.players[p_ref].player_pos[0]
                y = self.players[p_ref].player_pos[1]
                
                pos = None

                # Up
                if direction[0] == "w":
                    pos = (x, y - 1)
                # Left
                elif direction[0] == "a":
                    pos = (x - 1, y)
                # Right
                elif direction[0] == "d":
                    pos = (x + 1, y)
                # Down
                elif direction[0] == "s":
                    pos = (x, y + 1)
                else:
                    raise Exception
                    
                if pos in room.walls:
                    __prompt_move(ap)
              
                if pos in room.exits:

                else:
                    self.players[p_ref] = Character(player.data, pos)

        
        __draw_screen(room, [ p.player_pos for p in self.players ])
        choice = input("m to move, a to attack, e for inventory, q to quit: ")

        if choice == "m":
            __prompt_move(ap)
        elif choice == "q":
            sys.exit(0)
        else:
            __retry()

    def start(self):
        stage = MapGenerator()
        for room in self.rooms:
            stage.clear()
            for player in self.players:
                is_turn = True
                while is_turn:
                    self.take_turn(stage, room, player)
                    is_turn = False
                print("Turn Complete!")
            

def main():
    logging.debug("Starting new game...")
    parser = argparse.ArgumentParser(description="ASCII DND")
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument('-n', '--new-game', help="start a new game")
    actions.add_argument('-l', '--load-game', help="load an old game")
    args = parser.parse_args()

    if args.new_game:
        logging.debug("loading %s", args.new_game)
        data = yaml.safe_load(open(os.path.join(ASCII_DND_DIR, "game_scripts", "%s.yml"%args.new_game), "r"))
        quest = Game(data)
        quest.start()


if __name__ == "__main__":
    main()

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

ASCII_DND_DIR = os.environ['ASCII_DND_DIR']
pp = pprint.PrettyPrinter()

# Map things
class MapGrid():
    """ Draws a map of a given height and width """
    def __init__(self, width, height, players):
        """ New room instance """
        self.width = width
        self.height = height
        self.walls = []
        self.start = (0, 0)
        self.goal = (width - 1, height - 1)
        self.players = players

    def move_player(self, d, player):
        """Move a player"""
        pp.pprint(player)
        x = player.player_pos[0]
        y = player.player_pos[1]
        pos = None

        # Up
        if d[0] == "w":
            pos = (x, y - 1)
        # Left
        if d[0] == "a":
            pos = (x - 1, y)
        # Right
        if d[0] == "d":
            pos = (x + 1, y)
        # Down
        if d[0] == "s":
            pos = (x, y + 1)

        if pos not in self.walls:
            player.player_pos = pos

        if pos == self.goal:
            print("You made it to the end!")


    def draw_grid(self, width=2):
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.walls:
                    symbol = "^"
                elif (x, y) in self.players:
                    symbol = "$"
                elif (x, y) == self.start:
                    symbol = "<"
                elif (x, y) == self.goal:
                    symbol = ">"
                else:
                    symbol = "."
                print("%%-%ds" % width % symbol, end="")
            print()
    
    def clear(self):
        subprocess.Popen("cls" if platform.system() == "Windows" else "clear", shell=True)
        time.sleep(0.01)

class Obstacles():
    def __init__(self, grid: MapGrid):
        self.grid = grid

    def gen_cavern(self, pct=0.25):
        out = []
        for i in range(int(self.grid.height * self.grid.width * pct) // 2):

            x = randint(1, self.grid.width - 2)
            y = randint(1, self.grid.height - 2)

            out.append((x, y))
            out.append((x + choice([-1, 0, 1]), y + choice([-1, 0, 1])))
        return out

class Character():
    def __init__(self, name):
        self.data = json.load(open(os.path.join(ASCII_DND_DIR, "characters", "%s.json" % name), "r"))
        self.player_pos = (0, 0)

class Game():
    def __init__(self, game_data):
        self.game_data = game_data
        self.players = self.__load_players()
 
    def __load_players(self):
        players = []
        for player in self.game_data["players"]:
            players.append(Character(player))
        return players

    def __take_turn(self, room, player):
        while player.player_pos != room.goal:
            room.draw_grid()
            d = input("Which way? (WASD)")[0]
            player.player_pos = room.move_player(d, player)
            room.clear()

    def start(self):
        for room in self.game_data["rooms"]:
            room = MapGrid(room["width"], room["height"], self.players)
            generator = Obstacles(room)
            room.walls = generator.gen_cavern()
            for player in self.players:
                self.__take_turn(room, player)
            

def main():
    parser = argparse.ArgumentParser(description="ASCII DND")
    parser.add_argument('-s', '--script', help="Game script")
    args = parser.parse_args()

    data = yaml.safe_load(open(args.script, "r"))
    quest = Game(data)
    quest.start()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from ascii_dnd import Game
import argparse
import yaml

def main():
    parser = argparse.ArgumentParser(description="ASCII DND")
    parser.add_argument('-s', '--script', help="Game script")
    args = parser.parse_args()

    data = yaml.safe_load(open(args.script, "r"))
    print(data)
    quest = Game(data)
    quest.start()



if __name__ == "__main__":
    main()

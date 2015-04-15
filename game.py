#!/usr/bin/env python

import argparse, sys

from libraries.engine import Game


def usage(error_code=None):
    print 'game.py -m <module> -f'
    sys.exit(error_code)


def main(argv):
    module_name = None
    fullscreen = False

    parser = argparse.ArgumentParser()
    parser.add_argument('module_name', metavar='module', type=str, help='module name to use')
    parser.add_argument('-f', '--fullscreen', dest='fullscreen', action='store_true')

    args = parser.parse_args()

    game = Game(module_name=args.module_name, fullscreen=args.fullscreen)
    game.run()


if __name__ == '__main__':
   main(sys.argv[1:])

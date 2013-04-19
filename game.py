#!/usr/bin/env python
import sys

from libraries.engine import Game

if __name__ == "__main__" :
    if len(sys.argv) == 1:
        print 'Specify module name'
        exit(1)
    game = Game(module_name=sys.argv[1], debug=False)
    game.run()

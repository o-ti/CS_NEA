#PyGame Modules
import pygame
from pygame.locals import *
import sys

#Import Game class
from game import Game

#Global settings
REFRESH_RATE = 90
HEIGHT = 1080
WIDTH = 1920

#Game class
g = Game(WIDTH, HEIGHT, REFRESH_RATE)

#Run the game
g.run()

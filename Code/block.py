import pygame
from pygame.locals import *
from utils import Utility as U

class Block(pygame.sprite.Sprite):

    #Length1 is in the x direction
    #Length2 is in the y direction
    def __init__(self, centre, length1, length2, colour, SCREEN_DIMS, camera_position):

        pygame.sprite.Sprite.__init__(self)

        self.centre = centre
        self.length1 = length1
        self.length2 = length2
        self.colour = colour

        self.initial_screenPosition = U.convertToScreen(camera_position, self.centre, SCREEN_DIMS)
        self.rect = pygame.Rect(self.initial_screenPosition[0], self.initial_screenPosition[1], self.length1, self.length2)

    def render(self, display, camera_position, directions, dt, SCREEN_DIMS, zoom):

        self.rect.center = U.convertToScreen(camera_position, self.centre, SCREEN_DIMS, zoom)

        if zoom != 1:
            scaled_rect = self.rect.scale_by(zoom)
            pygame.draw.rect(display, self.colour, scaled_rect)
        else:
            pygame.draw.rect(display, self.colour, self.rect)

    def getCorners(self):
        #TL, BL, BR, TR
        corners = []

        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                corners.append(U.vecAdd(self.centre, [i * self.length1/2, i * j * self.length2/2]))

        return corners

    def getEdges(self):
        #Get the corners
        corners = self.getCorners()

        #Decompose the rectangle into 4 lines: TL -> TR, TR -> BR, BR -> BL, BL -> TL
        
        #Top, Right, Bottom, Left
        lines = [[corners[i], corners[i+1]] for i in range(-1, 3)]

        return lines


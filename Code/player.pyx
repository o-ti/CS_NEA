import pygame
from pygame.locals import *
from weapon import Weapon
from utils import Utility as U
from math import sqrt, pi

import pygame.freetype

pygame.freetype.init()
text_font = pygame.freetype.SysFont('iosevka', 48)
zoomed_out = pygame.freetype.SysFont('iosevka', 24)

class Player(pygame.sprite.Sprite):

    def __init__(self, spawn_point, initial_forward_vec, team, weapon):

        #Initialise the PyGame sprite
        pygame.sprite.Sprite.__init__(self)

        #Where the player will spawn every time they are killed
        self.spawn_point = spawn_point

        #The direction the player will face when they are respawned
        self.initial_forward_vec = initial_forward_vec

        #The maximum health that the player can have at any time
        self.max_health = 100

        #The current health of the player
        self.health = 100

        #The maximum magnitude of the velocity
        self.max_speed = 1000

        #Which team the player is on, it will be an integer (0 or 1)
        #To check for a hit between two enemies
        #XOR the teams of the two players involved (0 means no hit, 1 means hit)
        self.team = team

        #Set team colour
        self.colours = {0: (0, 100, 100),
                        1: (100, 20, 0)
                        }

        self.colour = self.colours[team]

        #The player's Weapon
        self.weapon = weapon

        #Current position of the players
        self.position = self.spawn_point

        #Current direction of the player
        self.forward_vec = self.initial_forward_vec

        if self.initial_forward_vec == [0, -1]:
            self.movement_multiplier = -1
        else:
            self.movement_multiplier = 1

        #Radius of the circle representing the player
        self.radius = 75

        #For AI use only, will be the action of the model
        self.rotation_rate = 0

        #Dash range
        self.dashRange = 600

        self.spoke_range = self.weapon.range

    #Move the player based on the directions
    def movePlayer(self, directions, dt):
        #directions = [horizontal input, vertical input]

        #Used to normalise directions
        magnitude = sqrt(U.dot(directions, directions))

        #If no movement, break
        if magnitude == 0:
            return None

        #Calculate movement in the frame
        frameMovement = U.mult(directions, self.movement_multiplier * dt * self.max_speed/magnitude)

        #Orient the player movement properly
        frameMovement[0] *= -1

        #Update position
        updatedPosition = U.vecAdd(self.position, frameMovement)

        #Position must be inside of the field
        for i in range(2):
            
            if updatedPosition[i] - self.radius <= 0:
                updatedPosition[i] = self.radius

            elif updatedPosition[i] + self.radius >= 4000:
                updatedPosition[i] = 4000 - self.radius

        #Set new position
        self.position = updatedPosition

    #Upon event will fire the weapon in the specified class
    #Returns ray produced and information about the ray
    def fire(self):
        return self.weapon.fire(self.position, self.forward_vec)

    #Update the player state
    def updatePlayerState(self, action, countdown, dt):

        #Get the directions from the action
        directions = [action["right"], action["forward"]]

        #Move the player
        self.movePlayer(directions, dt)

        #If dt != 0 we want to turn
        if dt != 0:
            angleTurned = action["rot_rate"] * dt
            self.forward_vec = U.rotateVector(self.forward_vec, angleTurned)

        #Array of [Position, Final Extent, Damage]
        if action["firing"] and countdown <= 0:
            weaponRay = self.fire()
            fired = True
        else:
            weaponRay = []
            fired = False

        return weaponRay, fired


    #Renders the character to the display of the player
    def render(self, display, camera_position, SCREEN_DIMS, zoom):

        #Find relative posistion
        rel_pos = U.convertToScreen(camera_position, self.position, SCREEN_DIMS, zoom)

        #Draw the circle
        pygame.draw.circle(display, self.colour, rel_pos, self.radius * zoom)

        #Final extent of the forward vector
        for_pos = U.vecAdd(U.mult(self.forward_vec, 100*zoom), rel_pos)

        #Draw anti-aliased line for forward vector
        pygame.draw.aaline(display, (0, 0, 0), rel_pos, for_pos)

        #Create text surface of the health

        if zoom == 1:
            self.text_surface, self.text_rect = text_font.render(str(self.health), fgcolor=(255,255,255), bgcolor=self.colour)
        else:
            self.text_surface, self.text_rect = zoomed_out.render(str(self.health), fgcolor=(255,255,255), bgcolor=self.colour)

        #Set text position
        self.text_rect.center = rel_pos

        #Blit the text
        display.blit(self.text_surface, self.text_rect)

    def reset(self):
        self.position = self.spawn_point
        self.forward_vec = self.initial_forward_vec
        self.rotation_rate = 0
        self.health = self.max_health

    def getCorners(self):
        #TL, BL, BR, TR
        corners = []

        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                corners.append(U.vecAdd(self.position, [i * self.radius, i * j * self.radius]))

        return corners

    def getEdges(self):
        #Get the corners
        corners = self.getCorners()

        #Decompose the rectangle into 4 lines: TL -> TR, TR -> BR, BR -> BL, BL -> TL
        
        #Top, Right, Bottom, Left
        lines = [[corners[i], corners[i+1]] for i in range(-1, 3)]

        return lines

    def detectionSpokes(self):

        #Get all direction vectors
        #Set all to correct length
        #return

        spokeVectors = []

        deltaAngle = pi / 4

        for i in range(0, 8):
            direction = U.mult(U.rotateVector(self.forward_vec, deltaAngle * i), self.spoke_range)
            spokeVectors.append([self.position, U.vecAdd(self.position, direction)])

        return spokeVectors
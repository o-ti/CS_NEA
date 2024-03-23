# PyGame modules
from player import Player
from weapon import *
from block import Block

from utils import Utility as U
from math import sqrt

class GameLoop:

    def __init__(self):

        # Initialise the clock, and set the refresh rate
        self.REFRESH_RATE = 240

        # We will have an array of all of the objects in the map, and where they are
        # Each object will have its own rendering class
        # [identifier, position, direction, object]

    # Checks for hits between rays and objects in the map
    def handlePlayerCollisions(self):
        for player in self.players:
            playerCircle = [player.position, player.radius]
            for collision_player in self.players:
                if collision_player != player:
                    hitResult = U.circleCircleCollision(
                        playerCircle, [collision_player.position, collision_player.radius]
                    )
                    if hitResult[0] == True:
                        player.position = U.vecAdd(player.position, hitResult[1])
                        collision_player = U.vecSub(collision_player.position, hitResult[1])


    def handleBlockCollisions(self, player1):

        for player in self.players:
            for block in self.blocks:
                #Do dat thing
                delta = U.circleRectCollision(player, block)
                if delta[0]:
                    player.position = U.vecAdd(player.position, delta[1])


    def handleRayCollisions(self, rays):
        
        #Dicts for credit
        damageCredit = {p: 0 for p in self.players}
        eliminationCredit = {p: 0 for p in self.players}
        deathCredit = {p: 0 for p in self.players}

        #Iterate through all players
        for player_i in self.players:
            firedRays = rays[player_i]

            for ray in firedRays:

                #Larger than possible hit range
                t = 2
                bestHit = None
                
                #Line we want to test with
                line = ray[0:2]

                #Iterate through all blocks
                for block in self.blocks:

                    #Determine whether a result is met
                    hitResult = U.lineRectCollision(line, block)

                    #If a hit has occurred
                    if hitResult[0]:

                        #If the result is closer
                        if hitResult[1] < t:

                            #Reassign the hit result
                            t = hitResult[1]


                #Iterate through test players
                for testPlayer in self.players:

                    #Don't check if test is the player
                    if testPlayer != player_i and testPlayer.team != player_i.team:

                        #Player circle
                        circle = [testPlayer.position, testPlayer.radius]

                        #Check if hit has occurred
                        hitResult = U.lineCircleCollision(line, circle)

                        #Is there a hit, and was it closer
                        if hitResult[0] and t > hitResult[1]:

                            #If so, update bestHit and min t
                            t = hitResult[1]
                            bestHit = testPlayer

                #If hit registered
                if bestHit:

                    #Reduce health of player which was killed
                    bestHit.health -= ray[2]
                    
                    #If player died
                    if bestHit.health <= 0:

                        #Reset the player
                        bestHit.reset()

                        #Add elim credit to player_i
                        eliminationCredit[player_i] += 1

                        #Add death credit to player which died
                        deathCredit[bestHit] += 1

                    #Add damage credit to player_i for the hit
                    damageCredit[player_i] += ray[2]


        return damageCredit, eliminationCredit, deathCredit


    def run(self, returnValues):

        #Dt for frame-rate independent physics
        dt = 1 / self.REFRESH_RATE

        # Team 1
        player1 = Player([self.pos_x - 500, self.pos_y + 400], [0, -1], 0, AssaultRifle(self.REFRESH_RATE))
        player2 = Player([self.pos_x, self.pos_y + 400], [0, -1], 0, AssaultRifle(self.REFRESH_RATE)
        )
        player3 = Player([self.pos_x + 500, self.pos_y + 400], [0, -1], 0, SniperRifle(self.REFRESH_RATE)
        )

        # Team 2
        player4 = Player([self.pos_x - 500, self.pos_y], [0, 1], 1, Shotgun(self.REFRESH_RATE))
        player5 = Player([self.pos_x, self.pos_y], [0, 1], 1, AssaultRifle(self.REFRESH_RATE))
        player6 = Player([self.pos_x + 500, self.pos_y], [0, 1], 1, SniperRifle(self.REFRESH_RATE))

        # Contains all of the players in the game
        self.players = [player1, player2, player3, player4, player5, player6]

        #Block 1
        block1 = Block([self.pos_x - 500, self.pos_y + 200], 100, 100)

        #List of all blocks
        self.blocks = [block1]

        countdowns = {p: 0 for p in self.players}

        #Main loop
        running = True

        while running:

            rays = {}
            #Update player states
            for i, player in enumerate(self.players, 0):
                rays[player], fired = player.updatePlayerState(model_predictions[i], countdowns[player], dt)
                if fired:
                    countdowns[player] = player.weapon.maxFrameCooldown
                else:
                    countdowns[player] -= 1

            #Handle collision
            self.handlePlayerCollisions()
            self.handleBlockCollisions()
            
            #Handle ray collisions
            deltaDamageCredit, deltaEliminationCredit, deltaDeathCredit = self.handleRayCollisions(rays, player1.position)

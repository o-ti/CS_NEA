from pettingzoo import ParallelEnv
from training.momentum_env.weapon import Weapon, Shotgun, AssaultRifle, SniperRifle
from training.momentum_env.player import Player
from training.momentum_env.block import Block
from training.momentum_env.utils import Utility as U
import numpy as np

import functools
from copy import copy

from gymnasium.spaces import Discrete, MultiBinary, Dict, Box, Tuple
from gymnasium.spaces.utils import flatten_space
from math import pi

class Momentum(ParallelEnv):
    metadata = {
        "name": "momentum_env",
    }

    def __init__(self, set_seed=42):
        self.REFRESH_RATE = 90
        self.dt = 1 / self.REFRESH_RATE

        # Team 1
        self.player1 = Player([1500, 3000], [0, -1], 0, Shotgun(self.REFRESH_RATE))
        self.player2 = Player([2000, 3000], [0, -1], 0, AssaultRifle(self.REFRESH_RATE)
        )
        self.player3 = Player([2500, 3000], [0, -1], 0, SniperRifle(self.REFRESH_RATE)
        )

        # Team 2
        self.player4 = Player([2500, 1000], [0, 1], 1, Shotgun(self.REFRESH_RATE))
        self.player5 = Player([2000, 1000], [0, 1], 1, AssaultRifle(self.REFRESH_RATE))
        self.player6 = Player([1500, 1000], [0, 1], 1, SniperRifle(self.REFRESH_RATE))

        # Contains all of the players in the game
        self.players = [self.player1, self.player2, self.player3, self.player4, self.player5, self.player6]

        #Blocks
        self.block1 = Block([1500, 2000], 200, 1200)
        self.block2 = Block([2500, 2000], 200, 1200)
        #self.block3 = Block([1000, 2000], 400, 400)
        #self.block4 = Block([2000, 2000], 400, 400)
        #self.block5 = Block([3000, 2000], 400, 400)

        self.borderLeft = Block([1000-10, 2000], 20, 4000)
        self.borderRight = Block([4010- 1000, 2000], 20, 4000)
        self.borderTop = Block([2000, 500-10], 4040, 20)
        self.borderBottom = Block([2000, 4010-500], 4040, 20)

        #List of all blocks
        self.blocks = [self.block1, self.block2, self.borderLeft, self.borderRight, self.borderTop, self.borderBottom]#, self.block3, self.block4, self.block5]

        #Set countdowns
        self.countdowns = {p: 0 for p in self.players}

        #Access player object using string
        self.playerLabel = {"player1": self.player1,
                            "player2": self.player2,
                            "player3": self.player3,
                            "player4": self.player4,
                            "player5": self.player5,
                            "player6": self.player6,
        }

        #Access player string using player object
        self.invPlayerLabels = {self.player1: "player1",
                                self.player2: "player2",
                                self.player3: "player3",
                                self.player4: "player4",
                                self.player5: "player5",
                                self.player6: "player6",
        }

        #Player strings
        self.possible_agents = ["player1", "player2", "player3", "player4", "player5", "player6"]

        #Current timestep
        self.timesteps = 0

        self.agent_selection = copy(self.possible_agents)

        #Max timesteps in a game
        self.max_timestep = 3000

        self.scores = {0: 0, 
                       1: 0}

        self.max_score = 1200

        #self.num_agents = 6
        #self.max_num_agents = 6

        self.agents = copy(self.possible_agents)


        # obs_space = flatten_space(Dict({
        #     "distances": Box(low=0, high=1, shape=(8,), dtype=np.float32),
        #     "healths": Box(low=0, high=100, shape=(8,), dtype='i'),
        #     "alliances": Box(low=-1, high=1, shape=(8,), dtype='i'),
        #     "player_health": Discrete(101, start=0),
        #     "can_fire": MultiBinary(1),
        # }), )

        low_obs = [0] * 8 + [0] * 8 + [-1]*8 + [0] + [0]
        high_obs = [1] * 8 + [100] * 8 + [1]*8 + [100] + [1]

        obs_space = Box(low=np.array(low_obs), high=np.array(high_obs), shape=(26,), dtype=np.float32)

        self.observation_spaces = {a: obs_space for a in self.agents}

        # action_space = flatten_space(Dict({
        #     "forward": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
        #     "right": Box(low=-1, high=1, shape=(1,), dtype=np.float32),
        #     "rot_rate": Box(low=-pi, high=pi, shape=(1,), dtype=np.float32),
        #     "firing": MultiBinary(1),
        # }))

        low_act = [-1, -1, -pi, 0]
        high_act = [1, 1, pi, 1]

        action_space = Box(low=np.array(low_act), high=np.array(high_act), shape=(4,), dtype=np.float32)

        self.action_spaces = {a: action_space for a in self.agents}


    #Nothing to really do here
    def set_seed(self, seed):
        pass

    # Checks for hits between rays and objects in the map
    def handlePlayerCollisions(self):

        #Iterate through players
        for player in self.players:

            #Get player circle
            playerCircle = [player.position, player.radius]

            #Iterate through all possible collisions
            for collision_player in self.players:

                #Don't self-check
                if collision_player != player:

                    #Collision checking
                    hitResult = U.circleCircleCollision(playerCircle, [collision_player.position, collision_player.radius])

                    #If a collision happened
                    if hitResult[0] == True:

                        #Resolve it
                        player.position = U.vecAdd(player.position, hitResult[1])
                        collision_player = U.vecSub(collision_player.position, hitResult[1])

    #Collisions with the blocks
    def handleBlockCollisions(self):

        #Iterate through all players
        for player in self.players:

            #Iterate through all blocks
            for block in self.blocks:

                #Check for collision
                delta = U.circleRectCollision(player, block)

                #Resolve
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

    def getObservations(self, player):

        spokes = player.detectionSpokes()

        distances = []
        healths = []
        alliances = []

        for spoke in spokes:


            #Larger than possible hit range
            t = 2
            bestHit = None
            
            #Line we want to test with
            line = spoke

            #Block hit
            blockHit = False


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
                        blockHit = True


            #Iterate through test players
            for testPlayer in self.players:

                #Don't check if test is the player
                if testPlayer != player:

                    #Player circle
                    circle = [testPlayer.position, testPlayer.radius]

                    #Check if hit has occurred
                    hitResult = U.lineCircleCollision(line, circle)

                    #Is there a hit, and was it closer
                    if hitResult[0] and t > hitResult[1]:

                        #If so, update bestHit and min t
                        t = hitResult[1]
                        bestHit = testPlayer
                        blockHit = False
                            
            #Case 1
            if not blockHit and not bestHit:
                distances.append(0)
                healths.append(0)
                alliances.append(0)

            #Case 2
            if not blockHit and bestHit:
                if bestHit.team == player.team:
                    team = 1
                else:
                    team = -1
                distances.append(1-t)
                healths.append(bestHit.health)
                alliances.append(team)

            #Case 3
            if blockHit and not bestHit:
                distances.append(1-t)
                healths.append(0)
                alliances.append(0)

        #Add player information
        #Add player health
        #Add whether player is on cooldown or not

        countdown = self.countdowns[player]
        if countdown <= 0:
            can_fire = True
        else:
            can_fire = False

        # observation = {
        #     "distances": distances,
        #     "healths": healths,
        #     "alliances": alliances,
        #     "player_health": player.health,
        #     "can_fire": can_fire,
        # }

        observations = distances + healths + alliances
        observations.append(player.health)
        observations.append(can_fire)

        #obs = {self.invPlayerLabels[player]: observations, 'mask': [True, True, True, True]}

        return observations

    def reset(self, seed=None, options=None):

        self.agents = copy(self.possible_agents)

        for player in self.players:
            player.reset()

        #Reset countdowns
        self.countdowns = {p: 0 for p in self.players}

        self.timesteps = 0

        infos = {a: {} for a in self.agents}

        observations = {a: self.getObservations(self.playerLabel[a]) for a in self.agents}

        rewards = {a: 0 for a in self.agents}
        terminations = {a: False for a in self.agents}
        truncations = {a: False for a in self.agents}
        
        self.lastVals = observations, rewards, terminations, truncations, infos

        return observations, infos

    def step(self, actions):

        rays = {}

        #Update player states
        for i, player in enumerate(self.players, 0):

            playerStringLabel = self.invPlayerLabels[player]
            playerActions = actions[playerStringLabel]

            if playerActions[3] > 0.5:
                firing = True
            else:
                firing = False
            
            action = {"forward": playerActions[0],
                    "right": playerActions[1],
                    "rot_rate": playerActions[2],
                    "firing": firing}

            rays[player], fired = player.updatePlayerState(action, self.countdowns[player], self.dt)

            if fired:
                self.countdowns[player] = player.weapon.maxFrameCooldown
            else:
                self.countdowns[player] -= 1

        #Handle collision
        self.handlePlayerCollisions()
        self.handleBlockCollisions()
        
        #Handle ray collisions
        deltaDamageCredit, deltaEliminationCredit, deltaDeathCredit = self.handleRayCollisions(rays)        
        

        #Create rews
        rewards = {a: 0 for a in self.agents}

        #Attribute rewards
        for player in self.players:
            rew = deltaDamageCredit[player]/20 + deltaEliminationCredit[player] * 5 - 3.5 * deltaDeathCredit[player] -  (abs(2000 - player.position[1]))/2000
            if playerActions[3] and deltaDamageCredit[player] == 0:
                rew -= 0.1
            a = self.invPlayerLabels[player]
            rewards[a] = rew

        #Adjust score
        for player in self.players:
            deltaScore = deltaDamageCredit[player] + deltaEliminationCredit[player] * 75
            self.scores[player.team] += deltaScore

        #Truncation conditions
        truncations = {a: False for a in self.agents}
        if self.timesteps > self.max_timestep:
            truncations = {a: True for a in self.agents}

        #Termination condition
        terminations = {a: False for a in self.agents}
        for i in range(0, 2):
            if self.scores[i] > self.max_score:
                for player in self.players:
                    a = self.invPlayerLabels[player]
                    if player.team == i:
                        rewards[a] += 10
                    else:
                        rewards[a] -= 10

        #Get observations
        observations = {a: self.getObservations(self.playerLabel[a]) for a in self.agents}

        #Additional info - dummy
        infos = {a: {} for a in self.agents}

        #If terminated
        if any(terminations.values()) or all(truncations.values()):
            self.agents = []

        #Increment timestep
        self.timesteps += 1

        self.lastVals = observations, rewards, terminations, truncations, infos

        return observations, rewards, terminations, truncations, infos

    def render(self):
        pass

    def observation_space(self, agent):
        return self.observation_spaces[agent]

    def action_space(self, agent):
        return self.action_spaces[agent]

    def last(self, something):
        return self.lastVals



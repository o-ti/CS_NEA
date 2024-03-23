# PyGame modules
import pygame
from pygame.locals import *
import sys


# Menu, Player, Weapon classes
from menu import *
from player import Player
from weapon import *
from block import Block

from utils import Utility as U
from math import sqrt, pi

import time

from tensordict import TensorDict
import torch

import pygame.freetype
pygame.freetype.init()
text_font = pygame.freetype.SysFont('iosevka', 100)



from agents import MomentumAgents

class Game:

    # Initialise the game class
    def __init__(self, WIDTH, HEIGHT, REFRESH_RATE):

        # Initialise PyGame and the screen
        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), vsync=1, flags=DOUBLEBUF)
        #self.screen.set_alpha(None)

        pygame.display.set_caption("Momentum")
        pygame.display.set_icon(pygame.image.load("assets/momentum_icon.png"))

        # Create the game clock
        self.gameClock = pygame.time.Clock()
        self.dt = 0

        # Global settings
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT
        self.REFRESH_RATE = REFRESH_RATE

        # Game State Manager and Game States
        self.gameStateManager = GameStateManager(
            "start", [self.WIDTH, self.HEIGHT], self.REFRESH_RATE
        )
        self.start = Start(self.screen, self.gameStateManager)
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.login = Login(self.screen, self.gameStateManager)
        self.register = Register(self.screen, self.gameStateManager)
        self.createGame = CreateGame(self.screen, self.gameStateManager)
        self.setTimer = SetTimer(self.screen, self.gameStateManager)
        self.gameLoop = GameLoop(self.screen, self.gameStateManager)
        self.gameOver = GameOver(self.screen, self.gameStateManager)
        self.leaderboard = Leaderboard(self.screen, self.gameStateManager)
        self.textTest = TestInput(self.screen, self.gameStateManager)

        #Demo menus
        self.menuA = MenuA(self.screen, self.gameStateManager)
        self.menuB = MenuB(self.screen, self.gameStateManager)

        # A return value that we will pass into each new game state
        # Will contain things like, user info, score, etc
        self.returnValues = {}
        # Game States so that we can convert strings into instances
        self.states = {
            "start": self.start,
            "main": self.mainMenu,
            "login": self.login,
            "register": self.register,
            "create_game": self.createGame,
            "set_timer": self.setTimer,
            "game_loop": self.gameLoop,
            "game_over": self.gameOver,
            "menu_a": self.menuA,
            "menu_b": self.menuB,
            "leaderboard": self.leaderboard,
            "text_test": self.textTest,
        }

        # WASD which are pressed down right now (4-vector)
        self.directions = None

    # Get the currently pressed keys
    def get_keys(self):
        keys = pygame.key.get_pressed()
        self.directions = [
            int(keys[K_w]),
            int(keys[K_s]),
            int(keys[K_d]),
            int(keys[K_a]),
        ]

    # Runs the main game
    def run(self):

        # Main Application Loop
        while True:

            # Get all events
            events = pygame.event.get()

            # Get all key presses
            keys = pygame.key.get_pressed()

            # Check if user wants to quit
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Use flags to identify the return values, ie: returnValues[0] = 'score'
            # Maybe consider input Values into the run function?
            self.returnValues = self.states[self.gameStateManager.getState()].run(
                self.returnValues
            )

            if "finish_time" in self.returnValues.keys():
                if self.gameStateManager.getState() != "game_over" and self.returnValues["finish_time"] <= datetime.datetime.now():
                    pygame.quit()
                    sys.exit()

            # {'score': 100, 'mmr': 300, 'won': 0}
            # if returnValues != None:
            # if returnValues[0] == 'score':
            # Call database methods to update the user
            # pass

            # Update the display
            pygame.display.update()

            # Update the clock
            dt = self.gameClock.tick(self.REFRESH_RATE) / 1000


class GameLoop:

    def __init__(self, display, gameStateManager):

        # Get the display we are working on
        self.display = display

        # Get the gameStateManager, so we can process it within the class
        self.gameStateManager = gameStateManager

        # Get the screen dimensions conveniently
        self.SCREEN_DIMS = self.gameStateManager.SCREEN_DIMS

        # Placeholders for the moment
        self.pos_x = self.SCREEN_DIMS[0] // 2
        self.pos_y = self.SCREEN_DIMS[1] // 2

        # Initialise the clock, and set the refresh rate
        self.clock = pygame.time.Clock()
        self.REFRESH_RATE = self.gameStateManager.REFRESH_RATE




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
                #if player == player1:
                    #pygame.draw.circle(self.display, (0, 0, 0), U.convertToScreen(player1.position, delta[2], self.SCREEN_DIMS), 10)


    def handleRayCollisions(self, rays, player1Position):
        
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

                relPos = U.convertToScreen(player1Position, line[0], self.SCREEN_DIMS)

                finalRelPos = U.convertToScreen(player1Position, line[1], self.SCREEN_DIMS)

                pygame.draw.aaline(self.display, (226,135,67), relPos, finalRelPos)


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


    def handleDetections(self, detectionSpokes):

        for player in self.players:
            spokes = detectionSpokes[player]


    def drawHUD(self):
        #Find remaining time
        currentTime = time.time()
        if currentTime - self.startTime >= self.maxTime:
            return False

        timeRemaining = int(self.maxTime - (currentTime - self.startTime))

        minutesRemaining = timeRemaining // 60
        secondsRemaining = timeRemaining % 60

        #Render time text
        time_text_surface, time_text_rect = text_font.render(str(minutesRemaining) + ":" + str(secondsRemaining), 
            fgcolor=(255, 255, 255), bgcolor=(0, 0, 0))

        #Set position on the screen
        time_text_rect.center = [self.SCREEN_DIMS[0]//2, 50]

        #Draw background rectangle
        pygame.draw.rect(self.display, (0,0,0), self.time_rect)

        self.display.blit(time_text_surface, time_text_rect)

        #Scores for each team
        #Team 1
        score1_text_surface, score1_text_rect = text_font.render(str(self.scores[0]), 
            fgcolor=(255, 255, 255), bgcolor=(0, 0, 255))

        score1_text_rect.center = self.score_1_rect.center
        pygame.draw.rect(self.display, (0, 0, 255), self.score_1_rect)
        self.display.blit(score1_text_surface, score1_text_rect)

        #Team 2
        score2_text_surface, score2_text_rect = text_font.render(str(self.scores[1]), 
            fgcolor=(255, 255, 255), bgcolor=(255, 0, 0))

        score2_text_rect.center = self.score_2_rect.center
        pygame.draw.rect(self.display, (255, 0, 0), self.score_2_rect)
        self.display.blit(score2_text_surface, score2_text_rect)

        return True

    def run(self, returnValues):

        #Set the difficulties and create agent
        difficulty = returnValues["difficulty"]
        m = MomentumAgents(difficulty)
        self.groups = m.groups
        self.group_map = m.group_map
        self.policy = m.policy
        self.team0_policy = m.team0_policy
        self.team1_policy = m.team1_policy

        #Dt for frame-rate independent physics
        dt = 0

        # Team 1
        self.player1 = Player([1500, 3000], [0, -1], 0, AssaultRifle(self.REFRESH_RATE))
        self.player2 = Player([2000, 3000], [0, -1], 0, AssaultRifle(self.REFRESH_RATE))
        self.player3 = Player([2500, 3000], [0, -1], 0, SniperRifle(self.REFRESH_RATE))

        # Team 2
        self.player4 = Player([2500, 1000], [0, 1], 1, Shotgun(self.REFRESH_RATE))
        self.player5 = Player([2000, 1000], [0, 1], 1, AssaultRifle(self.REFRESH_RATE))
        self.player6 = Player([1500, 1000], [0, 1], 1, SniperRifle(self.REFRESH_RATE))

        # Contains all of the players in the game
        self.players = [self.player1, self.player2, self.player3, self.player4, self.player5, self.player6]

        #Colour of the blocks
        block_colour = [0, 150, 0]

        #Blocks
        self.block1 = Block([1500, 2000], 200, 1200, block_colour, self.SCREEN_DIMS, self.player1.position)
        self.block2 = Block([2500, 2000], 200, 1200, block_colour, self.SCREEN_DIMS, self.player1.position)
        #self.block3 = Block([1000, 2000], 400, 400, block_colour, self.SCREEN_DIMS, self.player1.position)
        #self.block4 = Block([2000, 2000], 400, 400, block_colour, self.SCREEN_DIMS, self.player1.position)
        #self.block5 = Block([3000, 2000], 400, 400, block_colour, self.SCREEN_DIMS, self.player1.position)

        self.borderLeft = Block([-10, 2000], 20, 4000, (0, 0, 0), self.SCREEN_DIMS, self.player1.position)
        self.borderRight = Block([4010, 2000], 20, 4000, (0, 0, 0), self.SCREEN_DIMS, self.player1.position)
        self.borderTop = Block([2000, -10], 4040, 20, (0, 0, 0), self.SCREEN_DIMS, self.player1.position)
        self.borderBottom = Block([2000, 4010], 4040, 20, (0, 0, 0), self.SCREEN_DIMS, self.player1.position)

        #List of all blocks
        self.blocks = [self.block1, self.block2, self.borderLeft, self.borderRight, self.borderTop, self.borderBottom]#, self.block3, self.block4, self.block5]

        self.countdowns = {p: 0 for p in self.players}

        #Team scores
        self.scores = {0: 0, 1: 0}

        #Max score in one game
        self.max_score = 600

        self.player_scores = {p : 0 for p in self.players}

        self.startTime = time.time()

        #Round time in seconds
        self.maxTime = 20#300

        #Zoom factor
        zoom = 1

        #Set min zoom factor
        if isinstance(self.player1.weapon, SniperRifle):
            maxZoom = 0.5
        elif isinstance(self.player1.weapon, AssaultRifle):
            maxZoom = 0.35
        else:
            maxZoom = 1
        #Main loop
        running = True

        #Are we zoomed in
        zoomed_in = False

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


        observations = self.getObservations()
        

        #For the time
        self.time_rect = pygame.Rect(self.SCREEN_DIMS[0]//2, 50, 300, 100)
        self.time_rect.center = [self.SCREEN_DIMS[0]//2, 50]

        self.score_1_rect = pygame.Rect(self.SCREEN_DIMS[0]//2 - 275, 0, 150, 100)
        self.score_2_rect = pygame.Rect(self.SCREEN_DIMS[0]//2 + 150, 0, 150, 100)

        while running:

            self.display.fill((255, 255, 255))
            mouse_clicked = False
            #Check if player wants to quit
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_clicked = True
                #Zoom functions
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                    zoomed_in = True
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    zoomed_in = False

            #Get the key presses and mouse position and buttons
            keys = pygame.key.get_pressed()

            #Get mouse position
            mouse_pos = pygame.mouse.get_pos()

            if zoomed_in:
                zoom = maxZoom
            else:
                zoom = 1

            #Get direction vector
            player1_direction = [mouse_pos[0] - self.SCREEN_DIMS[0]//2, mouse_pos[1] - self.SCREEN_DIMS[1]//2]

            #Normalise direction vector
            dir_mag = sqrt(U.dot(player1_direction, player1_direction))
            if dir_mag == 0:
                player1_direction = self.player1.initial_forward_vec
            else:
                player1_direction = U.mult(player1_direction, 1 / dir_mag)

            #Update the direction vector
            self.player1.forward_vec = player1_direction

            #Get the directions which are pressed
            directions = [int(keys[K_d]) - int(keys[K_a]), int(keys[K_w]) - int(keys[K_s])]


            #Team 0 actions
            action0 = self.team0_policy(observations)["team0", "action"]

            #Team 1 actions
            action1 = self.team1_policy(observations)["team1", "action"]

            #Output from the model will go here
            model_predictions = [
                {"forward": directions[1], "right": directions[0], "rot_rate": 0, "firing": mouse_clicked},
                {"forward": float(action0[1][0]), "right": float(action0[1][1]), "rot_rate": float(action0[1][2]), "firing": (float(action0[1][3]) > 0.5)},
                {"forward": float(action0[2][0]), "right": float(action0[2][1]), "rot_rate": float(action0[2][2]), "firing": (float(action0[2][3]) > 0.5)},
                {"forward": float(action1[0][0]), "right": float(action1[0][1]), "rot_rate": float(action1[0][2]), "firing": (float(action1[0][3]) > 0.5)},
                {"forward": float(action1[1][0]), "right": float(action1[1][1]), "rot_rate": float(action1[1][2]), "firing": (float(action1[1][3]) > 0.5)},
                {"forward": float(action1[2][0]), "right": float(action1[2][1]), "rot_rate": float(action1[2][2]), "firing": (float(action1[2][3]) > 0.5)},
            ]

            rays = {}
            #Update player states
            for i, player in enumerate(self.players, 0):
                rays[player], fired = player.updatePlayerState(model_predictions[i], self.countdowns[player], dt)
                if fired:
                    self.countdowns[player] = player.weapon.maxFrameCooldown
                else:
                    self.countdowns[player] -= 1

            self.handlePlayerCollisions()
            self.handleBlockCollisions(self.player1)
            
            #Handle ray collisions
            deltaDamageCredit, deltaEliminationCredit, deltaDeathCredit = self.handleRayCollisions(rays, self.player1.position)


            #Render players as needed
            for i, player in enumerate(self.players, 0):
                player.render(self.display, self.player1.position, self.SCREEN_DIMS, zoom)

                self.scores[player.team] += deltaDamageCredit[player] + 50 * deltaEliminationCredit[player] - 50*deltaDeathCredit[player]
                self.player_scores[player] += deltaDamageCredit[player] + 50 * deltaEliminationCredit[player] - 50*deltaDeathCredit[player]

            #Render blocks
            for block in self.blocks:
                block.render(self.display, self.player1.position, directions, dt, self.SCREEN_DIMS, zoom)


            running = self.drawHUD()

            #Update the display
            pygame.display.update()

            for i in range(0, 2):
                if self.scores[i] > self.max_score:
                    running = False

            #Get a screen capture
            #pygame.image.save(self.display, "map_border.png")

            #Tick the clock
            dt = self.clock.tick(self.REFRESH_RATE)/1000

            print(self.clock.get_fps())

            observations = self.getObservations()


        self.gameStateManager.setState("game_over")
        returnValues["team_scores"] = self.scores
        playerScores = {}
        for player in self.players:
            playerScores[self.invPlayerLabels[player]] = self.player_scores[player]
        returnValues["player_scores"] = playerScores
        return returnValues


    def getPlayerObservations(self, player):

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

        observations = distances + healths + alliances
        observations.append(player.health)
        observations.append(can_fire)

        return observations

    def getObservations(self):
        team0_labels = ["player1", "player2", "player3"]
        team1_labels = ["player4", "player5", "player6"]

        team0_obs = []
        team1_obs = []

        for label in team0_labels:
            playerInstance = self.playerLabel[label]

            team0_obs.append(self.getPlayerObservations(playerInstance))

        for label in team1_labels:
            playerInstance = self.playerLabel[label]

            team1_obs.append(self.getPlayerObservations(playerInstance))


        return TensorDict({
            "team0": 
                {
                "observation": torch.tensor(team0_obs, dtype=torch.float32),
                },
            "team1":
                {
                "observation": torch.tensor(team1_obs, dtype=torch.float32),
                },
            
        }, batch_size=torch.Size([]))
#PyGame Modules
import pygame
from pygame.locals import *
import sys
import datetime

from block import Block
from utils import Utility as U
from database import DatabaseHandler

#https://stackoverflow.com/questions/20842801/how-to-display-text-in-pygame
import pygame.freetype

#MD5 Hashing
import hashlib

from copy import copy

#https://stackoverflow.com/questions/46390231/how-can-i-create-a-text-input-box-with-pygame

pygame.freetype.init()
text_font = pygame.freetype.SysFont('iosevka', 100)
med_font = pygame.freetype.SysFont('iosevka', 70)
small_font = pygame.freetype.SysFont('iosevka', 50)


#Will detect if a user has clicked it, and will execute a function on click
class Button(Block):

    #Constructor
    def __init__(self, centre, length0, length1, text, rectangleBgColour, textBgColour, textColour, SCREEN_DIMS):

        #Middle of the screen
        camera_position = U.mult(SCREEN_DIMS, 0.5)

        #Position as an integer
        camera_position = [int(i) for i in camera_position]

        #Initiate the block class in the 
        super(Button, self).__init__(centre, length0, length1, rectangleBgColour, SCREEN_DIMS, camera_position)

        #Set the bg color
        self.BG_COLOR = rectangleBgColour

        #Text that we want to display on the button
        self.text = text

        #Set the text surface and rect to write on
        self.text_surface, self.text_rect = text_font.render(text, fgcolor=textColour, bgcolor=textBgColour)

        #Set the centre of the button on the screen
        self.text_rect.center = self.centre

        #Set screen dims for rendering
        self.SCREEN_DIMS = SCREEN_DIMS

        #The colour of the text
        self.textColour = textBgColour

        #The colour immediately surrounding the text
        self.textBgColour = textBgColour


    #Modified render function of the button
    def render(self, display, dt):

        #Render the block
        super().render(display, U.mult(self.SCREEN_DIMS, 0.5), [0, 0], dt, self.SCREEN_DIMS, zoom=1)

        #Render the text surface
        display.blit(self.text_surface, self.text_rect)

    #Check for clicks on the button
    def checkForClick(self, clickPosition):

        #Get the rectangle of the button
        boundRect = self.rect

        #Rectangle point collision
        clicked = boundRect.collidepoint(clickPosition)

        #Return whether clicked or not
        return clicked

#Parent Menu class
class Menu:
    def __init__(self, display, gameStateManager, bgColor):

        #Set the display on which we are rendering
        self.display = display
        
        #Set the gsm
        self.gameStateManager = gameStateManager

        #Set screen dims
        self.SCREEN_DIMS = gameStateManager.SCREEN_DIMS

        #Set bg color
        self.BG_COLOR = bgColor

    #Run the menu
    def run(self, returnValues):

        #Fill display
        self.display.fill(self.BG_COLOR)

        #Create clock
        self.clock = pygame.time.Clock()
        self.dt = 0

        #Condition for loop
        self.running = True

        self.setup()

        #Main loop
        while self.running:
            #Redraw display
            self.display.fill(self.BG_COLOR)

            # Get all events
            events = pygame.event.get()

            # Get all key presses
            keys = pygame.key.get_pressed()

            #Get if mouse was clicked in that frame
            self.clicked = False

            #Iterate through events
            for event in events:

                # Check if user wants to quit
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                #Check if mouse button has been presesed
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.clicked = True

            #Return values from specific methods
            returnValues = self.specificMethods(keys, events, returnValues)

            #Update the display
            pygame.display.update()

            #Tick the clock
            self.dt = self.clock.tick(self.gameStateManager.REFRESH_RATE)
        
        #Return modified (or not) returnValues
        return returnValues
    
    #Providing an interface for child classes to overwrite
    def specificMethods(self, keys, events, returnValues):

        #Empty for now
        pass

    #Any setup we want to do everytime we run the menu
    def setup(self):

        pass

#Demo menus
class MenuA(Menu):

    def __init__(self, display, gameStateManager):

        super().__init__(display, gameStateManager, (0, 0, 255))

    def specificMethods(self, keys, events):

        if keys[K_DOWN]:
            self.gameStateManager.setState('menu_b')
            self.running = False

        return None

class MenuB(Menu):

    def __init__(self, display, gameStateManager):

        super().__init__(display, gameStateManager, (255, 0, 0))

    def specificMethods(self, keys, events):

        if keys[K_UP]:
            self.gameStateManager.setState('menu_a')
            self.running = False

        return None

#Directed from the login page
class Start(Menu):

    def __init__(self, display, gameStateManager):

        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Centre of the button
        button_centre = U.mult(self.SCREEN_DIMS, 0.5)

        #Button dimensions
        length0, length1 = 500, 250

        #Text background colour
        textBgColour = (16, 26, 94)

        #Colour of the text
        textColour = (0, 0, 0)

        #Text to display
        text = "Start!"

        #Rectangle Colour
        rectangleBgColour = (129, 235, 182)
        textBgColour = rectangleBgColour

        #Create button instance
        self.button = Button(button_centre, length0, length1, text, rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

    #Overwritten from parent
    def specificMethods(self, keys, events, returnValues):
        #Initialise variables
        inPos = False

        #Render the button
        self.button.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        inPos = self.button.checkForClick(pos)

        #If button clicked, go to game loop
        if self.clicked and inPos:
            self.gameStateManager.setState('login')
            self.running = False

        #Save image
        #pygame.image.save(self.display, "start_menu.png")
        
        return returnValues

#Directed from the start page
class MainMenu(Menu):
    def __init__(self, display, gameStateManager):

        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, 400]

        length0, length1 = 400, 200

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        rectangleBgColour = (129, 235, 182)#(180, 193, 233)
        textBgColour = rectangleBgColour

        self.setTimerButton = Button(button_centre, 550, 120, "Set Timer", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.createGameButton = Button([self.SCREEN_DIMS[0]//2, 550], 680, 120, "Create Game", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.leaderboardButton = Button([self.SCREEN_DIMS[0]//2, 700], 550, 120, "Leaderboard", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.exitButton = Button([self.SCREEN_DIMS[0]//2, 880], 200, 120, "Exit", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)


        self.momentumLogo = pygame.transform.scale(pygame.image.load("assets/momentum_icon.png").convert_alpha(), (200, 200))

    def specificMethods(self, keys, events, returnValues):

        #Initialise variables
        inPos = False

        #Render text
        #text_surface, text_rect = text_font.render('Start Menu', fgcolor=(0, 0, 0), bgcolor=self.BG_COLOR)
        #text_rect.center = (self.SCREEN_DIMS[0] // 2, self.SCREEN_DIMS[1] // 2)

        #Blit to surface
        #self.display.blit(text_surface, text_rect)

        #Render the button
        self.setTimerButton.render(self.display, self.dt)
        self.createGameButton.render(self.display, self.dt)
        self.leaderboardButton.render(self.display, self.dt)
        self.exitButton.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        inPosTimer = self.setTimerButton.checkForClick(pos)
        inPosGame = self.createGameButton.checkForClick(pos)
        inPosLb = self.leaderboardButton.checkForClick(pos)
        inPosExit = self.exitButton.checkForClick(pos)

        #If button clicked, go to timer
        if self.clicked and inPosTimer:
            self.gameStateManager.setState('set_timer')
            self.running = False

        #If button clicked, go to game loop
        if self.clicked and inPosGame:
            self.gameStateManager.setState('create_game')
            self.running = False

        #If button clicked, go to leaderboard
        if self.clicked and inPosLb:
            self.gameStateManager.setState('leaderboard')
            self.running = False

        #If exit, exit the game
        if self.clicked and inPosExit:
            self.running = False
            pygame.quit()
            sys.exit()


        #Render logo
        self.display.blit(self.momentumLogo, (self.SCREEN_DIMS[0]//2 - 100, 100))

        #pygame.image.save(self.display, "main_menu.png")
        
        return returnValues

#Initial page
class Login(Menu):
    def __init__(self, display, gameStateManager):
        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Centre of the button
        button_centre = [self.SCREEN_DIMS[0]//2, 400]

        #Dims of the button
        length0, length1 = 400, 200

        #Text background colour
        textBgColour = (16, 26, 94)

        #Text colour
        textColour = (0, 0, 0)

        #Button colour
        rectangleBgColour = (129, 235, 182)
        textBgColour = rectangleBgColour

        #Create button instances
        self.loginButton = Button([self.SCREEN_DIMS[0]//2, 700], 350, 120, "Login", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.registerButton = Button([self.SCREEN_DIMS[0]//2, 880], 700, 120, "Register Here!", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        #Load momentum logo
        self.momentumLogo = pygame.transform.scale(pygame.image.load("assets/momentum_v3.png").convert_alpha(), (840, 140))

        #Boxes for inputs
        self.userBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2 - 200, 250, 60)
        self.passBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2, 250, 60)

        #User input boxes
        self.userInput = TextInput(self.userBox)
        self.passInput = TextInput(self.passBox)

    def specificMethods(self, key, events, returnValues):

        #Render the button
        self.loginButton.render(self.display, self.dt)
        self.registerButton.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        loginPos = self.loginButton.checkForClick(pos)
        registerPos = self.registerButton.checkForClick(pos)

        #If button clicked, go to game loop
        if self.clicked and loginPos:
            auth = DatabaseHandler.AuthenticateAccount(self.userInput.text, self.passInput.text)
            if auth[0] == False and auth[1] == "invalid_id":
                self.userInput.text = ""
                self.passInput.text = ""
            if auth[0] == False and auth[1] == "invalid_password":
                self.passInput.text = ""

            if auth[0]:
                self.gameStateManager.setState('main')
                self.running = False
                returnValues["PlayerID"] = self.userInput.text
                #print(returnValues)

        #If clicking the register button take to the register menu
        if self.clicked and registerPos:
            self.gameStateManager.setState("register")
            self.running = False

        #Render the user name text
        login_text_surface, login_text_rect = small_font.render("Username", fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))

        #Get position of input field
        temp = self.userBox.midleft

        #Update text position to the left of the user input field
        login_text_rect.midright = [temp[0] - 20, temp[1]]

        #Update to screen
        self.display.blit(login_text_surface, login_text_rect)

        #Render the password text
        pass_text_surface, pass_text_rect = small_font.render("Password", fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))

        #Get position of password field
        temp = self.passBox.midleft

        #Update text position to the left of pass field
        pass_text_rect.midright = [temp[0] - 20, temp[1]]
        
        #Update to screen
        self.display.blit(pass_text_surface, pass_text_rect)


        #Handle text inputs and render
        self.userInput.handleTextInput(events)
        self.userInput.render(self.display)

        #Handle text inputs and render
        self.passInput.handleTextInput(events)
        self.passInput.render(self.display)

        #pygame.image.save(self.display, "login_menu.png")

        #No modifications to returnValues
        return returnValues


#Text input test
class TestInput(Menu):
    def __init__(self, display, gameStateManager):
        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Boxes for inputs
        self.userBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2 - 200, 250, 60)


        #User input boxes
        self.userInput = TextInput(self.userBox)

    def specificMethods(self, key, events, returnValues):

        #Handle text inputs and render
        self.userInput.handleTextInput(events)
        self.userInput.render(self.display)
        #pygame.image.save(self.display, "test_input.png")

        #No modifications to returnValues
        return returnValues


#Handles text inputs
class TextInput:

    def __init__(self, rect, fgcolor=(0, 0, 0), bgcolor=(0, 255, 255), boxColor=(255, 0, 0)):
        self.box = rect
        self.active = False
        self.fgcolor = fgcolor
        self.bgcolor = bgcolor
        self.boxColor = boxColor
        self.text = ""

    def handleTextInput(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.box.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False

            if event.type == pygame.KEYDOWN:
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    else:
                        self.text += event.unicode

    def render(self, display):
        user_surf, user_rect = small_font.render(self.text, fgcolor=self.fgcolor, bgcolor=self.bgcolor)
        
        self.box.w = max(300, user_rect.w + 10)

        user_rect.center = self.box.center

        pass_surf, pass_rect = small_font.render(self.text, fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))

        pygame.draw.rect(display, self.boxColor, self.box, 2)

        display.blit(user_surf, user_rect)


#Directed from the Login page
class Register(Menu):
    def __init__(self, display, gameStateManager):
        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, 400]

        length0, length1 = 400, 200

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        rectangleBgColour = (129, 235, 182)#(180, 193, 233)
        textBgColour = rectangleBgColour

        self.registerButton = Button([self.SCREEN_DIMS[0]//2, 700], 400, 120, "Register", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.momentumLogo = pygame.transform.scale(pygame.image.load("assets/momentum_v3.png").convert_alpha(), (840, 140))

        self.emailBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2 - 400, 250, 60)
        self.userBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2 - 200, 250, 60)
        self.passBox = pygame.Rect(self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]//2, 250, 60)

        self.emailInput = TextInput(self.emailBox)
        self.userInput = TextInput(self.userBox)
        self.passInput = TextInput(self.passBox)

        self.boxColor = (255, 0, 0)

    def specificMethods(self, key, events, returnValues):

        #Initialise variables
        inPos = False

        #Render the button
        self.registerButton.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        registerPos = self.registerButton.checkForClick(pos)

        #If button clicked, go to game loop
        if self.clicked and registerPos:
            result = DatabaseHandler.CreateAccount(self.userInput.text, self.emailInput.text, self.passInput.text)
            if result == False:
                self.gameStateManager.setState("login")
                self.running = False

            if result:
                self.gameStateManager.setState('main')
                self.running = False
                returnValues["PlayerID"] = self.userInput.text


        email_text_surface, email_text_rect = small_font.render("Email", fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))
        temp = self.emailBox.midleft
        email_text_rect.midright = [temp[0] - 20, temp[1]]
        pygame.draw.rect(self.display, (0, 0, 255), email_text_rect)
        self.display.blit(email_text_surface, email_text_rect)


        login_text_surface, login_text_rect = small_font.render("Username", fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))
        temp = self.userBox.midleft
        login_text_rect.midright = [temp[0] - 20, temp[1]]
        pygame.draw.rect(self.display, (0, 0, 255), login_text_rect)
        self.display.blit(login_text_surface, login_text_rect)

        pass_text_surface, pass_text_rect = small_font.render("Password", fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))

        temp = self.passBox.midleft
        pass_text_rect.midright = [temp[0] - 20, temp[1]]
        pygame.draw.rect(self.display, (0, 0, 255), pass_text_rect)
        self.display.blit(pass_text_surface, pass_text_rect)

        self.emailInput.handleTextInput(events)
        self.userInput.handleTextInput(events)
        self.passInput.handleTextInput(events)

        self.emailInput.render(self.display)
        self.userInput.render(self.display)
        self.passInput.render(self.display)

        #pygame.image.save(self.display, "register_menu.png")


        return returnValues

    def handleTextInputs(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:

                if self.userBox.collidepoint(event.pos):
                    self.userActive = True
                    self.passActive = False
                    self.emailActive = False
                if self.passBox.collidepoint(event.pos):
                    self.passActive = True
                    self.userActive = False
                    self.emailActive = False
                if self.emailBox.collidepoint(event.pos):
                    self.passActive = False
                    self.userActive = False
                    self.emailActive = True                 

            if event.type == pygame.KEYDOWN:
                if self.userActive:
                    if event.key == pygame.K_RETURN:
                        self.userActive = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.username = self.username[:-1]
                    else:
                        self.username += event.unicode

                if self.passActive:
                    if event.key == pygame.K_RETURN:
                        self.passActive = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.password = self.password[:-1]
                    else:
                        self.password += event.unicode

                if self.emailActive:
                    if event.key == pygame.K_RETURN:
                        self.emailActive = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.email = self.email[:-1]
                    else:
                        self.email += event.unicode


        email_surf, email_rect = small_font.render(self.email, fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))
        
        self.emailBox.w = max(300, email_rect.w + 10)

        email_rect.center = self.emailBox.center



        user_surf, user_rect = small_font.render(self.username, fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))
        
        self.userBox.w = max(300, user_rect.w + 10)

        user_rect.center = self.userBox.center

        pass_surf, pass_rect = small_font.render(self.password, fgcolor=(0, 0, 0), bgcolor=(0, 255, 255))

        self.passBox.w = max(300, pass_rect.w + 10)

        pass_rect.center = self.passBox.center

        pygame.draw.rect(self.display, self.boxColor, self.userBox, 2)
        pygame.draw.rect(self.display, self.boxColor, self.passBox, 2)
        pygame.draw.rect(self.display, self.boxColor, self.emailBox, 2)

        self.display.blit(user_surf, user_rect)
        self.display.blit(pass_surf, pass_rect)
        self.display.blit(email_surf, email_rect)


#Directed from the Start
class CreateGame(Menu):
    def __init__(self, display, gameStateManager):

        #Cyan
        self.cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, self.cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]-200]

        length0, length1 = 400, 200

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        rectangleBgColour = (129, 235, 182)#(180, 193, 233)
        textBgColour = rectangleBgColour

        self.playButton = Button(button_centre, 550, 120, "Play!", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.momentumLogo = pygame.transform.scale(pygame.image.load("assets/momentum_icon.png").convert_alpha(), (200, 200))

        self.friendlyDifficulty, self.enemyDifficulty = 0, 0

        self.friendlyMinus = Button([self.SCREEN_DIMS[0]//4 + 400, self.SCREEN_DIMS[1]//3], 100, 100, "-", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.friendlyPlus = Button([self.SCREEN_DIMS[0]//4 + 800, self.SCREEN_DIMS[1]//3], 100, 100, "+", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.enemyMinus = Button([self.SCREEN_DIMS[0]//4 + 400, self.SCREEN_DIMS[1]//3 + 250], 100, 100, "-", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.enemyPlus = Button([self.SCREEN_DIMS[0]//4 + 800, self.SCREEN_DIMS[1]//3 + 250], 100, 100, "+", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

    def specificMethods(self, keys, events, returnValues):

        #Reset values
        inPosFrMi, inPosFrPl, inPosEnMi, inPosEnPl = False, False, False, False

        #Adjustment buttons
        self.friendlyMinus.render(self.display, self.dt)
        self.friendlyPlus.render(self.display, self.dt)
        self.enemyMinus.render(self.display, self.dt)
        self.enemyPlus.render(self.display, self.dt)

        #Render play button
        self.playButton.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over buttons
        inPosFrMi = self.friendlyMinus.checkForClick(pos)
        inPosFrPl = self.friendlyPlus.checkForClick(pos)
        inPosEnMi = self.enemyMinus.checkForClick(pos)
        inPosEnPl = self.enemyPlus.checkForClick(pos)

        inPosPlay = self.playButton.checkForClick(pos)


        if self.clicked and inPosFrMi:
            self.friendlyDifficulty = max(0, self.friendlyDifficulty-1)


        if self.clicked and inPosFrPl:
            self.friendlyDifficulty = min(1, self.friendlyDifficulty+1)
            

        if self.clicked and inPosEnMi:
            self.enemyDifficulty = max(0, self.enemyDifficulty-1)


        if self.clicked and inPosEnPl:
            self.enemyDifficulty = min(1, self.enemyDifficulty+1)


        #If exit, exit the game
        if self.clicked and inPosPlay:
            self.gameStateManager.setState("game_loop")
            self.running = False

        friendly_text_surface, friendly_text_rect = med_font.render("Team-mate Strength", fgcolor=(0, 0, 0), bgcolor=self.cyan)
        enemy_text_surface, enemy_text_rect = med_font.render("Enemy Strength", fgcolor=(0, 0, 0), bgcolor=self.cyan)

        frStrength_text_surface, frStrength_text_rect = med_font.render(str(self.friendlyDifficulty+1), fgcolor=(0, 0, 0), bgcolor=self.cyan)
        enStrength_text_surface, enStrength_text_rect = med_font.render(str(self.enemyDifficulty+1), fgcolor=(0, 0, 0), bgcolor=self.cyan)

        friendly_text_rect.center = [self.SCREEN_DIMS[0]//4, self.SCREEN_DIMS[1]//3]
        enemy_text_rect.center = [self.SCREEN_DIMS[0]//4, self.SCREEN_DIMS[1]//3 + 250]

        frStrength_text_rect.center = [self.SCREEN_DIMS[0]//4 + 600, self.SCREEN_DIMS[1]//3]
        enStrength_text_rect.center = [self.SCREEN_DIMS[0]//4 + 600, self.SCREEN_DIMS[1]//3 + 250]

        self.display.blit(friendly_text_surface, friendly_text_rect)
        self.display.blit(enemy_text_surface, enemy_text_rect)

        self.display.blit(frStrength_text_surface, frStrength_text_rect)
        self.display.blit(enStrength_text_surface, enStrength_text_rect)

        returnValues["difficulty"] = [self.friendlyDifficulty, self.enemyDifficulty]
        print(returnValues["difficulty"])


        #pygame.image.save(self.display, "create_menu.png")
        return returnValues

#Directed from the CreateGame Menu, leads to the Game Loop
class SetTimer(Menu):
    def __init__(self, display, gameStateManager):

        #Cyan
        self.cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, self.cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]-200]

        length0, length1 = 400, 200

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        rectangleBgColour = (129, 235, 182)
        textBgColour = rectangleBgColour

        self.playButton = Button(button_centre, 550, 120, "Go!", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.momentumLogo = pygame.transform.scale(pygame.image.load("assets/momentum_icon.png").convert_alpha(), (200, 200))

        self.hours, self.minutes = 0, 0

        self.hourMinus = Button([self.SCREEN_DIMS[0]//4 + 400, self.SCREEN_DIMS[1]//3], 100, 100, "-", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.hourPlus = Button([self.SCREEN_DIMS[0]//4 + 800, self.SCREEN_DIMS[1]//3], 100, 100, "+", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.minuteMinus = Button([self.SCREEN_DIMS[0]//4 + 400, self.SCREEN_DIMS[1]//3 + 250], 100, 100, "-", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)
        self.minutePlus = Button([self.SCREEN_DIMS[0]//4 + 800, self.SCREEN_DIMS[1]//3 + 250], 100, 100, "+", rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

    def specificMethods(self, keys, events, returnValues):

        #Reset values
        inPosHrMi, inPosHrPl, inPosMiMi, inPosMiPl = False, False, False, False

        #Adjustment buttons
        self.hourMinus.render(self.display, self.dt)
        self.hourPlus.render(self.display, self.dt)
        self.minuteMinus.render(self.display, self.dt)
        self.minutePlus.render(self.display, self.dt)

        #Render play button
        self.playButton.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over buttons
        inPosHrMi = self.hourMinus.checkForClick(pos)
        inPosHrPl = self.hourPlus.checkForClick(pos)
        inPosMiMi = self.minuteMinus.checkForClick(pos)
        inPosMiPl = self.minutePlus.checkForClick(pos)

        inPosPlay = self.playButton.checkForClick(pos)


        if self.clicked and inPosHrMi:
            self.hours -= 1
            self.hours = max(0, self.hours)


        if self.clicked and inPosHrPl:
            self.hours += 1
            

        if self.clicked and inPosMiMi:
            self.minutes -= 1
            self.minutes = max(0, self.minutes)


        if self.clicked and inPosMiPl:
            self.minutes += 1
            if self.minutes >= 60:
                self.hours += 1
                self.minutes -= 60

        #If exit, exit the game
        if self.clicked and inPosPlay:
            self.gameStateManager.setState("create_game")
            self.running = False
            deltatime = datetime.timedelta(hours=self.hours, minutes=self.minutes)
            current_time = datetime.datetime.now()
            returnValues["finish_time"] = current_time + deltatime
            #print("Start Time:", datetime.datetime.now())
            #print("Finish Time:", returnValues["finish_time"])

        

        hour_text_surface, hour_text_rect = med_font.render("Hours", fgcolor=(0, 0, 0), bgcolor=self.cyan)
        minute_text_surface, minute_text_rect = med_font.render("Minutes", fgcolor=(0, 0, 0), bgcolor=self.cyan)

        hrVal_text_surface, hrVal_text_rect = med_font.render(str(self.hours), fgcolor=(0, 0, 0), bgcolor=self.cyan)
        minVal_text_surface, minVal_text_rect = med_font.render(str(self.minutes), fgcolor=(0, 0, 0), bgcolor=self.cyan)

        hour_text_rect.center = [self.SCREEN_DIMS[0]//4, self.SCREEN_DIMS[1]//3]
        minute_text_rect.center = [self.SCREEN_DIMS[0]//4, self.SCREEN_DIMS[1]//3 + 250]

        hrVal_text_rect.center = [self.SCREEN_DIMS[0]//4 + 600, self.SCREEN_DIMS[1]//3]
        minVal_text_rect.center = [self.SCREEN_DIMS[0]//4 + 600, self.SCREEN_DIMS[1]//3 + 250]

        self.display.blit(hour_text_surface, hour_text_rect)
        self.display.blit(minute_text_surface, minute_text_rect)

        self.display.blit(hrVal_text_surface, hrVal_text_rect)
        self.display.blit(minVal_text_surface, minVal_text_rect)

        #pygame.image.save(self.display, "set_timer.png")

        return returnValues

#Directed from the game loop
class GameOver(Menu):

    def __init__(self, display, gameStateManager):

        #Cyan
        cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]-200]

        length0, length1 = 200, 120

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        text = "Back"

        rectangleBgColour = (129, 235, 182)#(180, 193, 233)
        textBgColour = rectangleBgColour

        self.button = Button(button_centre, length0, length1, text, rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.registered = False


    def specificMethods(self, keys, events, returnValues):
        #Initialise variables
        inPos = False

        #Render the button
        self.button.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        inPos = self.button.checkForClick(pos)

        #If button clicked, go to game loop
        if self.clicked and inPos:
            self.gameStateManager.setState('main')
            self.running = False

        #Vicory or defeat

        if returnValues["team_scores"][0] > returnValues["team_scores"][1]:
            text = "Victory!"
            vic = True

        else:
            text = "Defeat!"
            vic = False

        vic_text_surface, vic_text_rect = text_font.render(text, 
            fgcolor=(255, 255, 255), bgcolor=(0, 0, 255))

        vic_text_rect.center = U.mult(self.SCREEN_DIMS, 0.5)
        pygame.draw.rect(self.display, (0, 0, 255), vic_text_rect)
        self.display.blit(vic_text_surface, vic_text_rect)

        #pygame.image.save(self.display, "game_over.png")

        if not self.registered:
            mmr = 5 if vic else -5
            DatabaseHandler.UpdateAccount(returnValues["PlayerID"], returnValues["player_scores"]["player1"], mmr, vic)

            self.registered = True
        
        return returnValues

    def setup(self):
        self.registered = False

#Directed from the start
class Leaderboard(Menu):
    def __init__(self, display, gameStateManager):
        #Cyan
        self.cyan = (0, 255, 255)

        #Cyan background
        super().__init__(display, gameStateManager, self.cyan)

        #Create button instance to use
        #colour, SCREEN_DIMS, text, bg_color, hoverColour=None, hoverScale=1

        button_centre = [self.SCREEN_DIMS[0]//2, self.SCREEN_DIMS[1]-100]

        length0, length1 = 200, 120

        #Text background colour
        textBgColour = (16, 26, 94)

        textColour = (0, 0, 0)

        text = "Back"

        rectangleBgColour = (129, 235, 182)#(180, 193, 233)
        textBgColour = rectangleBgColour

        self.button = Button(button_centre, length0, length1, text, rectangleBgColour, textBgColour, textColour, self.SCREEN_DIMS)

        self.fetched = False

        self.players = []


    def specificMethods(self, keys, events, returnValues):

        if not self.fetched:
            
            self.players = DatabaseHandler.getLeaderboardPlayers()

            self.fetched = True

        #Initialise variables
        inPos = False

        #Render the button
        self.button.render(self.display, self.dt)

        #Get mouse position
        pos = pygame.mouse.get_pos()

        #Check if over button
        inPos = self.button.checkForClick(pos)

        #If button clicked, go to game loop
        if self.clicked and inPos:
            self.gameStateManager.setState('main')
            self.running = False


        rank_text_surface, rank_text_rect = med_font.render("Rank", fgcolor=(0, 0, 0), bgcolor=self.cyan)
        playerID_text_surface, playerID_text_rect = med_font.render("Player", fgcolor=(0, 0, 0), bgcolor=self.cyan)
        mmr_text_surface, mmr_text_rect = med_font.render("MMR", fgcolor=(0, 0, 0), bgcolor=self.cyan)


        initial_x, initial_y = 500, 250
        offset_y = 150
        offset_x_1 = 500
        offset_x_2 = 900

        rank_text_rect.center = [initial_x, initial_y - offset_y]
        playerID_text_rect.center = [initial_x + offset_x_1, initial_y - offset_y]
        mmr_text_rect.center = [initial_x + offset_x_2, initial_y - offset_y]

        self.display.blit(rank_text_surface, rank_text_rect)
        self.display.blit(playerID_text_surface, playerID_text_rect)
        self.display.blit(mmr_text_surface, mmr_text_rect)


        #Render three text surfaces for each player
        for i, player in enumerate(self.players):

            rank = i+1
            playerID, mmr = player

            rank_text_surface, rank_text_rect = med_font.render(str(rank), fgcolor=(0, 0, 0), bgcolor=self.cyan)
            playerID_text_surface, playerID_text_rect = med_font.render(playerID, fgcolor=(0, 0, 0), bgcolor=self.cyan)
            mmr_text_surface, mmr_text_rect = med_font.render(str(mmr), fgcolor=(0, 0, 0), bgcolor=self.cyan)

            rank_text_rect.center = [initial_x, initial_y + i*offset_y]
            playerID_text_rect.center = [initial_x + offset_x_1, initial_y + i*offset_y]
            mmr_text_rect.center = [initial_x + offset_x_2, initial_y + i*offset_y]

            self.display.blit(rank_text_surface, rank_text_rect)
            self.display.blit(playerID_text_surface, playerID_text_rect)
            self.display.blit(mmr_text_surface, mmr_text_rect)

        #pygame.image.save(self.display, "leaderboard.png")
        
        return returnValues

    def setup(self):
        self.fetched = False

class GameStateManager:
    def __init__(self, current_state, SCREEN_DIMS, REFRESH_RATE):

        #Get the global game variables in a convenient way
        #Allows all states to easily access these values
        self.current_state = current_state
        self.SCREEN_DIMS = SCREEN_DIMS
        self.REFRESH_RATE = REFRESH_RATE

    #Returns the current state of the game
    def getState(self):
        return self.current_state

    #Set the next state of the game (ie. game loop -> game over)
    def setState(self, state):
        self.current_state = state

if __name__ == "__main__":
    gsm = GameStateManager('start', 20, 20)
    gsm.setState('next_state')
    print(gsm.getState())

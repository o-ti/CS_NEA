from momentum_env.weapon import Weapon

class Player:

    def __init__(self, spawn_point, initial_forward_vec, team, weapon):

        #Where the player will spawn every time they are killed
        self.spawn_point = spawn_point

        #The direction the player will face when they are respawned
        self.initial_forward_vec = initial_forward_vec

        #The maximum health that the player can have at any time
        self.max_health = 100

        #The current health of the player
        self.health = 100

        #The maximum magnitude of the velocity
        self.max_speed = 500

        #Which team the player is on, it will be an integer (0 or 1)
        #To check for a hit between two enemies
        #XOR the teams of the two players involved (0 means no hit, 1 means hit)
        self.team = team

        #Visual representation of the character on the screen
        #TODO

        #The player's Weapon
        self.weapon = weapon

        #Current position of the players
        self.position = self.spawn_point

        #Current direction of the player
        self.forward_vec = self.initial_forward_vec

        #Radius of the circle representing the player
        self.radius = 75

        #For AI use only, will be the action of the model
        self.rotation_rate = 0

    def move_player(self, directions, forward_vec, dt):
        velocity = [0, 0]

        #For loop avoids repeated code
        for i in (0, 2):
            if directions[i] == directions[i+1]:
                velocity[i//2] = 0
            else:
                velocity[i//2] = directions[i] - directions[i+1]

        #Velocity will have -1, 0, or 1 in each spot
        #If it is moving diagonally, x^2 + y^2 = 2
        #So we must divide the components by sqrt(2)
        if (velocity[0]**2 + velocity[1]**2 == 2):
            velocity = [i / 2**(1/2) for i in velocity]

        #We need to multiply by the max speed in order to get our final velocity
        velocity = [self.max_speed * i for i in velocity]

        #We will finally update the position of the player
        updated_position = [self.position[i] + velocity[i]*dt for i in (0, 1)]

        #Check that the values are within (0, 0) and (8000, 8000)
        #(0, 0) is the top left of the map
        #(8000, 8000) is the bottom right

        for i in range(2):
            if updated_position[i] - self.radius <= 0:
                updated_position[i] = self.radius
            elif updated_position[i] + self.radius >= 8000:
                updated_position[i] = 8000 - self.radius
        self.position = updated_position

    #Upon event will fire the weapon in the specified class
    #Returns the ray produced and information about this ray
    def fire(self, weapon):
        return weapon.fire(self.position, self.direction)

    def updatePlayerState(self, input_keys):
        raise NotImplementedError


    #Will convert the world position of the character to a camera position for the player
    def convertToScreen(self, camera_position, object_position, SCREEN_DIMS):
        screenPosition = [object_position[i] - camera_position[i] + SCREEN_DIMS[i]//2 for i in (0, 1)]
        return screenPosition

    #Renders the character to the display of the player
    def render(self, display, camera_position, directions, dt, SCREEN_DIMS):
        #Add code to not render if outside frame
        pygame.draw.circle(display, (0, 100, 100), self.convertToScreen(camera_position, self.position, SCREEN_DIMS), self.radius)
        for_pos = [self.position[i] + 100*self.forward_vec[i] for i in range(2)]
        pygame.draw.aaline(display, (100, 0, 0), self.convertToScreen(camera_position, self.position, SCREEN_DIMS), self.convertToScreen(camera_position, for_pos, SCREEN_DIMS))
        self.move_player(directions, self.forward_vec, dt)

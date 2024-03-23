from utils import Utility as U
from math import sqrt, sin, cos, pi
from numpy import random

class Weapon:
    #We need a way to move the weapon alongside the Weapon
    #Some way to attach the two together
    #TODO
    def __init__(self, REFRESH_RATE):
        self.ammo = 30
        self.reloadTime = 2.0
        self.damagePerHit = 20
        self.range = 1000
        self.std_dev = 0.10
        self.cooldown = 0.3
        self.raysPerShot = 1
        self.spread = 1
        self.maxFrameCooldown = int(self.cooldown * REFRESH_RATE)

    #We will attach the damage to this as well
    def fire(self, position, direction):
        rays = []
        magnitude_squared = U.dot(direction, direction)
        unit_dir = U.mult(direction, 1 / sqrt(magnitude_squared))

        for i in range(self.raysPerShot):

            #Sample deviation using the normal distribution
            if self.spread == 1:
                angleDeviation = random.normal(loc = 0, scale=self.std_dev, size=None)
                rotated_dir = U.rotateVector(unit_dir, angleDeviation)
            else:
                rotated_dir = unit_dir

            #Add unit_dir rotation here using matrices
            final_extent = U.vecAdd(position, U.mult(rotated_dir, self.range))
            rays.append([position, final_extent, self.damagePerHit])

        return rays

#Automatic weapon, good at mid range
class AssaultRifle(Weapon):
    def __init__(self, REFRESH_RATE):
        super().__init__(REFRESH_RATE)

#Long range, with a very high damage per hit, but slow reloads
class SniperRifle(Weapon):
    def __init__(self, REFRESH_RATE):
        super().__init__(REFRESH_RATE)
        self.ammo = 5
        self.reloadTime = 5.0
        self.damagePerHit = 60
        self.range = 4000
        self.std_dev = 1e-2
        self.cooldown = 2.0
        self.raysPerShot = 1
        self.cooldown = 2.0
        self.spread = 0
        self.maxFrameCooldown = int(self.cooldown * REFRESH_RATE)

#A very short range weapon
class Shotgun(Weapon):
    def __init__(self, REFRESH_RATE):
        super().__init__(REFRESH_RATE)
        self.ammo = 6
        self.reloadTime = 3.0
        self.damagePerHit = 3
        self.range = 500
        self.std_dev = pi/12
        self.raysPerShot = 8
        self.cooldown = 0.75
        self.spread = 1
        self.maxFrameCooldown = int(self.cooldown * REFRESH_RATE)


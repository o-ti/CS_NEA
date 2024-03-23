from momentum_env.utils import Utility as U
from math import sqrt

class Weapon:
    #We need a way to move the weapon alongside the Weapon
    #Some way to attach the two together
    #TODO
    def __init__(self):
        self.ammo = 30
        self.reloadTime = 2.0
        self.damagePerHit = 5
        self.range = 1000
        self.std_dev = 1.0
        #self.

    #We will attach the damage to this as well
    #TODO: Add angular range
    def fire(self, position, direction):
        magnitude_squared = U.dot(direction, direction)
        unit_dir = U.mult(direction, 1 / sqrt(magnitude_squared))

        #Add unit_dir rotation here using matrices
        final_extent = U.vecAdd(position, U.mult(unit_dir, self.range))

        return [position, final_extent, self.damage]

#Automatic weapon, good at mid range
class AssaultRifle(Weapon):
    def __init__(self):
        pass

#Long range, with a very high damage per hit, but slow reloads
class SniperRifle(Weapon):
    def __init__(self):
        self.ammo = 5
        self.reloadTime = 5.0
        self.damagePerHit = 100
        self.range = 4000

#A very short range weapon
class Shotgun(Weapon):
    def __init__(self):
        self.ammo = 6
        self.reloadTime = 3.0
        self.damagerPerHit = 35
        self.range = 500

from math import sqrt

class Utility:

    #More complex collisions
    #https://gamedevacademy.org/pygame-collisions-tutorial-complete-guide/
    @staticmethod
    def dot(a, b):
        return sum([i*j for i, j in zip(a, b)])

    @staticmethod
    def vecSub(a, b):
        return [i-j for i, j in zip(a, b)]

    @staticmethod
    def vecAdd(a, b):
        return [i + j for i, j in zip(a, b)]

    @staticmethod
    def mult(vec, scalar):
        return [i * scalar for i in vec]

    #Rect is going to have a centre and the two sidelengths
    @staticmethod
    def lineRectCollision(line, rect):
        #https://stackoverflow.com/questions/56100547/how-do-i-check-collision-between-a-line-and-a-rect-in-pygame

        raise NotImplementedError

    #Circle should be a position and a radius [position, radius]
    #Line is provided as [intial position, final extent]
    #Direction [x, y]
    #Returns [hit, t]
    @staticmethod
    def lineCircleCollision(line, circle):

        #Notation from this stackexchange post
        #https://codereview.stackexchange.com/questions/86421/line-segment-to-circle-collision-algorithm

        q = circle[0]
        r = circle[1]
        p1 = line[0]
        v = Utility.vecSub(line[1], p1)

        a = Utility.dot(v, v)
        b = 2 * Utility.dot(v, Utility.vecSub(p1, q))
        c = Utility.dot(p1, p1) + Utility.dot(q, q) - 2 * Utility.dot(p1, q) - r**2

        discriminant = b**2 - 4 * a * c

        if discriminant < 0:
            return [False, None]

        sqrt_disc = sqrt(discriminant)

        t1 = (-b + sqrt_disc) / (2 * a)
        t2 = (-b - sqrt_disc) / (2 * a)

        if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
            return [False, None]

        t = min(t1, t2)
        return [True, t]

    @staticmethod
    def circleRectCollision(circle, rect):
        #https://gamedev.stackexchange.com/questions/179635/circle-square-collision-detection-simple-formula
        #Could be decomposed as being 4 circle line collisions
        raise NotImplementedError

    #We will return [False, None] if no collision
    #If there is a collision, we will return the direction of the collision
    @staticmethod
    def circleCircleCollision(circle1, circle2):

        centreDiff = Utility.vecSub(circle2[0], circle1[0])
        magnitude = Utility.dot(centreDiff, centreDiff)

        if magnitude > 4*circle1[1]**2:
            return [False, None]

        return [True, Utility.mult(centreDiff, 0.5)]

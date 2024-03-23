from math import sqrt, pi, sin, cos
import numpy as np
import time
import random


class Utility:

    #More complex collisions
    #https://gamedevacademy.org/pygame-collisions-tutorial-complete-guide/

    #Take a dot product
    @staticmethod
    def dot(a, b):
        return sum([i*j for i, j in zip(a, b)])

    #Subtract two vectors
    @staticmethod
    def vecSub(a, b):
        return [i-j for i, j in zip(a, b)]

    #Add two vectors
    @staticmethod
    def vecAdd(a, b):
        return [i + j for i, j in zip(a, b)]

    @staticmethod
    def mult(vec, scalar):
        return [i * scalar for i in vec]

    #The first coefficient in the result is for line1

    @staticmethod
    def lineLineCollision(line1, line2):

        #We have both lines in vector form
        #line 1 -> [x_1, y_1], [x_2, y_2]
        #line 2 -> [x_3, y_3], [x_4, y_4]
        x_1, y_1 = line1[0]
        x_2, y_2 = line1[1]
        x_3, y_3 = line2[0]
        x_4, y_4 = line2[1]

        #Left row is lambda
        #Right row is mu

        #matrix = np.array([[x_2 - x_1, x_3 - x_4], [y_2 - y_1, y_3 - y_4]])
        matrix = [[x_2 - x_1, x_3 - x_4], [y_2 - y_1, y_3 - y_4]]


        #resultVec = np.array([x_3 - x_1, y_3 - y_1])
        resultVec = [x_3 - x_1, y_3 - y_1]

        #Find the determinant of the matrix
        #determinant = np.linalg.det(matrix)

        determinant = matrix[0][0] * matrix[1][1] - matrix[1][0] * matrix[0][1]

        #det = 0 -> Can't be solved
        if determinant == 0:
            return [False, None]

        inverseMatrix1 = [[y_3 - y_4, x_4 - x_3], [y_1 - y_2, x_2 - x_1]]


        #Solve system
        #result = np.linalg.solve(matrix, resultVec)
        result = [Utility.dot(inverseMatrix1[0], resultVec), Utility.dot(inverseMatrix1[1], resultVec)]
        result = Utility.mult(result, 1/determinant)

        #Check that the result is between the constraint points
        if 0 <= result[0] <= 1 and 0 <= result[1] <= 1:
            return [True, result]
        
        #Solution is not in bounds
        return [False, None]

    #Return the distance along the line of the collision. The rest doesn't actually matter
    @staticmethod
    def lineRectCollision(line, block):
        #https://www.jeffreythompson.org/collision-detection/line-rect.php
        #https://stackoverflow.com/questions/56100547/how-do-i-check-collision-between-a-line-and-a-rect-in-pygame

        #Get the corners
        corners = block.getCorners()

        #Decompose the rectangle into 4 lines: TL -> TR, TR -> BR, BR -> BL, BL -> TL
        lines = [[corners[i], corners[i+1]] for i in range(-1, 3)]

        #We only care about how far along the main line the collision is
        t_val = 3
        for edge in lines:
            isHit, lambda_mu = Utility.lineLineCollision(line, edge)
            if isHit:
                if lambda_mu[0] < t_val:
                    t_val = lambda_mu[0]

        if t_val == 3:
            return [False, None]
        return [True, t_val]

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

    #Determine whether there is a collision and resolve it
    @staticmethod
    def circleRectCollision(player, block):
        #https://dot32.dev/tutorials/circle-vs-rectangle-collision

        #Get player position
        px, py = player.position

        #Get block corners
        bCorners = block.getCorners()
        
        #Get rectangle values
        #rect_x = bCorners[0][0]
        #rect_y = bCorners[0][1]
        rect_x = bCorners[1][0]
        rect_y = bCorners[1][1]
        rect_w = block.length1
        rect_h = block.length2

        #Collision equation
        px = max(px, rect_x)
        px = min(px, rect_x + rect_w)
        py = max(py, rect_y)
        py = min(py, rect_y + rect_h)

        point = [px, py]

        #Check for collision
        isCollision = ((player.position[1] - py)**2 + (player.position[0] - px)**2) < player.radius**2

        #If collision find vector to resolve
        if isCollision:
            offset = Utility.vecSub(player.position, point)
            offset_mag = sqrt(Utility.dot(offset, offset))

            if offset_mag == 0:
                return [False, point, None]

            delta = Utility.mult(offset, (player.radius - offset_mag)/offset_mag)

            return [True, delta]#, point]

        return [False, None] #, point]

    #We will return [False, None] if no collision
    #If there is a collision, we will return the direction of the collision
    @staticmethod
    def circleCircleCollision(circle1, circle2):

        #Difference between the centres
        centreDiff = Utility.vecSub(circle2[0], circle1[0])

        #Magnitude squared of the difference
        magnitude = Utility.dot(centreDiff, centreDiff)

        #If outside of the range no collision
        if magnitude > 4*circle1[1]**2:
            return [False, None]

        #Avoids div by 0 errors
        if magnitude == 0:
            return [False, None]

        #The point on the circle where an intersection happens
        intersect_dir = Utility.mult(centreDiff, circle1[1]/sqrt(magnitude))

        #Midpoint of the collision
        centre_mid_point = Utility.mult(centreDiff, 0.5)

        #The half-distance in the collision
        mid_circum_vec = Utility.vecSub(intersect_dir, centre_mid_point)

        #The vector to push the player back by
        delta_position = Utility.mult(mid_circum_vec, -1)

        return [True, delta_position]

    #Returns a boolean if two points are within range
    @staticmethod
    def checkCircleInRange(pos1, pos2, range):
        dir_vec = Utility.vec_sub(pos2, pos1)
        magnitude_squared = Utility.dot(dir_vec, dir_vec)
        return (magnitude_squared <= range**2)

    @staticmethod
    def checkBlockInRange(pos1, block, range):
        raise NotImplementedError

    @staticmethod
    def rotateVector(vec, angle):

        #https://matthew-brett.github.io/teaching/rotation_2d.html

        rotatedVec = [0, 0]
        rotatedVec[0] = vec[0] * cos(angle) - vec[1] * sin(angle)
        rotatedVec[1] = vec[0] * sin(angle) + vec[1] * cos(angle)

        return rotatedVec

    #Will convert the world position of the character to a camera position for the player
    @staticmethod
    def convertToScreen(camera_position, object_position, SCREEN_DIMS, zoom=1):
        screenPosition = [zoom*(object_position[i] - camera_position[i]) + SCREEN_DIMS[i]//2 for i in (0, 1)]
        return screenPosition


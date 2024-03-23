from training.momentum_env.utils import Utility as U
class Block():

    #Length1 is in the x direction
    #Length2 is in the y direction
    def __init__(self, centre, length1, length2):

        self.centre = centre
        self.length1 = length1
        self.length2 = length2

    def getCorners(self):
        #TL, BL, BR, TR
        corners = []

        for i in range(-1, 2, 2):
            for j in range(-1, 2, 2):
                corners.append(U.vecAdd(self.centre, [i * self.length1/2, i * j * self.length2/2]))

        return corners
        
    def getEdges(self):
        #Get the corners
        corners = self.getCorners()

        #Decompose the rectangle into 4 lines: TL -> TR, TR -> BR, BR -> BL, BL -> TL
        
        #Top, Right, Bottom, Left
        lines = [[corners[i], corners[i+1]] for i in range(-1, 3)]

        return lines


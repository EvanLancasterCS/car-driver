import pygame, sys, math, NrNt

from pygame.locals import *

def rot_center(image, angle):
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image

class Vector2:
    x = None
    y = None
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def setX(self, x):
        self.x = x
    def setY(self, y):
        self.y = y
    def reduceSpeed(self, friction):
        self.x = self.x * friction
        self.y = self.y * friction
    def rotateAround(self, aX, aY, rot):
        radians = math.radians(rot)
        s = math.sin(radians)
        c = math.cos(radians)
        self.x -= aX
        self.y -= aY
        xNew = self.x * c - self.y * s
        yNew = self.x * s + self.y * c
        self.x = xNew + aX
        self.y = yNew + aY
    def distance(self, other):
        dist = math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
        return dist
        
        
class Line:
    pos1 = None
    pos2 = None
    lineColor = (255, 255, 255)
    def __init__(self, x1, y1, x2, y2):
        self.pos1 = Vector2(x1, y1)
        self.pos2 = Vector2(x2, y2)
    def draw(self):
        pygame.draw.line(display, self.lineColor, (self.pos1.x, self.pos1.y), (self.pos2.x, self.pos2.y), 2)
    def set(self, x1, y1, x2, y2):
        self.pos1.x = x1
        self.pos1.y = y1
        self.pos2.x = x2
        self.pos2.y = y2
    def checkCollisions(self, lines):
        for i in range(len(lines)):
            if self.doesIntersect(lines[i]):
                self.lineColor = (255, 0, 0)
                return i
        self.lineColor = (255, 255, 255)
    def checkRaycast(self, lines):
        closest = ()
        for i in range(len(lines)):
            if self.doesIntersect(lines[i]):
                if len(closest) == 0:
                    closest = self.doesIntersect(lines[i])
                else:
                    intersection = self.doesIntersect(lines[i])
                    v1 = Vector2(closest[0], closest[1])
                    v2 = Vector2(intersection[0], intersection[1])
                    d1 = self.pos1.distance(v1)
                    d2 = self.pos1.distance(v2)
                    if d1 < d2:
                        closest = (v1.x, v1.y)
                    else:
                        closest = (v2.x, v2.y)
        if len(closest) != 0:
            return closest
            
    def rotateAround(self, aX, aY, rot):
        self.pos1.rotateAround(aX, aY, rot)
        self.pos2.rotateAround(aX, aY, rot)
    def doesIntersect(self, other):
        X1 = self.pos1.x
        X2 = self.pos2.x
        X3 = other.pos1.x
        X4 = other.pos2.x
        Y1 = self.pos1.y
        Y2 = self.pos2.y
        Y3 = other.pos1.y
        Y4 = other.pos2.y
        
        if max(X1, X2) < min(X3, X4):
            return False
        if max(Y1, Y2) < min(Y3, Y4):
            return False
        
        try:
            m1 = (Y1-Y2)/(X1-X2)
        except ZeroDivisionError:
            m1 = 10000
            try:
                m2 = (Y3-Y4)/(X3-X4)
            except ZeroDivisionError:
                m2=10000#return False
            b2 = Y3 - m2*X3
            
            Ya = X1*m2 + b2
            
            if X1 <= max(X3, X4) and X1 >= min(X3, X4) and Ya <= max(Y1, Y2) and Ya >= min(Y1, Y2):
                return (X1, Ya)
            return False
        
        try:
            m2 = (Y3-Y4)/(X3-X4)
        except ZeroDivisionError:
            m2 = 1
            b1 = Y1 - m1*X1
            
            Ya = X3*m1 + b1
            
            if X3 <= max(X1, X2) and X3 >= min(X1, X2) and Ya <= max(Y3, Y4) and Ya >= min(Y3, Y4):
                return (X3, Ya)
            return False
            
        b1 = Y1 - m1*X1
        b2 = Y3 - m2*X3
             
        if m1 == m2:
            return False
        
        Xa = (b2 - b1) / (m1 - m2)
        if Xa < max(min(X1,X2), min(X3,X4)) or Xa > min(max(X1,X2), max(X3,X4)):
            return False
        else:
            return (Xa, (Xa*m1 + b1))
        
class BoxCollider:
    length = 0
    width = 0
    centerX = 0
    centerY = 0
    currRot = 0
    lines = []
    def __init__(self, length, width, x, y):
        self.length = length
        self.width = width
        self.centerX = x
        self.centerY = y
        self.defineLines()
    def defineLines(self):
        halfWidth = self.width/2
        halfLength = self.length/2
        p1 = Vector2(self.centerX-halfWidth, self.centerY-halfLength)
        p2 = Vector2(self.centerX-halfWidth, self.centerY+halfLength)
        p3 = Vector2(self.centerX+halfWidth, self.centerY+halfLength)
        p4 = Vector2(self.centerX+halfWidth, self.centerY-halfLength)
        self.lines.append(Line(p1.x, p1.y, p2.x, p2.y))
        self.lines.append(Line(p2.x, p2.y, p3.x, p3.y))
        self.lines.append(Line(p3.x, p3.y, p4.x, p4.y))
        self.lines.append(Line(p4.x, p4.y, p1.x, p1.y))
    def draw(self):
        for i in range(4):
            self.lines[i].draw()
    def setPos(self, x, y, rot):
        self.centerX = x
        self.centerY = y
        self.currRot = rot
        self.updatePositions()
    def updateRotation(self):
        for i in range(4):
            self.lines[i].rotateAround(self.centerX, self.centerY, self.currRot)
    def updatePositions(self):
        halfWidth = self.width/2
        halfLength = self.length/2
        p1 = Vector2(self.centerX-halfWidth, self.centerY-halfLength)
        p2 = Vector2(self.centerX-halfWidth, self.centerY+halfLength)
        p3 = Vector2(self.centerX+halfWidth, self.centerY+halfLength)
        p4 = Vector2(self.centerX+halfWidth, self.centerY-halfLength)
        self.lines[0].set(p1.x, p1.y, p2.x, p2.y)
        self.lines[1].set(p2.x, p2.y, p3.x, p3.y)
        self.lines[2].set(p3.x, p3.y, p4.x, p4.y)
        self.lines[3].set(p4.x, p4.y, p1.x, p1.y)
        self.updateRotation()
    def checkCollisions(self, lines):
        for i in range(4):
            n = self.lines[i].checkCollisions(lines)
            if n != None:
                return "kill"
    def checkGoals(self, gls, checked):
        for i in range(4):
            n = self.lines[i].checkCollisions(gls)
            if n != None and n not in checked:
                return n
            
rayLength = 700
class Car:
    myColor = (128, 128, 128)
    speed = 1
    turnSpeed = 10
    friction = 0.9
    currRot = 0.0
    currPos = None
    currVelocity = Vector2(0, 0)
    myRect = None
    myCollider = None
    myRays = None
    score = 0
    goalsChecked = []
    def __init__(self, x, y):
        self.currPos = Vector2(x, y)
        self.myCollider = BoxCollider(25, 50, x+25, y+50)
        self.goalsChecked = []
        self.myRays = []
        for i in range(9):
            obj = Line(0,0,0,0)
            self.myRays.append(obj)
        self.currRot = 90
        self.fixRot()
        self.updatePosition()
        self.currVelocity = Vector2(0,0)
        self.score = 0
        #self.updateRaysPos()
    def updateRaysPos(self):
        for i in range(len(self.myRays)):
            self.myRays[i].pos1.x = self.currPos.x + 25
            self.myRays[i].pos1.y = self.currPos.y + 25
        cosLen = math.cos(math.radians(360-self.currRot)) * rayLength
        sinLen = math.sin(math.radians(360-self.currRot)) * rayLength
        cosDiagRightLen = math.cos(math.radians(360-self.currRot+15)) * rayLength
        sinDiagRightLen = math.sin(math.radians(360-self.currRot+15)) * rayLength
        cosDiagLeftLen = math.cos(math.radians(360-self.currRot-15)) * rayLength
        sinDiagLeftLen = math.sin(math.radians(360-self.currRot-15)) * rayLength
        cosDiag2RightLen = math.cos(math.radians(360-self.currRot+30)) * rayLength
        sinDiag2RightLen = math.sin(math.radians(360-self.currRot+30)) * rayLength
        cosDiag2LeftLen = math.cos(math.radians(360-self.currRot-30)) * rayLength
        sinDiag2LeftLen = math.sin(math.radians(360-self.currRot-30)) * rayLength
        cosRightLen = math.cos(math.radians(self.currRot)) * rayLength
        sinRightLen = math.sin(math.radians(self.currRot)) * rayLength
        cosDiagDownRightLen = math.cos(math.radians(360-self.currRot+135)) * rayLength
        sinDiagDownRightLen = math.sin(math.radians(360-self.currRot+135)) * rayLength
        cosDiagDownLeftLen = math.cos(math.radians(360-self.currRot-135)) * rayLength
        sinDiagDownLeftLen = math.sin(math.radians(360-self.currRot-135)) * rayLength
        self.myRays[0].pos2.x = self.currPos.x + cosLen + 25
        self.myRays[0].pos2.y = self.currPos.y + sinLen + 25
        self.myRays[1].pos2.x = self.currPos.x + cosDiagRightLen + 25
        self.myRays[1].pos2.y = self.currPos.y + sinDiagRightLen + 25
        self.myRays[2].pos2.x = self.currPos.x + cosDiagLeftLen + 25
        self.myRays[2].pos2.y = self.currPos.y + sinDiagLeftLen + 25
        self.myRays[3].pos2.x = self.currPos.x + cosDiag2RightLen + 25
        self.myRays[3].pos2.y = self.currPos.y + sinDiag2RightLen + 25
        self.myRays[4].pos2.x = self.currPos.x + cosDiag2LeftLen + 25
        self.myRays[4].pos2.y = self.currPos.y + sinDiag2LeftLen + 25
        self.myRays[5].pos1.x += math.cos(math.radians(360-self.currRot))*12
        self.myRays[5].pos1.y += math.sin(math.radians(360-self.currRot))*12
        self.myRays[5].pos2.x = self.currPos.x + sinRightLen + 25 + math.cos(math.radians(360-self.currRot))*12
        self.myRays[5].pos2.y = self.currPos.y + cosRightLen + 25 + math.sin(math.radians(360-self.currRot))*12
        self.myRays[6].pos1.x -= math.cos(math.radians(180-self.currRot))*12
        self.myRays[6].pos1.y -= math.sin(math.radians(180-self.currRot))*12
        self.myRays[6].pos2.x = self.currPos.x - sinRightLen + 25 - math.cos(math.radians(180-self.currRot))*12
        self.myRays[6].pos2.y = self.currPos.y - cosRightLen + 25 - math.sin(math.radians(180-self.currRot))*12
        self.myRays[7].pos1.x -= math.cos(math.radians(360-self.currRot))*12
        self.myRays[7].pos1.y -= math.sin(math.radians(360-self.currRot))*12
        self.myRays[7].pos2.x = self.currPos.x + cosDiagDownRightLen + 25
        self.myRays[7].pos2.y = self.currPos.y + sinDiagDownRightLen + 25
        self.myRays[8].pos1.x += math.cos(math.radians(180-self.currRot))*12
        self.myRays[8].pos1.y += math.sin(math.radians(180-self.currRot))*12
        self.myRays[8].pos2.x = self.currPos.x + cosDiagDownLeftLen + 25
        self.myRays[8].pos2.y = self.currPos.y + sinDiagDownLeftLen + 25
    def drawRays(self):
        for i in range(len(self.myRays)):
            endPos = self.myRays[i].checkRaycast(walls)#checkRaycast(self.myRays[i])
            if endPos != False and endPos != None:
                pygame.draw.circle(display, (25, 200, 25), (int(endPos[0]), int(endPos[1])), 5, 0)
    def getRayLen(self, n):
        endPos = self.myRays[n].checkRaycast(walls)
        if endPos != False and endPos != None:
            realLine = Line(self.myRays[n].pos1.x, self.myRays[n].pos1.y, endPos[0], endPos[1])
        else:
            realLine = self.myRays[n]
        return realLine.pos1.distance(realLine.pos2)
    def updatePosition(self):
        self.currVelocity.reduceSpeed(self.friction)
        self.currPos.x += self.currVelocity.x
        self.currPos.y += self.currVelocity.y
        self.myCollider.setPos(self.currPos.x+25, self.currPos.y+25, 360-self.currRot)
        n = self.myCollider.checkGoals(goals, self.goalsChecked)
        if n != None and len(self.goalsChecked) != len(goals)-1:
            self.score += 1
            self.goalsChecked.append(n)
        elif len(self.goalsChecked) == len(goals)-1:
            self.score += 1
            self.goalsChecked = []
        self.updateRaysPos()
    def draw(self):
        rotatedImg = rot_center(carImg, self.currRot)#pygame.transform.rotate(carImg, self.currRot)
        display.blit(rotatedImg, (self.currPos.x, self.currPos.y))#self.myRect = pygame.draw.rect(display, self.myColor, (self.pos.x, self.pos.y, 50, 50))
    def moveForward(self):
        xAmount = math.cos(math.radians(self.currRot)) * self.speed
        yAmount = math.sin(math.radians(self.currRot)) * self.speed
        self.currVelocity.x += xAmount
        self.currVelocity.y -= yAmount
    def moveBackward(self):
        xAmount = math.cos(math.radians(self.currRot)) * self.speed
        yAmount = math.sin(math.radians(self.currRot)) * self.speed
        self.currVelocity.x -= xAmount
        self.currVelocity.y += yAmount
    def fixRot(self):
        if self.currRot >= 360:
            self.currRot = self.currRot - 360
        elif self.currRot < 0:
            self.currRot += 360
        
        if self.currRot == 90:
            self.currRot = 89
        elif self.currRot == 270:
            self.currRot = 269
    def turnRight(self):
        self.currRot -= self.turnSpeed
        self.fixRot()
    def turnLeft(self):
        self.currRot += self.turnSpeed
        self.fixRot()
    def determineDir(self, direc):
        if direc == 'forward':
            self.moveForward()
        elif direc == 'backward':
            self.moveBackward()
        elif direc == 'right':
            self.turnRight()
        elif direc == 'left':
            self.turnLeft()

inputAm = 9
hiddenAm = 9
outputAm = 4
numMuts = 10
class AIPlayer:
    myNet = None
    myCar = None
    alive = True
    timeSinceLastGoal = 0
    lastGoal = 0
    def __init__(self, *helper):
        self.alive = True
        self.myCar = Car(startPos[0], startPos[1])
        #self.time
        if len(helper) == 0:
            self.myNet = NrNt.NNetwork(inputAm, hiddenAm, outputAm)
        else:
            self.myNet = helper[0].myNet.DeepCopy()
            for i in range(numMuts):
                self.myNet.Mutate()
    def determineState(self, inputs):
        outputs = self.myNet.calculateNetwork(inputs)
        dirS = ""
        dirF = ""
        if outputs[0] > 0.5 and outputs[1] < 0.5:
            dirS = "right"
        elif outputs[1] > 0.5 and outputs[0] < 0.5:
            dirS = "left"
        if outputs[0] > outputs[1] and outputs[0] > 0.5 and outputs[1] > 0.5:
            dirS = "right"
        elif outputs[1] > outputs[0] and outputs[0] > 0.5 and outputs[1] > 0.5:
            dirS = "left"
        if outputs[2] > 0.5 and outputs[3] < 0.5:
            dirF = "forward"
        elif outputs[3] > 0.5 and  outputs[2] < 0.5:
            dirF = "backward"
        self.myCar.determineDir(dirS)
        self.myCar.determineDir(dirF)
        
    def tick(self):
        inputs = []
        self.timeSinceLastGoal += 1/30.0
        #print(str(self.timeSinceLastGoal))
        if self.myCar.score > self.lastGoal:
            self.timeSinceLastGoal = 0
            self.lastGoal = self.myCar.score
        elif self.timeSinceLastGoal > 1:
            self.alive = False
            return
        
        for i in range(len(self.myCar.myRays)):
            inputs.append(self.myCar.getRayLen(i))
        self.determineState(inputs)
        self.myCar.updatePosition()
        collided = self.myCar.myCollider.checkCollisions(walls)
        if collided == "kill":
            self.alive = False
            return
        self.myCar.draw()

def reset(car):
    car.currPos.x = startPos[0]
    car.currPos.y = startPos[1]
    car.currRot = 90
    car.updatePosition()
    car.currVelocity = Vector2(0,0)
    car.score = 0
    
walls = []
goals = []
drawn = []
def printDrawn():
    for i in range(len(drawn)):
        print(str(drawn[i].pos1.x) + "," + str(drawn[i].pos1.y) + "," + str(drawn[i].pos2.x) + "," + str(drawn[i].pos2.y))

goalstemp = [33,420,164,428,
26,331,213,385,
120,242,232,387,
254,243,306,426,
357,191,400,331,
506,177,481,327,
632,227,562,363,
738,242,674,368,
843,359,698,419,
842,478,670,487,
846,542,662,540,
852,627,677,605,
817,781,697,648,
671,802,671,628,
590,763,626,590,
552,739,548,587,
509,738,427,611,
465,799,331,691,
358,862,312,724,
198,827,294,703,
171,746,245,629,
24,665,191,581,
32,554,182,526]

temp = [89,256,292,256,
292,256,330,232,
330,232,411,202,
411,202,490,200,
490,200,561,229,
561,229,599,254,
599,254,733,255,
733,255,810,282,
810,282,835,338,
835,338,827,540,
827,540,826,689,
826,689,806,741,
806,741,755,775,
755,775,692,794,
692,794,633,793,
633,793,596,739,
596,739,538,705,
538,705,481,707,
481,707,452,740,
452,740,412,819,
412,819,359,853,
359,853,277,860,
277,860,208,793,
208,793,172,729,
172,729,137,722,
137,722,94,729,
94,729,62,721,
62,721,48,686,
48,686,54,296,
54,296,60,278,
60,278,89,256,
149,368,145,577,
145,577,189,624,
189,624,248,660,
248,660,290,741,
290,741,313,770,
313,770,345,731,
345,731,370,665,
370,665,452,621,
452,621,585,603,
585,603,651,633,
651,633,705,692,
705,692,724,691,
724,691,717,381,
717,381,687,350,
687,350,608,344,
608,344,554,332,
554,332,520,291,
520,291,447,279,
447,279,358,303,
358,303,315,347,
315,347,223,359,
223,359,168,353,
168,353,149,368]

def buildGoals():
    currGoal = []
    for i in range(len(goalstemp)):
        currGoal.append(goalstemp[i])
        if len(currGoal) == 4:
            goals.append(Line(currGoal[0], currGoal[1], currGoal[2], currGoal[3]))
            currGoal = []
def buildFromTemp():
    currWall = []
    for i in range(len(temp)):
        currWall.append(temp[i])
        if len(currWall) == 4:
            walls.append(Line(currWall[0], currWall[1], currWall[2], currWall[3]))
            currWall = []
buildFromTemp()
buildGoals()
        
pygame.init()

FPS = 30
fpsClock = pygame.time.Clock()
startPos = (75, 450)

display = pygame.display.set_mode((900,900))
pygame.display.set_caption('Game')

carImg = pygame.image.load('car.png')
carImg = pygame.transform.scale(carImg, (50, 50))
#myCar = Car(startPos[0], startPos[1])
topAI = AIPlayer()
plrs = []#AIPlayer()
populationSize = 25
currentGen = 0
currentCreature = 0
def buildPlayers(arr):
    arr = []
    arr.append(topAI)
    for i in range(populationSize-1):
        arr.append(AIPlayer(topAI))
    return arr

def getBestPlayer(arr):
    best = arr[0]
    for i in range(1, len(arr)):
        if arr[i].myCar.score > best.myCar.score:
            best = arr[i]
        elif arr[i].myCar.score == best.myCar.score:
            center = Vector2(450, 450)
            if arr[i].myCar.currPos.distance(center) < best.myCar.currPos.distance(center):
                best = arr[i]
    return best

plrs = buildPlayers(plrs)

#print(line1.doesIntersect(line2))
snapDistance = 10
def addWall(X1, Y1, X2, Y2):
    v1 = Vector2(X1, Y1)
    v2 = Vector2(X2, Y2)
    for i in range(len(walls)):
        if v1.distance(walls[i].pos1) < snapDistance:
            v1.x = walls[i].pos1.x
            v1.y = walls[i].pos1.y
            break
        if v1.distance(walls[i].pos2) < snapDistance:
            v1.x = walls[i].pos2.x
            v1.y = walls[i].pos2.y
            break
        if v2.distance(walls[i].pos1) < snapDistance:
            v2.x = walls[i].pos1.x
            v2.y = walls[i].pos1.y
            break
        if v2.distance(walls[i].pos2) < snapDistance:
            v2.x = walls[i].pos2.x
            v2.y = walls[i].pos2.y
            break
    myLine = Line(v1.x, v1.y, v2.x, v2.y)
    walls.append(myLine)
    
def drawWalls():
    for i in range(len(walls)):
        walls[i].draw()

drawingWall = False
wallpos = ()

font = pygame.font.SysFont('Comic Sans MS', 30)


while True:
    display.fill((0,0,0))
    drawWalls()
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        
        #elif event.type == pygame.MOUSEBUTTONDOWN:
        #    pos = pygame.mouse.get_pos()
        #    if drawingWall == False:
        #        wallPos = Vector2(pos[0], pos[1])
        #        drawingWall = True
        ##    else:
        #        drawn.append(Line(wallPos.x, wallPos.y, pos[0], pos[1]))
        #        wallPos = ()
         #       drawingWall = False
        
    if drawingWall:
        pos = pygame.mouse.get_pos()
        newl = Line(wallPos.x, wallPos.y, pos[0], pos[1])
        newl.draw()
    #for i in range(len(goals)):
    #    goals[i].lineColor = (0, 255, 0)
    #    goals[i].draw()
    #plr.myCar.determineDir(directionF)
    #plr.myCar.determineDir(directionS)
    #plr.myCar.updatePosition()
    #plr.myCar.myCollider.checkCollisions(walls)
    #plr.myCar.drawRays()
    #plr.myCar.draw()
    #print(plr.myCar.score)
    #myCar.myCollider.draw()
    if plrs[currentCreature].alive:
        plrs[currentCreature].tick()
        plrs[currentCreature].myCar.drawRays()
    elif currentCreature + 1 < len(plrs):
        currentCreature += 1
        #plrs[currentCreature-1].myNet.print()
    elif currentCreature == len(plrs)-1:
        topAI = getBestPlayer(plrs)
        plrs = buildPlayers(plrs)
        currentCreature = 0
        currentGen += 1
    plrs[currentCreature].myNet.draw(display)
    surface = font.render('Population Num: ' + str(currentCreature) + ', Gen: ' + str(currentGen)
                          + ', Time: ' + str("{:.2f}".format(plrs[currentCreature].timeSinceLastGoal) + ', Score: ' + str(topAI.myCar.score)), False, (255,0,0))
    display.blit(display,(0,0))
    pygame.display.update()
    fpsClock.tick(FPS)


    
        
    
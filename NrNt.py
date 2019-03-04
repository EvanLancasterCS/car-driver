import random, math, pygame
CONST_mutationRate = 0.02
#random.seed(1)

def sigmoid(x):
    return 1 / (1+math.exp(-x))

# A hidden node object consisting of weights and an activation function
# as well as the ability to mutate a random weight
class NetNode:
    # Array of floats
    weights = []
    total = 0
    
    # Defines a node with given weights
    def __init__(self, weights):
        self.weights = weights
    
    # Returns true if is output layer
    def isOutput(self):
        if len(self.weights) == 0:
            return True
        return False
    
    # Activation function for node. Returns some number based on inputs.
    def AF(self, inputs):
        addition = 0
        for i in range(len(inputs)):
            addition += inputs[i]
        addition = sigmoid(addition)
        self.total = addition
        return addition
    
    def draw(self, x, y, nextPoses, surface):
        pygame.draw.circle(surface, (255,255,255), (int(x), int(y)), 6)
        for i in range(len(nextPoses)):
            lineColor = 255 - abs(int(255*self.weights[i]))
            
            nX = nextPoses[0]
            nY = nextPoses[1]
            pygame.draw.line(surface, (lineColor,lineColor,lineColor), (int(x), int(y)), (nX, nY), 1)
    
    # Randomly chooses a weight and randomly adjusts it.
    def Mutate(self):
        # Positive or negative mutation
        m = random.randrange(2)
        wC = random.randrange(len(self.weights))
        if m == 0:
            m = -1
        self.weights[wC] += m * CONST_mutationRate

# A layer of NetNodes
class NetLayer:
    # Array of NetNodes
    nodes = None
    # Takes in 2 dimensional array of weights
    def __init__(self, tweights):
        self.nodes = []
        for i in range(len(tweights)):
            self.nodes.append(NetNode(tweights[i]))
    
    # Mutates a random node
    def Mutate(self):
        n = random.randrange(len(self.nodes))
        self.nodes[n].Mutate()
    
    # Sets all of nodes to appropriate total
    def calculateAllNodes(self, previousLayer):
        for i in range(len(self.nodes)):
            self.calculateNode(previousLayer, i)
    
    # Gets weights and totals of all nodes for this node and appends to input, then adds to node
    def calculateNode(self, previousLayer, nodeNum):
        inputs = []
        for i in range(len(previousLayer.nodes)):
            w = previousLayer.nodes[i].weights[nodeNum]
            a = previousLayer.nodes[i].total
            inputs.append(w * a)
        self.nodes[nodeNum].AF(inputs)
    
    # Returns true if is output layer
    def isOutputLayer(self):
        return self.nodes[0].isOutput()
    
    # Sets layer node weights
    def setNodeWeights(self, nodeNum, weights):
        self.nodes[nodeNum].weights = weights
    
    def getDrawYs(self, middleY):
        yPositions = []
        currentAdd = 0
        for i in range(len(self.nodes)):
            if i == 0:
                yPositions.append(middleY)
                continue
            
            modifier = 1
            if i % 2 == 0:
                modifier = -1
                currentAdd+=1
            yPositions.append(middleY + (currentAdd*modifier*20));
            
        yPositions.sort()
        return yPositions
    
    def draw(self, surface, x, middleY, nextPoses):
        yPositions = self.getDrawYs(middleY)
        for i in range(len(self.nodes)):
            self.nodes[i].draw(x, yPositions[i], nextPoses, surface)
    
    # Returns safe weights
    def getNodeWeights(self):
        arr = []
        for i in range(len(self.nodes)):
            lst = []
            for j in range(len(self.nodes[i].weights)):
                lst.append(self.nodes[i].weights[j])
            arr.append(lst)
        return arr

class NNetwork:
    layers = []
    outputs = []
    # Creates default nnetwork
    def __init__(self, numInputs, numHidden, numOutputs):
        self.layers = []
        self.outputs = []
        inputsArr = self.InitializeLayer(numInputs, numHidden)
        hiddenArr = self.InitializeLayer(numHidden, numOutputs)
        outputsArr = self.InitializeLayer(numOutputs, 0)
        inLayer = NetLayer(inputsArr)
        hidLayer = NetLayer(hiddenArr)
        outLayer = NetLayer(outputsArr)
        
        self.layers.append(inLayer)
        self.layers.append(hidLayer)
        self.layers.append(outLayer)
    
    def draw(self, surface):
        largest = self.layers[0]
        for i in range(1, 3):
            if len(self.layers[i].nodes) > len(largest.nodes):
                largest = self.layers[i]
        longest = len(largest.nodes)
        midY = ((longest / 2.0) * 8) + 50
        for i in range(len(self.layers)):
            nextPosses = []
            x = 50 * i + 50
            if i != len(self.layers)-1:
                yPosses = self.layers[i+1].getDrawYs(midY)
                for j in range(len(yPosses)):
                    nextPosses.append(x, yPosses[j])
            self.layers[i].draw(surface, x, midY, nextPosses)
    
    # Returns a deep copy of neural network
    def DeepCopy(self):
        nInputs = len(self.layers[0].nodes)
        nHidden = len(self.layers[1].nodes)
        nOut = len(self.layers[2].nodes)
        Network = NNetwork(nInputs, nHidden, nOut)
        for i in range(3):
            Network.setWeights(i, self.layers[i].getNodeWeights())
        return Network
        
    # Randomly mutates a layer
    def Mutate(self):
        n = random.randrange(len(self.layers)-1)
        self.layers[n].Mutate()
    
    # Calculates all of network based on inputs, stores outputs
    def calculateNetwork(self, inputs):
        for i in range(len(self.layers[0].nodes)):
            self.layers[0].nodes[i].total = inputs[i]
            
        for i in range(1, len(self.layers)):
            self.layers[i].calculateAllNodes(self.layers[i-1])
        
        length = len(self.layers)
        endLen = len(self.layers[length-1].nodes)
        self.outputs = []
        for i in range(endLen):
            self.outputs.append(self.layers[length-1].nodes[i].total)
        return self.outputs
        
    # Sets the weights of a given layer
    def setWeights(self, layerNum, tweights):
        layer = self.layers[layerNum]
        for i in range(len(layer.nodes)):
            layer.setNodeWeights(i, tweights[i])
        
    # Returns an arr of default weights of length
    def InitializeLayer(self, length, nextLen):
        arr = []
        for i in range(length):
            arrJ = []
            for j in range(nextLen):
                arrJ.append(0)#random.uniform(0,1)) #Default val
            arr.append(arrJ)
            
        return arr
    
    def print(self):
        for i in range(len(self.layers)):
            print("Layer " + str(i))
            for j in range(len(self.layers[i].nodes)):
                print(str(self.layers[i].nodes[j].total) + ", " +
                    str(self.layers[i].nodes[j].weights))
       





    

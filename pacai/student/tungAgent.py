from pacai.core.directions import Directions
from pacai.agents.capture.reflex import ReflexCaptureAgent

def createTeam(firstIndex, secondIndex, isRed,
        first = 'pacai.agents.capture.dummy.DummyAgent',
        second = 'pacai.agents.capture.dummy.DummyAgent'):
    """
    This function should return a list of two agents that will form the capture team,
    initialized using firstIndex and secondIndex as their agent indexed.
    isRed is True if the red team is being created,
    and will be False if the blue team is being created.
    """

    firstAgent = OffensiveAgent
    secondAgent = DefensiveAgent

    return [
        firstAgent(firstIndex),
        secondAgent(secondIndex),
    ]

class OffensiveAgent(ReflexCaptureAgent):

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = super().getFeatures(gameState, action)
        successor = self.getSuccessor(gameState, action)

        # 1. Compute distance to the nearest food.
        foodList = self.getFood(successor).asList()
        myPos = successor.getAgentState(self.index).getPosition()

        if len(foodList) > 0:
            minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
            features['distanceToFood'] = minDistance

        # 2. Compute distance to the nearest capsule.
        capsules = self.getCapsules(successor)
        if len(capsules) > 0:
            minDistance = min([self.getMazeDistance(myPos, capsule) for capsule in capsules])
            features['distanceToCapsule'] = minDistance

        # 3. Compute distance to the nearest enemy.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        enemies = [a for a in enemies if a.getPosition() is not None]
        if len(enemies) > 0:
            minDistance = min([self.getMazeDistance(myPos, e.getPosition()) for e in enemies])
            features['distanceToEnemy'] = minDistance

        # Compute distance to the nearest scared enemy.
        scaredEnemies = [a for a in enemies if a._scaredTimer > 0]
        if len(scaredEnemies) > 0:
            minDistance = min([self.getMazeDistance(myPos, e.getPosition()) for e in scaredEnemies])
            features['distanceToScaredEnemy'] = minDistance

        # 4. Add a feature to discourage stopping.
        if action == Directions.STOP:
            features['stop'] = 1
        else:
            features['stop'] = 0

        return features

    def getWeights(self, gameState, action):
        return {
            'successorScore': 100,
            'distanceToFood': -5, 
            'distanceToCapsule': -2,
            'distanceToEnemy': 2,
            'distanceToScaredEnemy': -10,
            'stop': -100,
        }

class DefensiveAgent(ReflexCaptureAgent):

    """
    A reflex agent that tries to keep its side Pacman-free.
    This is to give you an idea of what a defensive agent could be like.
    It is not the best or only way to make such an agent.
    """

    def __init__(self, index, **kwargs):
        super().__init__(index)

    def getFeatures(self, gameState, action):
        features = {}

        successor = self.getSuccessor(gameState, action)
        myState = successor.getAgentState(self.index)
        myPos = myState.getPosition()

        # Computes whether we're on defense (1) or offense (0).
        features['onDefense'] = 1
        if (myState.isPacman()):
            features['onDefense'] = 0

        # Computes distance to invaders we can see.
        enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
        invaders = [a for a in enemies if a.isPacman() and a.getPosition() is not None]
        features['numInvaders'] = len(invaders)

        if (len(invaders) > 0):
            dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
            features['invaderDistance'] = min(dists)

        if (action == Directions.STOP):
            features['stop'] = 1

        rev = Directions.REVERSE[gameState.getAgentState(self.index).getDirection()]
        if (action == rev):
            features['reverse'] = 1

        return features

    def getWeights(self, gameState, action):
        return {
            'numInvaders': -1000,
            'onDefense': 100,
            'invaderDistance': -10,
            'stop': -100,
            'reverse': -2
        }
    

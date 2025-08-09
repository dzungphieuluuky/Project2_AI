class Cell:
    def __init__(self, x: int, y: int) -> None:
        """Initialize an empty tile"""
        self.__isPit = False
        self.__isBreeze = False
        self.__isWumpus = False
        self.__isStench = False
        self.__isGold = False
        self.__isPlayer = False
        self._safe = False
        self._dangerous = False
        self.__visited = False
        self.name_state = ["Pit", "Breeze", "Wumpus", "Stench",
                          "Gold", "Player", "Safe", "Dangerous", "Visited"]
        self.location = (x, y)

    def states(self):
        return [
            self.__isPit, self.__isBreeze, self.__isWumpus, self.__isStench,
            self.__isGold, self.__isPlayer, self._safe, self._dangerous, self.__visited
        ]
    
    # Getters
    def getPit(self) -> bool:
        return self.__isPit

    def getBreeze(self) -> bool:
        return self.__isBreeze

    def getWumpus(self) -> bool:
        return self.__isWumpus

    def getStench(self) -> bool:
        return self.__isStench

    def getGold(self) -> bool:
        return self.__isGold
    
    def getPlayer(self) -> bool:
        return self.__isPlayer
    
    def isSafe(self) -> bool:
        return self._safe

    def isDangerous(self) -> bool:
        return self._dangerous
    
    def isVisited(self) -> bool:
        return self.__visited
    
    # Setters
    def setPit(self) -> None:
        self.__isPit = True

    def setBreeze(self) -> None:
        self.__isBreeze = True
    
    def setWumpus(self) -> None:
        self.__isWumpus = True

    def setStench(self) -> None:
        self.__isStench = True

    def setGold(self) -> None:
        self.__isGold = True

    def setPlayer(self) -> None:
        self.__isPlayer = True

    def markSafe(self) -> None:
        self._safe = True
        self._dangerous = False

    def markDangerous(self) -> None:
        self._dangerous = True
        self._safe = False

    def setVisited(self) -> None:
        self.__visited = True

    # Removers
    def removeWumpus(self) -> None:
        self.__isWumpus = False

    def removeStench(self) -> None:
        self.__isStench = False

    def removeGold(self) -> None:
        self.__isGold = False
    
    def removePlayer(self) -> None:
        self.__isPlayer = False

    ################################# DEBUGGING #################################
    
    def printTile(self) -> str:
        string = ''
        if self.__isPit:
            string += '🫓 '
        if self.__isBreeze:
            string += '💨 '
        if self.__isWumpus:
            string += '👻 '
        if self.__isStench:
            string += '💩 '
        if self.__isGold:
            string += '🥇 '
        if self.__isPlayer:
            string += '🤖 '
        if self._safe:
            string += '✅ '
        if self._dangerous:
            string += '❌ '
        if self.__visited:
            string += '👁️ '
        return string
    
    def reset_safety_status(self) -> None:
        self._safe = False
        self._dangerous = False
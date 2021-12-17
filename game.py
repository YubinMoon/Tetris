import os
import sys
import time
import random
import numpy as np
import pygame
from pygame.constants import K_LEFT

def resource_path(relative_path):  # 파일 절대경로 추적
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class Container(pygame.Surface):
    def __init__(self, size):
        global blockList
        super().__init__(size, pygame.SRCALPHA, 32)
        setImage()
        self.background = pygame.transform.scale(pygame.image.load(
            resource_path("src/container.png")), size).convert_alpha()
        # self.currentBlock = Tetromino()
        blockList = []
        self.ground = Ground((450, 900))
        self.nextBox = NextBlock(150, 1)
        self.keepBox = KeepBlock(150)
        self.nextBox.makeList()
        self.ground_rect = self.ground.get_rect(topleft=(20, 20))
        self.keepBox_rect = self.keepBox.get_rect(topleft=(500, 317))
        self.nextBox_rect = self.nextBox.get_rect(topleft=(500, 78))
        self.status = Status((170, 423))
        self.status_rect = self.status.get_rect(topleft=(490, 497))
        self.tList = []  # 출력 리스트
        self.FPS = [0 for _ in range(5)]
        self.initValue()

    #변수 초기화
    def initValue(self):
        self.blockDownTime = 0
        self.floorinvincibilityTime = 0
        self.maxFloorinvincibilityTime = 0
        self.keyMoveRelease = 0
        self.keyMoveRepeat = 0
        self.keyDownRelease = 0
        self.keyDownRepeat = 0
        self.BLOCK_DOWN_TIME = 200
        self.ereaseBlock = 0
        self.keepCan = True

    def update(self, dt: int, key: dict):
        output = []
        self.FPS.pop(0)
        self.FPS.append(1000/dt)
        self.keyInput(dt, key)
        self.blockDown(dt)
        self.ground.gameOverCheck(output)
        self.BLOCK_DOWN_TIME = self.ground.speed
        return output

    def keyInput(self, dt: int, key: dict):
        if key[pygame.K_LEFT] or key[pygame.K_RIGHT]:
            x = 1 if key[pygame.K_RIGHT] else -1
            if self.keyMoveRelease == 0:
                self.ground.move(x)
            self.keyMoveRelease += dt
            self.keyMoveRepeat += dt
            self.floorinvincibilityTime = 0
            if self.keyMoveRelease > KEY_RELEASE_TIME and self.keyMoveRepeat > KEY_REPEAT_TIME:
                self.keyMoveRepeat = 0
                self.ground.move(x)
        else:
            self.keyMoveRelease = 0
            self.keyMoveRepeat = 0
        if key[pygame.K_UP]:
            self.ground.rotateRight()
            self.floorinvincibilityTime = 0
            key[pygame.K_UP] = False
        if key[pygame.K_DOWN]:
            if self.keyDownRelease == 0:
                self.blockDownTime += self.BLOCK_DOWN_TIME
                self.floorinvincibilityTime = INVINCIBILITY_TIME
            self.keyDownRelease += dt
            self.keyDownRepeat += dt
            if self.keyDownRelease > KEY_RELEASE_TIME and self.keyDownRepeat > KEY_REPEAT_TIME:
                self.keyDownRepeat = 0
                self.blockDownTime = self.BLOCK_DOWN_TIME
                self.floorinvincibilityTime = INVINCIBILITY_TIME
        else:
            self.keyDownRelease = 0
        if key[pygame.K_SPACE]:
            key[pygame.K_SPACE] = False
            self.maxFloorinvincibilityTime = MAX_INVINCIBILITY_TIME
            while not self.ground.isBlockFloor():
                self.blockDown(100)
        if key[pygame.K_z] and self.keepCan:
            self.keepCan = False
            self.keep()

    def get_status(self):
        status = {
            "score": self.ground.score,
            "speed": self.ground.speed,
            "ereaseBlock": self.ground.ereaseBlock
        }
        return status

    def get_score(self):
        return self.ground.score

    def get_speed(self):
        return self.ground.speed

    def blockDown(self, dt: int):
        if self.ground.isBlockFloor():
            self.blockDownTime = 0
            self.floorinvincibilityTime += dt
            self.maxFloorinvincibilityTime += dt
            if self.floorinvincibilityTime > INVINCIBILITY_TIME or self.maxFloorinvincibilityTime > MAX_INVINCIBILITY_TIME:
                self.floorinvincibilityTime = 0
                self.maxFloorinvincibilityTime = 0
                self.keyDownRelease = 0
                self.changeBlock()
                self.keepBox.holded = False
                self.keepCan = True
        else:
            self.floorinvincibilityTime = 0
            self.blockDownTime += dt
            while self.blockDownTime > self.BLOCK_DOWN_TIME:
                self.blockDownTime -= self.BLOCK_DOWN_TIME
                self.ground.move(y=1)

    def changeBlock(self):
        self.ground.newBlock(self.nextBox.getBlock())
        self.ground.floorRemove()

    def keep(self):
        self.keepBox.holded = True
        if self.keepBox.type:
            temp = self.keepBox.type
            self.keepBox.setType(self.ground.type)
            self.ground.newBlock(temp, False)
        else:
            self.keepBox.setType(self.ground.type)
            self.ground.newBlock(self.nextBox.getBlock(), flag=False)

    def set_draw(self):
        self.tList.append("FPS: %d" % np.mean(self.FPS))
        self.tList.append("SCORE: %d" % (self.get_score()))
        self.tList.append("SPEED: %d" % (self.get_speed()))

        self.ground.draw()
        self.keepBox.draw()
        self.nextBox.draw()
        self.status.draw(self.tList)
        self.tList.clear()

    def draw(self):
        self.set_draw()
        self.blit(self.background, (0, 0))
        self.blit(self.ground, (self.ground_rect.x, self.ground_rect.y))
        self.blit(self.keepBox, (self.keepBox_rect.x, self.keepBox_rect.y))
        self.blit(self.nextBox,
                  (self.nextBox_rect.x, self.nextBox_rect.y))
        self.blit(self.status, (self.status_rect.x, self.status_rect.y))
        # pygame.draw.rect(self, (0, 255, 0), self.boxRect, 1)
        # pygame.draw.rect(self, (0, 255, 0), self.nextBlockRect, 1)
        # pygame.draw.rect(self, (0, 255, 0), self.status_rect, 1)


class Ground(pygame.Surface):  # 게임 화면
    def __init__(self, size: tuple = (200, 400), type: str = None):
        super().__init__(size, pygame.SRCALPHA, 32)
        self.type = type if type else "I"
        self.blockSize = size[0]/10
        self.blockList = []  # 고정된 블록
        self.ereaseBlock = 0
        self.block = None
        self.score = 0
        self.set_speed()
        self.newBlock(type)

    def set_speed(self):
        self.speed = int(40000/7/(self.ereaseBlock+100/7))

    def newBlock(self, type: str = None, flag: bool = True):
        if self.block and flag:
            self.blockList += [(i[0]+self.toX, i[1]+self.toY, self.type)
                               for i in self.block]
        self.type = type if type else getRandType()
        self.blockImage = getImage(self.type)
        self.block = BLOCK_LIST[self.type]
        self.rotateValue = ROTATE_VALUE[self.type]
        self.toX = 4 if self.type != "I" else 3
        self.toY = -2

    def blockCollision(self, block: list, x: int = 0, y: int = 0):
        for b in block:
            if isIncluded((b[0]+x, b[1]+y), self.blockList) or \
                    not (0 <= b[0]+x < MAP_WIDTH and b[1]+y < MAP_HEIGHT):
                return True
        return False

    def move(self, x: int = 0, y: int = 0):
        if not self.blockCollision(self.block, self.toX+x, self.toY+y):
            self.toX += x
            self.toY += y

    def rotateRight(self, dir: int = 1):
        temp = [(i[0]-self.rotateValue[0], i[1]-self.rotateValue[1])
                for i in self.block]
        temp = [(-i[1]*dir, i[0]*dir) for i in temp]
        temp = [(int(i[0]+self.rotateValue[1]), int(i[1]+self.rotateValue[0]))
                for i in temp]
        if not self.rotateCollision(temp):
            self.block = temp

    def rotateCollision(self, tempBlock: list, val: list = 0):
        self.testValue = [(0, 0), (0, 1), (1, 0), (-1, 0), (1, 1), (-1, 1), (0, -1),
                          (0, -2), (2, 0), (-2, 0), (1, -1), (-1, -1)]
        if val == len(self.testValue):
            return True
        if self.blockCollision(tempBlock, self.toX + self.testValue[val][0], self.toY + self.testValue[val][1]):
            return self.rotateCollision(tempBlock, val+1)
        self.toX += self.testValue[val][0]
        self.toY += self.testValue[val][1]
        return False

    def isBlockFloor(self, n: int = 1):
        return self.blockCollision(self.block, self.toX, self.toY + n)

    def get_block(self):
        return [(i[0]+self.toX, i[1]+self.toY, self.type) for i in self.block]

    #칸 제거
    def floorRemove(self):
        ereaseBlock = 0
        mapList = [0 for _ in range(MAP_HEIGHT)]
        temp = []
        for i in self.blockList:
            if i[1] >= 0:
                mapList[i[1]] += 1
        c = 0
        for idx, val in enumerate(mapList):
            if val == MAP_WIDTH:
                ridx = idx
                mapList[ridx] = 0
                c += 1
                for k, i in enumerate(self.blockList):
                    if i[1] < ridx:
                        a = sumPos(i, (0, 1))
                        temp.append((a[0], a[1], i[2]))
                    elif i[1] > ridx:
                        temp.append(i)
                self.blockList = temp.copy()
                temp.clear()
                ereaseBlock += 1
                self.ereaseBlock += 1

        self.score += pow(ereaseBlock, 2)
        #속도 증가
        self.set_speed()

    #예상 블록 위치
    def drawForecastBlock(self):
        y = 0
        a = False
        while True:
            for i in self.block:
                if self.isBlockFloor(y+1):
                    a = True
                    break
            else:
                y += 1
            if a:
                break
        for i in self.block:
            self.blit(getImage("B"), ((i[0]+self.toX)*self.blockSize,
                                      (i[1]+self.toY+y)*self.blockSize))

    def gameOverCheck(self, output: list):
        for i in self.blockList:
            if i[1] < 0:
                output.append(GAMEOVER)

    #전체 출력
    def draw(self):
        self.fill(pygame.Color(0, 0, 0, 0))
        for i in self.blockList:
            self.blit(getImage(i[2]),
                      (i[0]*self.blockSize, i[1]*self.blockSize))
        self.drawForecastBlock()
        for i in self.block:
            self.blit(self.blockImage, ((i[0]+self.toX)*self.blockSize,
                                        (i[1]+self.toY)*self.blockSize))


class KeepBlock(pygame.Surface):
    def __init__(self, size, type=None):
        super().__init__((size, size), pygame.SRCALPHA)
        self.size = size
        self.rect = (10, 10, 10+size, 10+size)
        self.type = type
        self.holded = False

    def init(self):
        if self.type == "I":
            self.blockSize = self.size/4
            self.toX = 0
            self.toY = -self.blockSize/2
        elif self.type == "O":
            self.blockSize = self.size/3
            self.toX = self.blockSize/2
            self.toY = self.blockSize/2
        elif self.type in "JLSZT":
            self.blockSize = self.size/3
            self.toX = 0
            self.toY = self.blockSize/2

    def setType(self, type):
        self.type = type
        self.blockList = BLOCK_LIST[type]
        self.init()

    def draw(self):
        self.fill(pygame.Color(255, 255, 255, 0))
        if self.type:
            if self.holded:
                for i in self.blockList:
                    self.blit(pygame.transform.scale(getImage("H"), (self.blockSize, self.blockSize)),
                              (i[0]*self.blockSize+self.toX, i[1]*self.blockSize+self.toY))
            else:
                for i in self.blockList:
                    self.blit(pygame.transform.scale(getImage(self.type), (self.blockSize, self.blockSize)),
                              (i[0]*self.blockSize+self.toX, i[1]*self.blockSize+self.toY))


class NextBlock(pygame.Surface):
    def __init__(self, size, num):
        super().__init__((size, size), pygame.SRCALPHA)
        self.size = size
        self.num = num
        self.list = []

    def makeList(self, type=None):
        while len(self.list) < self.num:
            self.list.append(getRandType())

    def getBlock(self):
        temp = self.list.pop(0)
        self.makeList()
        return temp

    def init(self, type):
        if type == "I":
            self.blockSize = self.size/4
            self.toX = 0
            self.toY = -self.blockSize/2
        elif type == "O":
            self.blockSize = self.size/3
            self.toX = self.blockSize/2
            self.toY = self.blockSize/2
        elif type in "JLSZT":
            self.blockSize = self.size/3
            self.toX = 0
            self.toY = self.blockSize/2

    def draw(self):
        self.fill(pygame.Color(255, 255, 255, 0))
        self.init(self.list[0])
        for i in BLOCK_LIST[self.list[0]]:
            self.blit(pygame.transform.scale(getImage(self.list[0]), (self.blockSize, self.blockSize)),
                      (i[0]*self.blockSize+self.toX, i[1]*self.blockSize+self.toY))


class Status(pygame.Surface):
    def __init__(self, size):
        super().__init__(size, pygame.SRCALPHA)
        self.font = pygame.font.SysFont("arial", 30, True)
        self.size = size

    def draw(self, set: list):
        tList = []
        num = len(set)
        for str in set:
            tList.append(self.font.render(str, True, (255, 255, 255)))
        self.fill(pygame.Color(0, 0, 0, 0))
        for i, text in enumerate(tList):
            self.blit(text, (10, 10+i*30))


def sumPos(a, b):  # 좌표 더하기
    return ((a[0] + b[0]), (a[1] + b[1]))


def isIncluded(a, map):
    for b in map:
        if (a[0], a[1]) == (b[0], b[1]):
            return True
    return False


blockList = []


def getRandType():  # 블록 타임 뽑기
    global blockList
    if len(blockList) == 0:
        blockList = list("IOZSJLT")
    a = random.choice(blockList)
    blockList.remove(a)
    return a


def getImage(type):
    return BLOCK_IMAGE[type]


def setImage():
    for i in "IOZSJLTBH":
        BLOCK_IMAGE[i] = pygame.image.load(
            resource_path("src/block/%s.png" % i)).convert()


MAP_WIDTH = 10
MAP_HEIGHT = 20
BLOCK_LIST = {
    "I": [(0, 2), (1, 2), (2, 2), (3, 2)],
    "O": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "Z": [(0, 0), (1, 0), (1, 1), (2, 1)],
    "S": [(1, 0), (2, 0), (0, 1), (1, 1)],
    "J": [(0, 0), (0, 1), (1, 1), (2, 1)],
    "L": [(2, 0), (0, 1), (1, 1), (2, 1)],
    "T": [(1, 0), (0, 1), (1, 1), (2, 1)]
}
ROTATE_VALUE = {
    "I": (1.5, 1.5),
    "O": (0.5, 0.5),
    "Z": (1, 1),
    "S": (1, 1),
    "J": (1, 1),
    "L": (1, 1),
    "T": (1, 1)
}
KEY_RELEASE_TIME = 200
KEY_REPEAT_TIME = 50
INVINCIBILITY_TIME = 500
MAX_INVINCIBILITY_TIME = 5000
MAP_X = 200
MAP_Y = 400

BLOCK_IMAGE = {}

SCORE = [0, 1, 3, 6, 10]

GAMEOVER = 400

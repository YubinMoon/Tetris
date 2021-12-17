import os
import math
import pygame


class mainDisplay():
    def __init__(self):
        self.background = pygame.image.load(
            os.path.join(current_path, "container.png"))
        self.rect = self.background.get_rect(
            center=(screen_width//2, screen_height//2))
        self.map = []
        for i in range(20):
            self.map.append(list(".........."))
        self.currentBlock = None
        self.blockSize = (self.rect.right - self.rect.left)//10
        self.currentTime = 0
        self.floorTime = 0
        self.isFloor = False

    def makeCurrentBlock(self):
        if not self.currentBlock:
            self.currentBlock = tetromino(self, "T")
            self.currentBlock.makeBlock()

    def moveCurrentBlock(self):
        global toRight, toLeft, toUp
        if toRight:
            self.currentBlock.moveRight()
            toRight = False
        if toLeft:
            self.currentBlock.moveLeft()
            toLeft = False
        if toUp:
            self.currentBlock.rotateRight()
            self.floorTime = 0
            self.isFloor = False
            toUp = False

    def blockDown(self, dt):
        self.currentTime += dt
        self.floorTime += dt
        if self.currentTime > BLOCK_TICK:
            self.currentTime = 0
            self.isFloor = self.currentBlock.down()
        if self.isFloor and self.floorTime > MAX_FLOOR_TICK:
            self.floorTime = 0
            self.isFloor = False
            self.currentBlock.setMap()
            self.currentBlock = tetromino(self, "I")

    def drawMap(self):
        for y, i in enumerate(self.map):
            for x, type in enumerate(i):
                if type == ".":
                    continue
                screen.blit(
                    blockImage[0], (self.rect.left+x*self.blockSize, self.rect.top+y*self.blockSize))

    def draw(self):
        screen.blit(self.background, self.rect)
        self.drawMap()
        self.currentBlock.draw()


class block(pygame.sprite.Sprite):
    def __init__(self, type, image):
        super().__init__()
        self.type = type
        self.block = image


class tetromino():
    def __init__(self, container, type):
        self.container = container
        self.type = type
        self.blockList = BLOCK_LIST[type]
        self.rotateValue = ROTATE_VALUE[type]
        self.map = []
        for i in range(20):
            self.map.append(list(".........."))
        self.toX = 0
        self.toY = 0
        self.clearMap()

    def clearMap(self):
        self.map.clear()
        for i in range(20):
            self.map.append(list(".........."))

    def moveRight(self):
        self.toX += 1

    def moveLeft(self):
        self.toX -= 1

    def rotateRight(self):
        mainMap = self.container.map
        temp = [(i[0]-self.rotateValue[0], i[1]-self.rotateValue[1])
                for i in self.blockList]
        temp = [(-i[1], i[0]) for i in temp]
        temp = [(int(i[0]+self.rotateValue[1]), int(i[1]+self.rotateValue[0]))
                for i in temp]
        self.blockList = temp
        self.availabilityCheck()

    def makeBlock(self):
        for i in self.blockList:
            self.map[i[1]+self.toY][i[0]+self.toX] = self.type

    def down(self):
        mainMap = self.container.map
        for i in self.blockList:
            if i[1]+self.toY == MAP_HEIGHT-1:
                return True
            elif mainMap[i[1]+self.toY+1][i[0]+self.toX] != ".":
                return True
        self.toY += 1

    def wallCollision(self):
        for i in self.blockList:
            if i[0] + self.toX < 0:
                self.toX += -(i[0] + self.toX)
            elif i[0] + self.toX > MAP_WIDTH - 1:
                self.toX -= (i[0] + self.toX) - (MAP_WIDTH - 1)
            if i[1] + self.toY > MAP_HEIGHT - 1:
                self.toY -= (i[1] + self.toY) - (MAP_HEIGHT - 1)

    def availabilityCheck(self):
        for i in self.blockList:
            if i[0] + self.toX < 0:
                self.toX += -(i[0] + self.toX)
            elif i[0] + self.toX > MAP_WIDTH - 1:
                self.toX -= (i[0] + self.toX) - (MAP_WIDTH - 1)
            if i[1] + self.toY > MAP_HEIGHT - 1:
                self.toY -= (i[1] + self.toY) - (MAP_HEIGHT - 1)

    def setMap(self):
        mainMap = self.container.map
        for i in self.blockList:
            mainMap[i[1]+self.toY][i[0]+self.toX] = self.type

    def draw(self):
        self.clearMap()
        self.availabilityCheck()
        for i in self.blockList:
            self.map[i[1]+self.toY][i[0]+self.toX] = self.type
        for y, i in enumerate(self.map):
            for x, type in enumerate(i):
                if type == ".":
                    continue
                screen.blit(blockImage[0], (self.container.rect.left+x*self.container.blockSize,
                            self.container.rect.top+y*self.container.blockSize))


#초기화
pygame.init()

#화면 크기 설정
screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode((screen_width, screen_height))

#화면 타이틀 설정
pygame.display.set_caption("TETRIS")

#FPS
clock = pygame.time.Clock()

#1. 사용자 게임 초기화
BLOCK_TICK = 200
MAX_FLOOR_TICK = 500
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
current_path = os.path.dirname(__file__)
background = pygame.image.load(os.path.join(current_path, "background.png"))
firstMap = mainDisplay()
spriteGroup = pygame.sprite.Group()
blockImage = [pygame.image.load(os.path.join(current_path, "red.png"))]
toRight = False
toLeft = False
toUp = False
toDown = False

running = True
while running:
    dt = clock.tick(60)

    #2. 이벤트 처리
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                toRight = True
            if event.key == pygame.K_LEFT:
                toLeft = True
            if event.key == pygame.K_UP:
                toUp = True
            if event.key == pygame.K_DOWN:
                toDOWN = True
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_RIGHT:
                toRight = False
            if event.key == pygame.K_LEFT:
                toLeft = False
            if event.key == pygame.K_UP:
                toUp = False
            if event.key == pygame.K_DOWN:
                toDOWN = False

    #3. 게임 캐릭터 위치 정의
    firstMap.makeCurrentBlock()
    #4. 충돌처리
    firstMap.moveCurrentBlock()
    firstMap.blockDown(dt)

    #5.화면에 그리기
    screen.blit(background, (0, 0))
    firstMap.draw()
    #spriteGroup.draw(screen)
    pygame.display.update()

pygame.quit()

import os
import sys
import time
import random
import numpy as np
import pygame
import datetime
import tetris.constants as Constants


def resource_path(relative_path):  # 파일 절대경로 추적
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


class Container(pygame.Surface):  # 메인 컨테이너
  def __init__(self, size):
    super().__init__(size, pygame.SRCALPHA, 32)
    setImage()  # 이미지 로딩
    self.background = pygame.transform.scale(pygame.image.load(
        resource_path("src/container.png")), size).convert_alpha()
    self.ground = Ground((450, 900))  # 게임판
    self.keepBox = KeepBlock(150)  # KEEP
    self.status = Status((170, 423))  # 상태 표시
    #출력 위치
    self.ground_rect = self.ground.get_rect(topleft=(20, 20))
    self.keepBox_rect = self.keepBox.get_rect(topleft=(500, 317))
    self.status_rect = self.status.get_rect(topleft=(490, 497))
    self.nextBox_rect = self.ground.nextBox.get_rect(
        topleft=(500, 78))  # 출력 위치
    self.state_list = []  # 출력 리스트
    self.FPS = [0 for _ in range(5)]  # FPS 평균값
    self.initValue()

  #변수 초기화
  def initValue(self):
    self.block_fall_time = 0
    self.floor_invincibility_time = 0
    self.max_floor_invincibility_time = 0
    self.key_move_release = 0
    self.key_move_repeat = 0
    self.key_down_release = 0
    self.key_down_repeat = 0
    self.ereased_block = 0
    self.keep_chance = True
    self.BLOCK_DOWN_TIME = 200

  # 화면 업데이트
  def update(self, dt: int, key: dict):
    output = []
    self.FPS.pop(0)
    self.FPS.append(1000/dt)  # 프레임 저장
    self.keyInput(dt, key)  # 키 입력
    self.blockDown(dt)  # 블록 하강
    self.BLOCK_DOWN_TIME = self.ground.speed  # 하강 속도 업데이트
    return self.ground.gameOverCheck()  # 게임 오버 체크

  def keyInput(self, dt: int, key: dict):
    if key[pygame.K_LEFT] or key[pygame.K_RIGHT]:
      # 이동 방향 설정
      x = -1 if not key[pygame.K_RIGHT] else 1 if not key[pygame.K_LEFT] else 0
      if self.key_move_release == 0:  # 처음 눌릴 때
        self.ground.move(x)
      # 반복 입력 메커니즘
      self.key_move_release += dt
      self.floor_invincibility_time = 0
      if self.key_move_release > KEY_RELEASE_TIME:
        self.key_move_repeat += dt
        while self.key_move_repeat > KEY_REPEAT_TIME:
         self.key_move_repeat -= KEY_REPEAT_TIME
         self.ground.move(x)
    else:
      # 반복 입력 초기화
      self.key_move_release = 0
      self.key_move_repeat = 0
    if key[pygame.K_UP]:
      key[pygame.K_UP] = False  # 연속 입력 방지
      self.ground.rotate_block()
      self.floor_invincibility_time = 0
    if key[pygame.K_DOWN]:
      #블록 하강
      self.floor_invincibility_time = INVINCIBILITY_TIME
      if self.key_down_release == 0:
        self.block_fall_time = self.BLOCK_DOWN_TIME
        self.blockDown(dt)  # 블록 하강
      self.key_down_release += dt
      if self.key_down_release > KEY_RELEASE_TIME:
        self.key_down_repeat += dt
        while self.key_down_repeat > KEY_REPEAT_TIME:
          self.key_down_repeat -= KEY_REPEAT_TIME
          self.block_fall_time = self.BLOCK_DOWN_TIME
          self.blockDown(dt)  # 블록 하강
    else:
      self.key_down_release = 0
      self.key_down_repeat = 0
    if key[pygame.K_SPACE]:
      # 즉시 하강
      key[pygame.K_SPACE] = False  # 연속 입력 방지
      self.max_floor_invincibility_time = MAX_INVINCIBILITY_TIME  # 무적 해제
      while not self.ground.isBlockFloor():  # 반복 하강
        self.blockDown(10000)
    if key[pygame.K_z] and self.keep_chance:
      self.keep_chance = False
      self.keep()

  # 안쓰는 함수
  # def get_status(self):
  #   status = {
  #       "score": self.ground.score,
  #       "speed": self.ground.speed,
  #       "ereaseBlock": self.ground.ereaseBlock
  #   }
  #   return status

  def get_score(self): # 점수 반환
    now = datetime.datetime.now()
    score_lists = {
      "year": now.year,
      "month": now.month,
      "day": now.day,
      "hour": now.hour,
      "minute": now.minute,
      "second": now.second,
      "score": self.ground.score,
      "speed": self.ground.speed,
      "ereaseBlock": self.ground.ereaseBlock
    }
    return score_lists

  def get_speed(self):
    return self.ground.speed

  def blockDown(self, dt: int):
    if self.ground.isBlockFloor():  # 바닥에 닿았을 때
      self.block_fall_time -= self.BLOCK_DOWN_TIME
      self.floor_invincibility_time += dt
      self.max_floor_invincibility_time += dt
      if self.floor_invincibility_time > INVINCIBILITY_TIME or self.max_floor_invincibility_time > MAX_INVINCIBILITY_TIME:
        self.block_fall_time = 0
        self.floor_invincibility_time = 0
        self.max_floor_invincibility_time = 0
        self.key_down_release = 0
        self.ground.newBlock()  # 새로운 블록 배치
        self.ground.check_line()  # 바닥 제거
        self.keepBox.holded = False
        self.keep_chance = True
    else:
      self.floor_invincibility_time = 0
      self.block_fall_time += dt
      while self.block_fall_time > self.BLOCK_DOWN_TIME and not self.ground.isBlockFloor():
        self.block_fall_time -= self.BLOCK_DOWN_TIME
        self.ground.move(y=1)

  def keep(self):
    self.keepBox.holded = True
    if self.keepBox.type:  # KEEP이 비어있으면
      temp = self.keepBox.type
      self.keepBox.setType(self.ground.type)
      self.ground.newBlock(temp, False)
    else:
      self.keepBox.setType(self.ground.type)
      self.ground.newBlock(flag=False)

  def set_draw(self):  # 그리기
    self.state_list.clear()
    self.state_list.append("FPS: %d" % np.mean(self.FPS))
    self.state_list.append("SCORE: %d" % (self.ground.score))
    self.state_list.append("SPEED: %d" % (self.ground.speed))

    self.ground.draw()
    self.keepBox.draw()
    self.status.draw(self.state_list)

  def draw(self):  # 그리기
    self.set_draw()
    self.blit(self.background, (0, 0))
    self.blit(self.ground, (self.ground_rect.x, self.ground_rect.y))
    self.blit(self.ground.nextBox,
              (self.nextBox_rect.x, self.nextBox_rect.y))
    self.blit(self.keepBox, (self.keepBox_rect.x, self.keepBox_rect.y))
    self.blit(self.status, (self.status_rect.x, self.status_rect.y))


class Ground(pygame.Surface):  # 게임 화면
  def __init__(self, size: tuple = (200, 400), type: str = None):
    super().__init__(size, pygame.SRCALPHA)
    # self.type = type if type else "I"
    self.nextBox = NextBlock(150, 1)  # NEXT
    self.blockSize = size[0]/10
    self.placed_block = []  # 고정된 블록
    self.ereaseBlock = 0
    self.block = None
    self.score = 0
    self.nextBox.makeList()  # 시작 블록 생성
    self.set_speed()
    self.newBlock(type)

  def set_speed(self):  # 속도 식
    self.speed = int(40000/7/(self.ereaseBlock+100/7))

  def newBlock(self, type: str = None, flag: bool = True):  # 블록 생성
    if self.block and flag:
      self.placed_block += [(i[0]+self.toX, i[1]+self.toY, self.type)
                            for i in self.block]
    self.type = type if type else self.nextBox.getBlock()  # 블록 가져오기
    self.blockImage = getImage(self.type)
    self.block = BLOCK_LIST[self.type]
    self.rotateValue = ROTATE_VALUE[self.type]
    self.toX = 4 if self.type != "I" else 3  # 가로 출현 위치
    self.toY = -2

  def blockCollision(self, block: list, x: int = 0, y: int = 0):  # 충돌 체크 함수
    for b in block:
      if self.isIncluded((b[0]+x, b[1]+y)) or not (0 <= b[0]+x < MAP_WIDTH and b[1]+y < MAP_HEIGHT):
        return True
    return False

  def move(self, x: int = 0, y: int = 0):  # 블록 이동
    if not self.blockCollision(self.block, self.toX+x, self.toY+y):
      self.toX += x
      self.toY += y

  def rotate_block(self, dir: int = 1):  # 블록 회전
    temp = [(i[0]-self.rotateValue[0], i[1]-self.rotateValue[1])
            for i in self.block]
    temp = [(-i[1]*dir, i[0]*dir) for i in temp]
    temp = [(int(i[0]+self.rotateValue[1]), int(i[1]+self.rotateValue[0]))
            for i in temp]
    if not self.rotateCollision(temp):
      self.block = temp

  def rotateCollision(self, tmp_block: list, depth: list = 0):  # 회전 후 충돌 감지 및 재배치
    self.testValue = [(0, 0), (0, 1), (1, 0), (-1, 0), (1, 1), (-1, 1), (0, -1),
                      (0, -2), (2, 0), (-2, 0), (1, -1), (-1, -1)]
    if depth == len(self.testValue):
      return True
    if self.blockCollision(tmp_block, self.toX + self.testValue[depth][0], self.toY + self.testValue[depth][1]):
      return self.rotateCollision(tmp_block, depth+1)
    self.toX += self.testValue[depth][0]
    self.toY += self.testValue[depth][1]
    return False

  def isBlockFloor(self, n: int = 1):
    return self.blockCollision(self.block, self.toX, self.toY + n)

  # def get_block(self): # 블록 호출
  #   return [(i[0]+self.toX, i[1]+self.toY, self.type) for i in self.block]

  def check_line(self):  # 칸 제거
    ereased_block = 0
    mapList = [0 for _ in range(MAP_HEIGHT)]
    temp = []
    for i in self.placed_block:
      if i[1] >= 0:
        mapList[i[1]] += 1
    for idx, val in enumerate(mapList):
      if val == MAP_WIDTH:
        ridx = idx
        mapList[ridx] = 0
        for k, i in enumerate(self.placed_block):
          if i[1] < ridx:
            a = self.sumPos(i, (0, 1))
            temp.append((a[0], a[1], i[2]))
          elif i[1] > ridx:
            temp.append(i)
        self.placed_block = temp.copy()
        temp.clear()
        ereased_block += 1
        self.ereaseBlock += 1

    self.score += pow(ereased_block, 2)
    #속도 증가
    self.set_speed()

  def drawForecastBlock(self):  # 예상 블록 위치
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

  def isIncluded(self, a):
    for b in self.placed_block:
      if (a[0], a[1]) == (b[0], b[1]):
        return True
    return False

  def sumPos(self, a, b):  # 좌표 더하기
    return ((a[0] + b[0]), (a[1] + b[1]))

  def gameOverCheck(self):
    for i in self.placed_block:
      if i[1] < 0:
        return Constants.GAMEOVER

  def draw(self):  # 출력
    self.nextBox.draw()
    self.fill(pygame.Color(0, 0, 0, 0))
    for i in self.placed_block:
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
  def __init__(self, size, num_of_list, seed=None):
    super().__init__((size, size), pygame.SRCALPHA)
    if seed:
      random.seed(seed)
    self.size = size
    self.num_of_list = num_of_list
    self.list = []
    self.blockList = []

  def makeList(self, type=None):
    while len(self.list) < self.num_of_list:
      self.list.append(self.getRandType())

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

  def getRandType(self):  # 블록 타임 뽑기
    if not self.blockList:
      self.blockList = list("IOZSJLT")
    a = random.choice(self.blockList)
    self.blockList.remove(a)
    return a


class Status(pygame.Surface):
  def __init__(self, size):
    super().__init__(size, pygame.SRCALPHA)
    self.font = pygame.font.SysFont("arial", 30, True)
    self.size = size

  def draw(self, set: list):
    tList = []
    for str in set:
      tList.append(self.font.render(str, True, (255, 255, 255)))
    self.fill(pygame.Color(0, 0, 0, 0))
    for i, text in enumerate(tList):
      self.blit(text, (10, 10+i*30))


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
KEY_REPEAT_TIME = 60
INVINCIBILITY_TIME = 500
MAX_INVINCIBILITY_TIME = 5000

BLOCK_IMAGE = {}

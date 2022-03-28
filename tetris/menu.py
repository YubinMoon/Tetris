import os
import sys
import pygame
import tetris.constants as Constants


def resource_path(relative_path):  # 파일 절대경로 추적
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class Menu(pygame.Surface):
  def __init__(self, size):
    super().__init__(size, pygame.SRCALPHA)
    self.size = size
    self.fill(pygame.Color(0, 100, 100, 0))
    self.group = pygame.sprite.Group()

  def eventHandling(self, key):
    List = []
    self.group.update(key, List)
    return List

  def draw(self):
    self.group.draw(self)


class MainMenu(Menu):
  def __init__(self, size):
    super().__init__(size)
    self.init()

  def init(self):
    self.group.add(BTN("GAME START", Constants.GAMESTART))
    self.group.add(BTN("CONTROL", Constants.CONTROL))
    self.group.add(BTN("HISTORY", Constants.SCORE))
    self.group.add(BTN("EXIT", Constants.EXIT))
    num = -1.5
    for i in self.group:
      i.rect = i.image.get_rect(
          center=(self.size[0]/2, self.size[1]/2+num*200))
      num += 1


class PauseMenu(Menu):
  def __init__(self, size):
    super().__init__(size)
    self.init()

  def init(self):
    self.group = pygame.sprite.Group()
    self.group.add(BTN("CONTINUE", Constants.CONTINUE))
    self.group.add(BTN("RESTAET", Constants.RESTART))
    self.group.add(BTN("EXIT", Constants.MAINMENU))
    num = -1
    for i in self.group:
      i.rect = i.image.get_rect(
          center=(self.size[0]/2, self.size[1]/2+num*200))
      num += 1


class ScoreBoard(Menu):
  def __init__(self, size: tuple, score: list):
    super().__init__(size)
    self.score = score[-1]
    self.image = pygame.image.load(resource_path("src/board.png")).convert()
    self.rect = self.image.get_rect(center=(960, 410))
    self.initBTN()

  def initBTN(self):
    self.group = pygame.sprite.Group()
    a = BTN("MAIN MENU", Constants.MAINMENU)
    b = BTN("RESTART", Constants.RESTART)
    a.rect = a.image.get_rect(center=(self.size[0]/2, 850))
    b.rect = b.image.get_rect(center=(self.size[0]/2, 980))
    self.group.add(a)
    self.group.add(b)

  def get_nowTime_str(self):
    year = str(self.score["year"]).zfill(4)
    month = str(self.score["month"]).zfill(2)
    day = str(self.score["day"]).zfill(2)
    hour = str(self.score["hour"]).zfill(2)
    minute = str(self.score["minute"]).zfill(2)
    return "%s/%s/%s-%s:%s" % (year, month, day, hour, minute)

  def textSetting(self):
    point = 100
    surface = pygame.Surface(self.image.get_size(), flags=pygame.SRCALPHA)
    s = getImage("SCORE", (0, 0, 0), None)
    s_rect = s.get_rect(center=(surface.get_width()/2, point))
    point += 100
    score = getImage(str(self.score["score"]), (0, 0, 0), None)
    score_rect = score.get_rect(center=(surface.get_width()/2, point))
    point += 300
    t = getImage("TIME", (0, 0, 0), None)
    t_rect = t.get_rect(center=(surface.get_width()/2, point))
    point += 100
    time = getImage(self.get_nowTime_str(), (0, 0, 0), None, font_size=60)
    time_rect = time.get_rect(center=(surface.get_width()/2, point))
    surface.blit(s, (s_rect.x, s_rect.y))
    surface.blit(score, (score_rect.x, score_rect.y))
    surface.blit(t, (t_rect.x, t_rect.y))
    surface.blit(time, (time_rect.x, time_rect.y))
    return surface

  def draw(self):
    self.blit(self.image, (self.rect.x, self.rect.y))
    self.blit(self.textSetting(), (self.rect.x, self.rect.y))
    super().draw()


class ScoreHistory(Menu):
  def __init__(self, size: tuple, score: dict):
    super().__init__(size)
    self.score = score
    self.header = score[0]
    self.len = len(score) - 1
    self.line = 7
    self.page = 0
    self.Lpage = self.len//self.line
    self.init()

  def init(self):
    self.group = pygame.sprite.Group()
    a = BTN("MAINMENU", Constants.MAINMENU)
    a.rect = a.image.get_rect(center=(self.size[0]/2, self.get_height()-100))
    if self.page > 0:
      l = BTN("<", "LEFT")
      l.rect = l.image.get_rect(
          center=(self.size[0]/2-600, self.get_height()-100))
      self.group.add(l)
    if self.page < self.Lpage and self.len % self.line != 0:
      l = BTN(">", "RIGHT")
      l.rect = l.image.get_rect(
          center=(self.size[0]/2+600, self.get_height()-100))
      self.group.add(l)
    self.group.add(a)

  def eventHandling(self, key):
      l = super().eventHandling(key)
      if "LEFT" in l:
        self.page -= 1
        self.init()
      if "RIGHT" in l:
        self.page += 1
        self.init()
      return l

  def maketop(self):
    surface = pygame.Surface((self.size[0], 100), pygame.SRCALPHA)
    date = getImage("DATE", (255, 255, 255), None, (200, 100))
    time = getImage("TIME", (255, 255, 255), None, (200, 100))
    score = getImage("SCORE", (255, 255, 255), None, (300, 100))
    line = getImage("LINE", (255, 255, 255), None, (300, 100))
    speed = getImage("SPEED", (255, 255, 255), None, (300, 100))
    a = 200
    surface.blit(date, (a, 0))
    a += 400
    surface.blit(time, (a, 0))
    a += 270
    surface.blit(score, (a, 0))
    a += 270
    surface.blit(line, (a, 0))
    a += 270
    surface.blit(speed, (a, 0))
    return surface

  def makeLine(self, score):
    surface = pygame.Surface((self.size[0], 100), pygame.SRCALPHA)
    year = str(score["year"]).zfill(2)
    month = str(score["month"]).zfill(2)
    day = str(score["day"]).zfill(2)
    hour = str(score["hour"]).zfill(2)
    minute = str(score["minute"]).zfill(2)
    d = "%s/%s/%s" % (year, month, day)
    t = "%s:%s" % (hour, minute)
    d = getImage(d, (255, 255, 255), None, (400, 100))
    t = getImage(t, (255, 255, 255), None, (300, 100))
    S = getImage(str(score["score"]), (255, 255, 255), None, (200, 100))
    line = getImage(str(score["ereaseBlock"]),
                    (255, 255, 255), None, (200, 100))
    speed = getImage(str(score["speed"]), (255, 255, 255), None, (200, 100))
    a = 100
    surface.blit(d, (a, 0))
    a += 450
    surface.blit(t, (a, 0))
    a += 370
    surface.blit(S, (a, 0))
    a += 270
    surface.blit(line, (a, 0))
    a += 270
    surface.blit(speed, (a, 0))
    return surface

  def drawList(self):
    if self.page < self.Lpage:
      for i in range(self.line):
        self.blit(self.makeLine(
            self.score[-(self.line*self.page+i+1)]), (0, 200+i*100))
    else:
      for i in range(self.len % self.line):
        self.blit(self.makeLine(
            self.score[-(self.line*self.page+i+1)]), (0, 200+i*100))

  def draw(self):
    version = getImage(
        "version:"+self.header["version"], (255, 255, 255), None, (100, 30), 20)
    self.fill(pygame.Color(0, 0, 0, 0))
    self.blit(version, (30, 30))
    self.blit(self.maketop(), (0, 100))
    # self.blit(self.makeLine(self.score[1]),(0,200))
    self.drawList()
    super().draw()


class Control(Menu):
  def __init__(self, size):
    super().__init__(size)
    self.init()

  def init(self):
    self.group = pygame.sprite.Group()
    a = BTN("MAINMENU", Constants.MAINMENU)
    a.rect = a.image.get_rect(
        center=(self.get_width()/2, self.get_height()-100))
    self.group.add(a)
    self.consurface = pygame.Surface(self.size, pygame.SRCALPHA)
    controlList = []
    controlList.append("RIGHT: move right")
    controlList.append("LEFT: move left")
    controlList.append("UP: trun right")
    controlList.append("DOWN: soft drop")
    controlList.append("SPACE: hard drop")
    controlList.append("Z: hold")
    controlList.append("F: full screen toggle")
    controlList.append("M: bgm mute toggle")
    controlList.append("ESC: menu & quit")
    for n, i in enumerate(controlList):
      img = getImage(i, (255, 255, 255), None, (self.get_width(), 100), 75)
      self.consurface.blit(img, (0, n*90+70))

  def draw(self):
    self.blit(self.consurface, (0, 0))
    super().draw()


class BTN(pygame.sprite.Sprite):
  def __init__(self, text: str, clicked):
    super().__init__()
    self.text = text
    self.clicked = clicked
    self.normal = getImage(self.text, (255, 255, 255), (0, 0, 0))
    self.toggle = getImage(self.text, (0, 0, 0), (255, 255, 255))
    # self.image = getImage(self.text, (0, 255, 0), (255, 255, 255))
    self.image = self.normal

  def update(self, key: dict, List: list):
    pos = key["pos"]
    if self.rect.collidepoint(pos[0]*key["ratio_x"], pos[1]*key["ratio_x"]):
      if key["pressed"]:
        self.image = getImage(self.text, (0, 255, 0), (255, 255, 255))
      else:
        self.image = self.toggle
      if key["clicked"]:
        List.append(self.clicked)
    else:
      self.image = self.normal


def getImage(text, color, background, size: tuple = (500, 100), font_size=80):
  font = pygame.font.SysFont("Arial", font_size)
  textSurf = font.render(text, 1, color)
  image = pygame.Surface(size, pygame.SRCALPHA)
  if background:
    image.fill(background)
  trect = textSurf.get_rect(center=(size[0]/2, size[1]/2))
  image.blit(textSurf, trect)
  return image

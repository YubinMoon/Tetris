import os
import sys
import time
import ctypes
import socket
import threading
import json
import tetris.constants as Constants
import tetris.menu as Menu

from pygame._sdl2.video import Window
import pygame
from datetime import datetime
from tetris.game import Container
from pygame.constants import *


# 점수 설정

# def saveScore(score: dict):
#   global totalScore
#   now = datetime.now()
#   temp = {
#       "year": now.year,
#       "month": now.month,
#       "day": now.day,
#       "hour": now.hour,
#       "minute": now.minute,
#       "second": now.second,
#       "score": score["score"],
#       "speed": score["speed"],
#       "ereaseBlock": score["ereaseBlock"]
#   }
#   totalScore.append(temp)


def eventSet():  # 키 맵핑
  key[pygame.K_RIGHT] = False
  key[pygame.K_LEFT] = False
  key[pygame.K_UP] = False
  key[pygame.K_DOWN] = False
  key[pygame.K_SPACE] = False
  key[pygame.K_z] = False
  key[pygame.K_ESCAPE] = False
  key["clicked"] = False
  key["pressed"] = False
  key["ratio_x"] = 1
  key["ratio_y"] = 1
  key["pos"] = (0, 0)


class Controller:  # 앱 컨트롤
  def __init__(self):
    self.WINDOW = pygame.Surface((1920, 1080))  # SRCALPHA
    self.mainMenu = Menu.MainMenu(SCREEN_SIZE)

  def run(self):  # 시작
    self.menu()

  def music_off(self):
    bgm_game.fadeout(500)
    bgm_menu.fadeout(500)

  def draw_and_update(self, surface, location=(0, 0)):  # 화면 업데이트
    surface.draw()
    self.WINDOW.blit(background, (0, 0))
    self.WINDOW.blit(surface, location)
    SCREEN.blit(pygame.transform.scale(
        self.WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
    pygame.display.update()

  def menu(self):  # 메인메뉴
    self.music_off()
    bgm_menu.play(-1, fade_ms=500)
    while True:
      self.dt = clock.tick(FPS)
      self.eventHandler()
      if key[pygame.K_ESCAPE]:
        # 종료 코드 추가
        sys.exit()
      for i in self.mainMenu.eventHandling(key):  # 마우스 이벤트 처리
        # 종료 후 리턴
        if i == Constants.GAMESTART:
          self.playGame()
          bgm_menu.play(-1, fade_ms=500)
        elif i == Constants.CONTROL:
          self.control()
        elif i == Constants.SCORE:
          self.scoreHistory()
        elif i == Constants.EXIT:
          sys.exit()
      self.draw_and_update(self.mainMenu)

  def playGame(self):
    self.mainMap = Container((680, 940))  # 판 사이즈
    self.mainMap_rect = self.mainMap.get_rect(
        center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))  # 위치 설정
    self.music_off()
    bgm_game.play(-1, fade_ms=500)
    while True:
      self.dt = clock.tick(FPS)
      self.eventHandler()
      if key[pygame.K_ESCAPE]:  # 일시정지
        pygame.mixer.pause()
        event = self.pause()  # 이벤트 처리
        if event == Constants.MAINMENU:
          return
        elif event == Constants.RESTART:
          return self.playGame()
        pygame.mixer.unpause()
      if self.mainMap.update(self.dt, key) == Constants.GAMEOVER:  # 프레임 업데이트
        self.music_off()
        #event = self.scoreBoard()# HOT: 스코어보드
        return
      self.draw_and_update(
          self.mainMap, (self.mainMap_rect.x, self.mainMap_rect.y))

  def pause(self):
    pause = Menu.PauseMenu(SCREEN_SIZE)
    blur = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)  # 블러
    blur.fill(pygame.Color(0, 0, 0, 60))
    while True:
      self.dt = clock.tick(FPS)
      self.eventHandler()
      if key[pygame.K_ESCAPE]:
        key[pygame.K_ESCAPE] = False
        return
      for event in pause.eventHandling(key):  # 마우스 이벤트 처리
        return event  # 상위에서 처리
      pause.draw()
      self.WINDOW.blit(background, (0, 0))
      self.WINDOW.blit(
          self.mainMap, (self.mainMap_rect.x, self.mainMap_rect.y))
      self.WINDOW.blit(blur, (0, 0))
      self.WINDOW.blit(pygame.transform.smoothscale(
          pygame.transform.smoothscale(self.WINDOW, (160, 90)), SCREEN_SIZE), (0, 0))
      self.WINDOW.blit(pause, (0, 0))
      SCREEN.blit(pygame.transform.scale(
          self.WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
      pygame.display.update()

  # !!HOT!!: 업데이트 필요
  def scoreBoard(self):
    board = ScoreBoard(SCREEN_SIZE, self.mainMap.score)
    threading.Thread(target=savingScore).start()
    while True:
      self.dt = clock.tick(FPS)
      eventHandler()
      if key[pygame.K_ESCAPE]:
        key[pygame.K_ESCAPE] = False
        menu()
      for i in board.eventHandling(key):
        if i == "MAINMENU":
          menu()
        elif i == "RESTART":
          playGame()
      mainMap_rect = mainMap.get_rect(
          center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
      board.draw()
      a = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
      a.fill(pygame.Color(0, 0, 0, 60))
      self.WINDOW.blit(background, (0, 0))
      self.WINDOW.blit(mainMap, (mainMap_rect.x, mainMap_rect.y))
      self.WINDOW.blit(pygame.transform.smoothscale(
          pygame.transform.smoothscale(self.WINDOW, (160, 90)), SCREEN_SIZE), (0, 0))
      self.WINDOW.blit(a, (0, 0))
      self.WINDOW.blit(board, (0, 0))
      SCREEN.blit(pygame.transform.scale(
          self.WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
      pygame.display.update()

  # def scoreHistory():
  #   page = ScoreHistory(SCREEN_SIZE, totalScore)
  #   while True:
  #     self.dt = clock.tick(FPS)
  #     eventHandler()
  #     if key[pygame.K_ESCAPE]:
  #       key[pygame.K_ESCAPE] = False
  #       menu()
  #     for i in page.eventHandling(key):
  #       if i == "MAINMENU":
  #         return
  #     page.draw()
  #     self.WINDOW.blit(background, (0, 0))
  #     self.WINDOW.blit(page, (0, 0))
  #     SCREEN.blit(pygame.transform.scale(
  #         self.WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
  #     pygame.display.update()

  def control(self):
    con = Menu.Control(SCREEN_SIZE)
    while True:
      self.dt = clock.tick(FPS)
      self.eventHandler()
      if key[pygame.K_ESCAPE]:
        key[pygame.K_ESCAPE] = False
        return
      for i in con.eventHandling(key):  # 마우스 이벤트 처리
        if i == Constants.MAINMENU:
          return
      self.draw_and_update(con)

  def getUserName(self):
    text = font.render("Enter Your Name", True, "white")
    rect_text = text.get_rect(center=(SCREEN_WIDTH/2, (SCREEN_HEIGHT/2)-100))
    input = ""
    input_width = 700
    input_height = 120
    inputArea = pygame.rect.Rect((SCREEN_WIDTH-input_width)/2,
                                 (SCREEN_HEIGHT-input_height)/2, input_width, input_height)
    while True:
      self.dt = clock.tick(FPS)
      for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_RETURN:
            if len(input) > 1:
              return input
          elif event.key == pygame.K_BACKSPACE:
            input = input[:-1]
          elif event.key == pygame.K_ESCAPE:
            sys.exit()
          else:
            if len(input) < 15:
              if event.unicode in codeList:
                input += event.unicode
      text_input = font.render(input, True, "black")
      rect_text_input = text_input.get_rect(
          center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
      self.WINDOW.blit(background, (0, 0))
      pygame.draw.rect(self.WINDOW, (200, 200, 200),
                       inputArea, border_radius=60)
      pygame.draw.rect(self.WINDOW, (0, 0, 0), inputArea, 10, 60)
      self.WINDOW.blit(text_input, rect_text_input)
      self.WINDOW.blit(text, rect_text)
      SCREEN.blit(pygame.transform.scale(
          self.WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
      pygame.display.update()

  def eventHandler(self):  # 키 입력
    global SCREEN, SCREEN_SIZE
    key["clicked"] = False
    key[pygame.K_ESCAPE] = False
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        sys.exit()
      if event.type == pygame.KEYDOWN:
        key[event.key] = True
        if event.key == pygame.K_f:
          if SCREEN.get_flags() & NOFRAME:
            size = (1600, 900)
            SCREEN = pygame.display.set_mode(size, DOUBLEBUF)
            key["ratio_x"] = SCREEN_WIDTH/1600
            key["ratio_y"] = SCREEN_HEIGHT/900
            window.position = ((1920-1600)/2, (1080-900)/2)
          else:
            SCREEN = pygame.display.set_mode(
                SCREEN_SIZE, DOUBLEBUF | NOFRAME)
            key["ratio_x"] = 1
            key["ratio_y"] = 1
            window.position = (0, 0)
          pygame.display.update()
        if event.key == pygame.K_m:
          if bgm_game.get_volume() == 0:
            bgm_game.set_volume(0.1)
            bgm_menu.set_volume(0.3)
          else:
            bgm_game.set_volume(0)
            bgm_menu.set_volume(0)
      if event.type == pygame.KEYUP:
        key[event.key] = False
      if event.type == pygame.MOUSEBUTTONUP:
        key["clicked"] = True
        key["pressed"] = False
      if event.type == pygame.MOUSEBUTTONDOWN:
        key["pressed"] = True
    key["pos"] = pygame.mouse.get_pos()

  def get_header(self):  # 헤더 셋팅
    global HEADER
    check_dir(current_dir)
    if os.path.exists(headerdir):
      setting = json.load(open(headerdir, "r"))
      for set in setting.keys():
        HEADER[set] = setting[set]
    if "username" not in HEADER:
      HEADER["username"] = self.getUserName()
      HEADER["userID"] = socket.gethostname()
      json.dump(HEADER, open(headerdir, "w"))


def check_dir(dir):
  if not os.path.exists(dir):
    os.makedirs(dir)


def resource_path(relative_path):  # 파일 절대경로 추적
  try:
    base_path = sys._MEIPASS
  except Exception:
    base_path = os.path.abspath(".")
  return os.path.join(base_path, relative_path)


ctypes.windll.user32.SetProcessDPIAware()  # 윈도우 화면 배율 무시


pygame.init()

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF | NOFRAME)
FPS = 100
HEADER = {
    "name": "TETRIS",
    "maker": "YubinMoon",
    "version": "1.1.1",
}
SETTING = {
}
SERVERIP = "limeskin.kro.kr"
SERVERPORT = 21915

pygame.display.set_caption("TETRIS")  # title


clock = pygame.time.Clock()

#-> resource
font = pygame.font.SysFont("arial", 80, True)
background = pygame.image.load(resource_path("src/background.png")).convert()
icon = pygame.image.load(resource_path("src/icon.png"))
bgm_game = pygame.mixer.Sound(resource_path("src/bgm/game.wav"))
bgm_menu = pygame.mixer.Sound(resource_path("src/bgm/menu.wav"))
user_dir = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'), "Tetris")
current_dir = os.path.join(user_dir, HEADER["version"])
scoredir = os.path.join(current_dir, "score.json")
headerdir = os.path.join(current_dir, "setting.json")

bgm_menu.set_volume(0.3)
bgm_game.set_volume(0.1)

pygame.display.set_icon(icon)
key = {}  # button
codeList = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890_-"

totalScore = []
window = Window.from_display_module()  # 윈도우 위치

eventSet()
game = Controller()
game.run()

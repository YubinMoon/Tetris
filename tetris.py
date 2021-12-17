import os
import sys
import time
import ctypes
import pickle
import threading

from pygame._sdl2.video import Window
import pygame
from menu import Control, MainMenu, ScoreBoard, ScoreHistory, Control
from menu import PauseMenu
from menu import GAMESTART, CONTINUE, CONTROL, SCORE, EXIT, MAINMENU, RESTART
from datetime import datetime
from game import Container
from game import GAMEOVER
from pygame.constants import DOUBLEBUF, NOFRAME

ctypes.windll.user32.SetProcessDPIAware()  # 윈도우 화면 배율 무시


def resource_path(relative_path):  # 파일 절대경로 추적
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# 초기화
pygame.init()

# 화면 크기 설정
displayInfo = pygame.display.Info()
# SCREEN_WIDTH = displayInfo.current_w
# SCREEN_HEIGHT = displayInfo.current_h
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
SCREEN_SIZE = pygame.display.list_modes()[0]
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN = pygame.display.set_mode(SCREEN_SIZE, DOUBLEBUF | NOFRAME)
WINDOW = pygame.Surface((1920, 1080), pygame.SRCALPHA)
FPS = 30
HEADER = {
    "name": "TETRIS",
    "maker": "terry",
    "version": "10.3",
}
# 화면 타이틀 설정
pygame.display.set_caption("TETRIS")


# FPS
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 80, True)
background = pygame.image.load(resource_path("src/background.png")).convert()
icon = pygame.image.load(resource_path("src/icon.png"))
bgm_game = pygame.mixer.Sound(resource_path("src/bgm/game.wav"))
bgm_game.set_volume(0.1)
bgm_menu = pygame.mixer.Sound(resource_path("src/bgm/menu.wav"))
bgm_menu.set_volume(0.3)
pygame.display.set_icon(icon)
userdir = os.path.join(os.path.expandvars(r'%LOCALAPPDATA%'), "Tetris")
scoredir = os.path.join(userdir, "score.bin")
print(userdir)
key = {}


running = True
totalScore = []
window = Window.from_display_module()


def get_totalScore():
    global totalScore
    if not os.path.exists(userdir):
        os.makedirs(userdir)
    if os.path.exists(scoredir):
        totalScore = pickle.load(open(scoredir, "rb"))
    else:
        totalScore.append(HEADER)


threading.Thread(target=get_totalScore).start()


def savingScore():
    pickle.dump(totalScore, open(scoredir, "wb"))


def saveScore(score: dict):
    global totalScore
    now = datetime.now()
    temp = {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "score": score["score"],
        "speed": score["speed"],
        "ereaseBlock": score["ereaseBlock"]
    }
    totalScore.append(temp)


def eventSet():
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


eventSet()


def eventHandler():
    global running, SCREEN, SCREEN_SIZE
    key["clicked"] = False
    key[pygame.K_ESCAPE] = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
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


def menu():
    global running
    mainMenu = MainMenu(SCREEN_SIZE)
    bgm_game.fadeout(500)
    bgm_menu.fadeout(500)
    bgm_menu.play(-1, fade_ms=500)
    while running:
        dt = clock.tick(FPS)
        eventHandler()
        if key[pygame.K_ESCAPE]:
            running = False
            sys.exit()
        for i in mainMenu.eventHandling(key):
            if i == GAMESTART:
                bgm_menu.fadeout(500)
                playGame()
            elif i == CONTROL:
                control()
            elif i == SCORE:
                scoreHistory()
            elif i == EXIT:
                running = False
                bgm_menu.fadeout(500)
                sys.exit()
        mainMenu.draw()
        WINDOW.blit(background, (0, 0))
        WINDOW.blit(mainMenu, (0, 0))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


def playGame():
    global running
    mainMap = Container((680, 940))
    bgm_game.fadeout(500)
    bgm_game.play(-1, fade_ms=500)
    while running:
        dt = clock.tick(FPS)  # MAX FPS
        eventHandler()
        if key[pygame.K_ESCAPE]:
            pygame.mixer.pause()
            pause(mainMap)
            pygame.mixer.unpause()
        # 4. 충돌처리
        for i in mainMap.update(dt, key):
            if i == GAMEOVER:
                bgm_game.fadeout(500)
                saveScore(mainMap.get_status())
                scoreBoard(mainMap)
        mainMap_rect = mainMap.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        # 화면에 그리기
        WINDOW.blit(background, (0, 0))
        mainMap.draw()
        WINDOW.blit(mainMap, (mainMap_rect.x, mainMap_rect.y))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


def pause(mainMap: Container):
    global running
    pause = PauseMenu(SCREEN_SIZE)
    while running:
        dt = clock.tick(FPS)
        eventHandler()
        if key[pygame.K_ESCAPE]:
            key[pygame.K_ESCAPE] = False
            return
        for i in pause.eventHandling(key):
            if i == CONTINUE:
                return
            elif i == MAINMENU:
                menu()
            elif i == RESTART:
                playGame()
        mainMap_rect = mainMap.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        pause.draw()
        a = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        a.fill(pygame.Color(0, 0, 0, 60))
        WINDOW.blit(background, (0, 0))
        WINDOW.blit(mainMap, (mainMap_rect.x, mainMap_rect.y))
        WINDOW.blit(a, (0, 0))
        WINDOW.blit(pygame.transform.smoothscale(
            pygame.transform.smoothscale(WINDOW, (160, 90)), SCREEN_SIZE), (0, 0))
        WINDOW.blit(pause, (0, 0))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


def scoreBoard(mainMap: Container):
    board = ScoreBoard(SCREEN_SIZE, totalScore)
    threading.Thread(target=savingScore).start()
    while running:
        dt = clock.tick(FPS)
        eventHandler()
        if key[pygame.K_ESCAPE]:
            key[pygame.K_ESCAPE] = False
            menu()
        for i in board.eventHandling(key):
            if i == MAINMENU:
                menu()
            elif i == RESTART:
                playGame()
        mainMap_rect = mainMap.get_rect(
            center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
        board.draw()
        a = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
        a.fill(pygame.Color(0, 0, 0, 60))
        WINDOW.blit(background, (0, 0))
        WINDOW.blit(mainMap, (mainMap_rect.x, mainMap_rect.y))
        WINDOW.blit(pygame.transform.smoothscale(
            pygame.transform.smoothscale(WINDOW, (160, 90)), SCREEN_SIZE), (0, 0))
        WINDOW.blit(a, (0, 0))
        WINDOW.blit(board, (0, 0))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


def scoreHistory():
    page = ScoreHistory(SCREEN_SIZE, totalScore)
    while running:
        dt = clock.tick(FPS)
        eventHandler()
        if key[pygame.K_ESCAPE]:
            key[pygame.K_ESCAPE] = False
            menu()
        for i in page.eventHandling(key):
            if i == MAINMENU:
                menu()
        page.draw()
        WINDOW.blit(background, (0, 0))
        WINDOW.blit(page, (0, 0))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


def control():
    con = Control(SCREEN_SIZE)
    while running:
        dt = clock.tick(FPS)
        eventHandler()
        if key[pygame.K_ESCAPE]:
            key[pygame.K_ESCAPE] = False
            menu()
        for i in con.eventHandling(key):
            if i == MAINMENU:
                menu()
        con.draw()
        WINDOW.blit(background, (0, 0))
        WINDOW.blit(con, (0, 0))
        SCREEN.blit(pygame.transform.scale(
            WINDOW, (SCREEN.get_rect().width, SCREEN.get_rect().height)), (0, 0))
        pygame.display.update()


while running:
    menu()
    playGame()

pygame.quit()

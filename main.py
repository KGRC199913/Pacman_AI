import threading
import time

import wx
from math import *

from node import *
from algorithms import *
from constants import *


def read_map(map_name):
    maze_map = []
    map_file = open(map_name, "r", encoding='utf8')
    lines = map_file.readlines()
    map_file.close()
    del lines[0]
    x_pacman_pos, y_pacman_pos = [int(x)
                                  for x in lines[len(lines) - 1].split(" ")]
    del lines[-1]
    for line in lines:
        maze_map.append([int(x) for x in line.split(" ")])

    return maze_map, (x_pacman_pos, y_pacman_pos)


def createBitmap(path, cellSize):
    bitmap = wx.Bitmap(path)
    img = bitmap.ConvertToImage()
    img = img.Scale(cellSize, cellSize, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(img)


class Map:
    def __init__(self, maze_map):
        # Map related.
        self.map = maze_map
        self.mapWidth = len(maze_map[0])
        self.mapHeight = len(maze_map)
        self.cellSize = floor(WINDOW_WIDTH / self.mapWidth)
        if self.cellSize > floor(WINDOW_HEIGHT / self.mapHeight):
            self.cellSize = floor(WINDOW_HEIGHT / self.mapHeight)
        self.startDrawPos = floor((WINDOW_WIDTH - (self.mapWidth * self.cellSize)) / 2)
        # Icons related.
        self.diamonIcon = createBitmap(".\\test\\icons\\diamon.png", self.cellSize)
        self.pacman = []
        self.pacman.append(createBitmap(".\\test\\icons\\pacman1.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman2.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman3.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman4.png", self.cellSize))
        self.ghost = []
        self.ghost.append(createBitmap(".\\test\\icons\\ghost1.png", self.cellSize))
        self.ghost.append(createBitmap(".\\test\\icons\\ghost3.png", self.cellSize))

    def drawCell(self, clientDC, x_pos, y_pos):
        clientDC.DrawLine(self.startDrawPos + self.cellSize * y_pos, self.cellSize * x_pos,
                          self.startDrawPos + self.cellSize * y_pos + self.cellSize, self.cellSize * x_pos)

    def drawBitmap(self, clientDC, bitmap, x_pos, y_pos):
        clientDC.DrawBitmap(bitmap, self.startDrawPos + self.cellSize * y_pos, \
                            self.cellSize * x_pos - floor(self.cellSize / 2), True)


def changeDirection(old_position, current_position):
    if type(old_position) != type(current_position):
        return 0
    if old_position.position[1] == current_position.position[1]:
        if old_position.position[0] < current_position.position[0]:
            return 4
        else:
            return 2
    if old_position.position[0] == current_position.position[0]:
        if old_position.position[1] < current_position.position[1]:
            return 3
        else:
            return 1


class GameFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(GameFrame, self).__init__(*args, **kwargs)
        self.SetSize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.agent = None
        self.current_position = None
        self.maze_map = None
        self.monster_postion = None

    def paint(self, newDirection):
        dc = wx.ClientDC(self)
        dc.Clear()
        pen = wx.Pen("#4c4c4c", self.maze_map.cellSize)
        pen.SetCap(wx.CAP_BUTT)
        dc.SetPen(pen)
        # draw map here
        self.maze_map.drawBitmap(dc, self.maze_map.pacman[newDirection - 1], \
                                 self.current_position.position[0], self.current_position.position[1])
        for i in range(self.maze_map.mapHeight):
            for j in range(self.maze_map.mapWidth):
                if self.maze_map.map[i][j] == WALL:
                    self.maze_map.drawCell(dc, i, j)
                if self.maze_map.map[i][j] == FOOD:
                    self.maze_map.drawBitmap(dc, self.maze_map.diamonIcon, i, j)

        for monster in self.monster_postion:
            self.maze_map.drawBitmap(dc, self.maze_map.ghost[0], \
                                     monster.position[0], monster.position[1])

    def start(self):
        while not self.agent.is_finished():
            old_position = self.current_position
            self.current_position = self.agent.get_next_step()
            newDirection = changeDirection(old_position, self.current_position)
            self.paint(newDirection)
            time.sleep(time_interval)

    @staticmethod
    def find_monster(maze_map):
        if maze_map is None:
            return None
        monsters = []
        height = len(maze_map)
        width = len(maze_map[0])
        for i in range(height):
            for j in range(width):
                if maze_map[i][j] == MONSTER:
                    monsters.append(Monster(position=(i, j)))
                    maze_map[i][j] = 0
        return monsters


class Monster:
    def __init__(self, position):
        self.position = position
        self.obj_under = 0


if __name__ == '__main__':
    try:
        app = wx.App()
        map_matrix, start_position = read_map(".\\test\\maps\\demo01.txt")
        game_frame = GameFrame(None, title="Test")
        game_frame.maze_map = Map(map_matrix)
        game_frame.current_position = start_position
        monster_positions = GameFrame.find_monster(map_matrix)
        game_frame.agent = AStarAgent(map_matrix, start_position, monster_positions)
        game_frame.monster_postion = monster_positions
        game_frame.Show()
        thread = threading.Thread(target=game_frame.start)
        thread.start()
        app.MainLoop()
    except RuntimeError:
        pass

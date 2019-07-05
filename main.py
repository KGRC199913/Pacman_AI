import time
from random import randrange
from math import *

import wx
import numpy


#Constains
windowHeight = 600
windowWidth = 800


def read_map(map_name):
    map = []
    map_file = open(map_name, "r", encoding='utf8')
    lines = map_file.readlines()
    map_file.close()
    del lines[0]
    x_pacman_pos, y_pacman_pos = [int(x)
                                  for x in lines[len(lines) - 1].split(' ')]
    del lines[-1]
    for line in lines:
        map.append(list(line))
    return map, (x_pacman_pos, y_pacman_pos)


class AStarAgent:
    def __init__(self, maze_map, start_pos):
        self.map = maze_map
        self.path = self.__a_star(self.map)
        self.start_pos = start_pos
        self.stepCount = -1

    def get_next_step(self):
        self.stepCount += 1
        return self.path[self.stepCount]

    @staticmethod
    # a* search alg
    def __a_star(map):
        return []  # list of position

    @staticmethod
    def __manhattan_heuristic(from_pos, to_pos):
        return abs(from_pos[0] - to_pos[0])\
               + abs(from_pos[1] - to_pos[1])

    def is_finished(self):
        return self.stepCount == len(self.path) - 1


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = self.h = self.f = 0

    def __eq__(self, other):
        return self.position == other.position


def createBitmap(path, cellSize):
    bitmap = wx.Bitmap(path)
    img = bitmap.ConvertToImage()
    img = img.Scale(cellSize, cellSize, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(img)


class Map:
    def __init__(self, maze_map, clientDC):
        # Map related.
        self.map = maze_map
        self.mapWidth = len(maze_map[0])
        self.mapHeight = len(maze_map)
        self.cellSize = floor(windowWidth / self.mapWidth)
        if self.cellSize > floor(windowHeight / self.mapHeight):
            self.cellSize = floor(windowHeight / self.mapHeight)
        self.startDrawPos = floor((windowWidth - (self.mapWidth * self.cellSize)) / 2)
        # Pen related.
        self.pen = wx.Pen('#4c4c4c', self.cellSize)
        self.pen.SetCap(wx.CAP_BUTT)
        self.DC = clientDC
        self.DC.SetPen(self.pen)
        # Icons related.
        self.diamonIcon = createBitmap("diamon.png", self.cellSize)

    def drawCell(self, x_pos, y_pos):
        self.DC.DrawLine(self.startDrawPos + self.cellSize * y_pos, self.cellSize * x_pos,\
            self.startDrawPos + self.cellSize * y_pos + self.cellSize, self.cellSize * x_pos)

    def drawBitmap(self, bitmap, x_pos, y_pos):
        self.DC.DrawBitmap(bitmap, self.startDrawPos + self.cellSize * y_pos,\
            self.cellSize * x_pos - floor(self.cellSize / 2), True)



class GameFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(GameFrame, self).__init__(*args, **kwargs)
        self.SetSize(windowHeight, windowWidth)
        self.agent = None
        self.current_position = None

    def paint(self):
        dc = wx.ClientDC(self)
        dc.Clear()
        # draw map here
        maze_map = Map(self.agent.map, dc)

        for i in range (maze_map.mapHeight):
            for j in range(maze_map.mapWidth):
                if maze_map.map[i][j] == "1":
                    maze_map.drawCell(i, j)
                if maze_map.map[i][j] == "2":
                    maze_map.drawBitmap(maze_map.diamonIcon, i, j)

    def start(self):
        while not self.agent.is_finished():
            self.current_position = self.agent.get_next_step()
            self.paint()


if __name__ == '__main__':
    app = wx.App()
    maze_map, start_position = read_map(".\\test\\maps\\demo01.txt")
    game_frame = GameFrame(None, title="Test")
    game_frame.current_position = start_position
    game_frame.agent = AStarAgent(maze_map, start_position)
    game_frame.Show()
    app.MainLoop()

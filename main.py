import time
from random import randrange
from math import *

import wx
import numpy


#Constains
windowHeight = 600
windowWidth = 800


def read_map(map_name):
    maze_map = []
    map_file = open(map_name, "r", encoding='utf8')
    lines = map_file.readlines()
    map_file.close()
    del lines[0]
    x_pacman_pos, y_pacman_pos = [int(x)
                                  for x in lines[len(lines) - 1].split(' ')]
    del lines[-1]
    for line in lines:
        maze_map.append([int(x) for x in list(line.rstrip('\n'))])

    return maze_map, (x_pacman_pos, y_pacman_pos)


class AStarAgent:
    def __init__(self, maze_map, start_pos):
        self.map = maze_map

        start_node = Node(position=start_pos)
        end_node = Node(position=AStarAgent.__find_food(maze_map))

        self.path = self.__a_star(self.map, start_node, end_node)
        self.start_pos = start_pos
        self.stepCount = -1

    def get_next_step(self):
        self.stepCount += 1
        return self.path[self.stepCount]

    @staticmethod
    def __manhattan_heuristic(from_pos, to_pos):
        return abs(from_pos.position[0] - to_pos.position[0]) \
               + abs(from_pos.position[1] - to_pos.position[1])

    # find least f node for A*
    @staticmethod
    def __find_least_f(open_list):
        result = open_list[0]
        for a in open_list:
            if a.f < result.f:
                result = a
        return result

    @staticmethod
    # find least f node for A*
    def __generate_childs(maze_map, current_node):
        childs = []
        x = current_node.position[0]
        y = current_node.position[1]

        child = maze_map[x][y + 1]
        if (child == 0) or (child == 2):
            childs.append(Node(parent=current_node,
                               position=(x, y + 1)))

        child = maze_map[x][y - 1]
        if (child == 0) or (child == 2):
            childs.append(Node(parent=current_node,
                               position=(x, y - 1)))

        child = maze_map[x + 1][y]
        if (child == 0) or (child == 2):
            childs.append(Node(parent=current_node,
                               position=(x + 1, y)))

        child = maze_map[x - 1][y]
        if (child == 0) or (child == 2):
            childs.append(Node(parent=current_node,
                               position=(x - 1, y)))

        return childs

    @staticmethod
    def __find_food(maze_map):
        if maze_map is None:
            return None
        height = len(maze_map)
        width = len(maze_map[0])
        for i in range(height):
            for j in range(width):
                if maze_map[i][j] == 2:
                    return i, j
        return None

    @staticmethod
    # a* search alg
    def __a_star(maze_map, start_node, end_node):
        open_list = []
        closed_list = []
        path = []
        if start_node is not end_node:
            open_list.append(start_node)

        while len(open_list) > 0:
            current_node = AStarAgent.__find_least_f(open_list)
            closed_list.append(open_list.pop(open_list.index(current_node)))

            if current_node == end_node:
                while current_node is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                return path[::-1]

            childs = AStarAgent.__generate_childs(maze_map, current_node)

            for child in childs:
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = AStarAgent.__manhattan_heuristic(child, end_node)
                child.f = child.g + child.h

                if child in open_list:
                    if child.g > current_node.g:
                        continue
                open_list.append(child)

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
        self.diamonIcon = createBitmap(".\\test\\icons\\diamon.png", self.cellSize)

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
    maze_map, start_position = read_map(".\\test\\maps\\demo02.txt")
    game_frame = GameFrame(None, title="Test")
    game_frame.current_position = start_position
    game_frame.agent = AStarAgent(maze_map, start_position)
    game_frame.Show()
    game_frame.start()
    app.MainLoop()

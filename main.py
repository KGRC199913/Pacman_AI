import time
from random import randrange
from math import *

import wx
import numpy


#Constains
windowHeight = 600
windowWidth = 800
cellSize = 5


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

        start_node = Node(position=start_pos)
        end_node = AStarAgent.__find_food(maze_map)

        self.path = self.__a_star(self.map, start_node, end_node)
        self.start_pos = start_pos
        self.stepCount = -1

    def get_next_step(self):
        self.stepCount += 1
        return self.path[self.stepCount]

    @staticmethod
    def __manhattan_heuristic(from_pos, to_pos):
        return abs(from_pos[0] - to_pos[0]) \
               + abs(from_pos[1] - to_pos[1])

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

        if maze_map[current_node.position[0] + 1][current_node.position[1] + 1] == 0:
            childs.pop(current_node.position[0] + 1)
            childs.pop(current_node.position[1] + 1)

        if maze_map[current_node.position[0] + 1][current_node.position[1] - 1] == 0:
            childs.pop(current_node.position[0] + 1)
            childs.pop(current_node.position[1] - 1)

        if maze_map[current_node.position[0] - 1][current_node.position[1] + 1] == 0:
            childs.pop(current_node.position[0] - 1)
            childs.pop(current_node.position[1] + 1)

        if maze_map[current_node.position[0] - 1][current_node.position[1] - 1] == 0:
            childs.pop(current_node.position[0] - 1)
            childs.pop(current_node.position[1] - 1)

        for child in childs:
            child.parent = current_node

        return childs

    @staticmethod
    def __find_food(maze_map):
        for pos in maze_map:
            if pos == 2:
                return Node(position=pos)

    @staticmethod
    # a* search alg
    def __a_star(maze_map, start_node, end_node):
        open_list = []
        closed_list = []
        result_list = []
        if start_node is not end_node:
            open_list.append(start_node)

        while len(open_list) > 0:
            current_node = AStarAgent.__find_least_f(open_list)
            closed_list.append(open_list.pop(open_list.index(current_node)))

            if current_node == end_node:
                while current_node is not start_node:
                    result_list.append(current_node)
                    current_node = current_node.parent
                result_list.append(start_node)
                return result_list

            childs = AStarAgent.__generate_childs(maze_map, current_node)

            for child in childs:
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = AStarAgent.__manhattan_heuristic(child,end_node)
                child.f = child.g + child.h

                if child in open_list:
                    if child.g > current_node.g:
                        continue
                open_list.append(child)

        return result_list

    def is_finished(self):
        return self.stepCount == len(self.path) - 1


class Node:
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = self.h = self.f = 0

    def __eq__(self, other):
        return self.position == other.position


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
        maze_map = self.agent.map
        mapWidth = len(maze_map[0])
        mapHeight = len(maze_map)

        if windowWidth / mapWidth <= windowHeight / mapHeight:
            cellSize = floor(windowWidth / mapWidth)
        else:
            cellSize = floor(windowHeight / mapHeight)

        startDrawPos = floor((windowWidth - (mapWidth * cellSize)) / 2)

        pen = wx.Pen('#4c4c4c', cellSize)
        pen.SetCap(wx.CAP_BUTT)
        dc.SetPen(pen)

        for i in range (mapHeight):
            for j in range(mapWidth):
                if maze_map[i][j] == "1":
                    dc.DrawLine(startDrawPos + cellSize * j, cellSize * i, \
                        startDrawPos + cellSize * j + cellSize, cellSize * i)

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

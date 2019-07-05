import threading
import time

import wx
from math import *

# Constains
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
WALL = 1
FOOD = 2
MONSTER = 3
time_interval = 0.2

# Global variables
MAZE_MAP = None


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
        maze_map.append([int(x) for x in line.split(' ')])

    return maze_map, (x_pacman_pos, y_pacman_pos)


class AStarAgent:
    def __init__(self, maze_map, start_pos, monsters_list):
        self.map = maze_map
        self.monsters = None
        if not monsters_list:
            self.monsters = []
        else:
            self.monsters = monsters_list
        start_node = Node(position=start_pos)
        end_node = Node(position=AStarAgent.__find_food(maze_map))

        self.path = self.__a_star(self.map, start_node, end_node, self.monsters)
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
    def __generate_childs(maze_map, monsters, current_node):
        childs = []
        x = current_node.position[0]
        y = current_node.position[1]
        monster_positions = [monster.position for monster in monsters]

        child = maze_map[x][y + 1]
        if ((child == 0) or (child == 2)) and ((x, y + 1) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y + 1)))

        child = maze_map[x][y - 1]
        if ((child == 0) or (child == 2)) and ((x, y - 1) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y - 1)))

        child = maze_map[x + 1][y]
        if ((child == 0) or (child == 2)) and ((x + 1, y) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x + 1, y)))

        child = maze_map[x - 1][y]
        if ((child == 0) or (child == 2)) and ((x - 1, y) not in monster_positions):
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
                if maze_map[i][j] == FOOD:
                    return i, j
        return None

    @staticmethod
    # a* search alg
    def __a_star(maze_map, start_node, end_node, monster_positions):
        open_list = []
        closed_list = []
        path = []
        if monster_positions is None:
            monster_positions = []

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

            childs = AStarAgent.__generate_childs(maze_map, monster_positions, current_node)

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
        clientDC.DrawLine(self.startDrawPos + self.cellSize * y_pos, self.cellSize * x_pos, \
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
        self.maze_map.drawBitmap(dc, self.maze_map.pacman[newDirection - 1],\
            self.current_position.position[0], self.current_position.position[1])
        for i in range(self.maze_map.mapHeight):
            for j in range(self.maze_map.mapWidth):
                if self.maze_map.map[i][j] == WALL:
                    self.maze_map.drawCell(dc, i, j)
                if self.maze_map.map[i][j] == FOOD:
                    self.maze_map.drawBitmap(dc, self.maze_map.diamonIcon, i, j)

        for monster in self.monster_postion:
            self.maze_map.drawBitmap(dc, self.maze_map.ghost[0],\
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
        map_matrix, start_position = read_map(".\\test\\maps\\demo02.txt")
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

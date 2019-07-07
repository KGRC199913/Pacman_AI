import threading
import time
from math import *
from random import randrange, random

import wx

# Constants
WINDOW_HEIGHT = 600
WINDOW_WIDTH = 800
MENU_HEIGHT = 450
MENU_WIDTH = 300
BUTTON_HEIGHT = 25
BUTTON_WIDTH = 100
BUTTON_PADDING = 5
WALL = 1
FOOD = 2
MONSTER = 3
time_interval = 0.2


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


class HillClimbing:
    def __init__(self, maze_map, start_pos, monsters_list):
        self.map = maze_map
        self.monsters = None
        if not monsters_list:
            self.monsters = []
        else:
            self.monsters = monsters_list

        self.start_node = Node(position=start_pos)
        self.end_node = None

    def get_next_step(self):

        scans = HillClimbing.__pacman_scan(self.map, self.start_node)
        min_distance = HillClimbing.__calc_distance(self.start_node, scans[0])

        temp = None
        for i in range(len(scans)):
            if HillClimbing.__calc_distance(self.start_node, scans[i]) < min_distance and scans[i] == FOOD:
                min_distance = HillClimbing.__calc_distance(self.start_node, scans[i])
                temp = scans[i]
        if self.end_node is None and temp is not None:
            self.end_node = temp
        if self.end_node is None and temp is None:
            while self.end_node is None \
                    or self.map[self.end_node.position[0]][self.end_node.position[1]] == WALL:
                rd = HillClimbing.random_pos(self.start_node)
                self.end_node = rd

        path = HillClimbing.__a_star(self.map, self.start_node, self.end_node, self.monsters)
        if self.map[path[1].position[0]][path[1].position[1]] == FOOD:
            self.end_node = None
        self.start_node = path[1]
        return path[1]

    @staticmethod
    def random_pos(node):
        pos = None
        rd_xy = randrange(0, 1)
        rd_1 = randrange(-1, 1)
        if rd_1 != 0:
            rd_2 = 0
        else:
            rd_2 = randrange(-1, 1)
        if rd_xy == 0:
            pos = (node.position[0] + rd_1, node.position[1] + rd_2)
        else:
            pos = (node.position[0] + rd_2, node.position[1] + rd_1)
        return Node(position=pos)

    def is_finished(self):
        food = FOOD
        is_finished = True
        for line in self.map:
            if food in line:
                is_finished = False
        return is_finished

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
        if ((child == 0) or (child == 2)) and (child not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y + 1)))

        child = maze_map[x][y - 1]
        if ((child == 0) or (child == 2)) and (child not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y - 1)))

        child = maze_map[x + 1][y]
        if ((child == 0) or (child == 2)) and (child not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x + 1, y)))

        child = maze_map[x - 1][y]
        if ((child == 0) or (child == 2)) and (child not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x - 1, y)))
        return childs

    @staticmethod
    def __pacman_scan(maze_map, current_node):
        scans = []
        x = current_node.position[0]
        y = current_node.position[1]

        scans.append(Node(position=(x - 1, y)))
        scans.append(Node(position=(x - 2, y)))
        scans.append(Node(position=(x - 3, y)))
        scans.append(Node(position=(x + 1, y)))
        scans.append(Node(position=(x + 2, y)))
        scans.append(Node(position=(x + 3, y)))
        scans.append(Node(position=(x, y - 1)))
        scans.append(Node(position=(x, y - 2)))
        scans.append(Node(position=(x, y - 3)))
        scans.append(Node(position=(x, y + 1)))
        scans.append(Node(position=(x, y + 2)))
        scans.append(Node(position=(x, y + 3)))
        scans.append(Node(position=(x + 1, y + 1)))
        scans.append(Node(position=(x - 1, y - 1)))
        scans.append(Node(position=(x - 1, y + 1)))
        scans.append(Node(position=(x + 1, y - 1)))
        scans.append(Node(position=(x - 1, y + 2)))
        scans.append(Node(position=(x - 2, y + 1)))
        scans.append(Node(position=(x + 1, y - 2)))
        scans.append(Node(position=(x + 2, y - 1)))
        scans.append(Node(position=(x + 1, y + 2)))
        scans.append(Node(position=(x + 2, y + 1)))
        scans.append(Node(position=(x - 1, y - 2)))
        scans.append(Node(position=(x - 2, y - 1)))

        return scans

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
            current_node = HillClimbing.__find_least_f(open_list)
            closed_list.append(open_list.pop(open_list.index(current_node)))

            if current_node == end_node:
                while current_node is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                return path[::-1]

            childs = HillClimbing.__generate_childs(maze_map, monster_positions, current_node)

            for child in childs:
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = HillClimbing.__manhattan_heuristic(child, end_node)
                child.f = child.g + child.h

                if child in open_list:
                    if child.g > current_node.g:
                        continue
                open_list.append(child)

    @staticmethod
    def __calc_distance(currend_node, end_node):
        return sqrt(
            (currend_node.position[0] - end_node.position[0]) * (currend_node.position[0] - end_node.position[0]) \
            + (currend_node.position[1] - end_node.position[1]) * (currend_node.position[1] - end_node.position[1]))


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
        if self.path is None:
            return Node(position=self.start_pos)
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

                for node in open_list:
                    if child == node and child.g > current_node.g:
                        continue
                open_list.append(child)

    def is_finished(self):
        if self.path is None:
            return True
        return self.stepCount == len(self.path) - 1


class AStarGhostAgent:
    def __init__(self, maze_map):
        self.map = maze_map

        self.start_node = None
        self.end_node = None

    def get_next_step(self):
        path = self.__a_star(self.map, self.start_node, self.end_node)
        if path is None:
            return self.start_node
        if len(path) > 1:
            self.start_node = path[1]
            return path[1].position
        return path[0].position

    @staticmethod
    def __euclidean_heuristic(from_pos, to_pos):
        x = abs(from_pos.position[0] - to_pos.position[0])
        y = abs(from_pos.position[1] - to_pos.position[1])

        distance: float = sqrt((x * x) + (y * y))
        return distance

    # find least f node for A*
    @staticmethod
    def __find_least_f(open_list):
        result = open_list[0]
        for a in open_list:
            if a.f < result.f:
                result = a
        return result

    @staticmethod
    def __generate_childs(maze_map, current_node):
        childs = []
        x = current_node.position[0]
        y = current_node.position[1]

        child = maze_map[x][y + 1]
        if (child is not WALL) or (child is FOOD):
            childs.append(Node(parent=current_node,
                               position=(x, y + 1)))

        child = maze_map[x][y - 1]
        if (child is not WALL) or (child is FOOD):
            childs.append(Node(parent=current_node,
                               position=(x, y - 1)))

        child = maze_map[x + 1][y]
        if (child is not WALL) or (child is FOOD):
            childs.append(Node(parent=current_node,
                               position=(x + 1, y)))

        child = maze_map[x - 1][y]
        if (child is not WALL) or (child is FOOD):
            childs.append(Node(parent=current_node,
                               position=(x - 1, y)))
        return childs

    @staticmethod
    # a* search alg
    def __a_star(maze_map, start_node, end_node):
        open_list = []
        closed_list = []
        path = []

        if start_node is not end_node:
            open_list.append(start_node)

        while len(open_list) > 0:
            current_node = AStarGhostAgent.__find_least_f(open_list)
            closed_list.append(open_list.pop(open_list.index(current_node)))

            if current_node == end_node:
                while current_node is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                return path[::-1]

            childs = AStarGhostAgent.__generate_childs(maze_map, current_node)

            for child in childs:
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = AStarGhostAgent.__euclidean_heuristic(child, end_node)
                child.f = child.g + child.h

                for node in open_list:
                    if child == node and child.g > current_node.g:
                        continue
                open_list.append(child)


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
        self.startDrawPos = None
        self.cellSize = floor(WINDOW_WIDTH / self.mapWidth)
        self.startDrawPos = Node(parent=None,
                                 position=(0, floor((WINDOW_HEIGHT - (self.mapHeight * self.cellSize)) / 2)))
        if self.cellSize > floor(WINDOW_HEIGHT / self.mapHeight):
            self.cellSize = floor(WINDOW_HEIGHT / self.mapHeight)
            self.startDrawPos = Node(parent=None,
                                     position=(floor((WINDOW_WIDTH - (self.mapWidth * self.cellSize)) / 2), 0))
        # Pen related.
        self.penWall = wx.Pen("#4c4c4c", self.cellSize)
        self.penWall.SetCap(wx.CAP_BUTT)
        self.penPath = wx.Pen("#ababab", self.cellSize)
        self.penPath.SetCap(wx.CAP_BUTT)
        # Icons related.
        self.diamonIcon = createBitmap(".\\test\\icons\\diamon.png", self.cellSize)
        self.pacman = []
        self.pacman.append(createBitmap(".\\test\\icons\\pacman1.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman2.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman3.png", self.cellSize))
        self.pacman.append(createBitmap(".\\test\\icons\\pacman4.png", self.cellSize))
        self.ghost = []
        self.ghost.append(createBitmap(".\\test\\icons\\ghost1.png", self.cellSize))
        self.ghost.append(createBitmap(".\\test\\icons\\ghost1.png", self.cellSize))
        self.ghost.append(createBitmap(".\\test\\icons\\ghost3.png", self.cellSize))
        self.ghost.append(createBitmap(".\\test\\icons\\ghost3.png", self.cellSize))

    def drawCell(self, clientDC, x_pos, y_pos):
        clientDC.DrawLine(self.startDrawPos.position[0] + self.cellSize * y_pos,
                          self.startDrawPos.position[1] + self.cellSize * x_pos, \
                          self.startDrawPos.position[0] + self.cellSize * y_pos + self.cellSize,
                          self.startDrawPos.position[1] + self.cellSize * x_pos)

    def drawBitmap(self, clientDC, bitmap, x_pos, y_pos):
        clientDC.DrawBitmap(bitmap, self.startDrawPos.position[0] + self.cellSize * y_pos, \
                            self.startDrawPos.position[1] + self.cellSize * x_pos - floor(self.cellSize / 2), True)


def changeDirection(old_position, current_position):
    if type(old_position) is tuple:
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
        self.old_position = None
        self.current_position = None
        self.maze_map = None
        self.monster_positions = None
        self.monster_agent = None
        self.score = 1
        self.status_bar = self.CreateStatusBar()

    def paint(self, newDirection):
        dc = wx.ClientDC(self)
        # draw map here
        for i in range(self.maze_map.mapHeight):
            for j in range(self.maze_map.mapWidth):
                if self.maze_map.map[i][j] == WALL:
                    dc.SetPen(self.maze_map.penWall)
                    self.maze_map.drawCell(dc, i, j)
                if self.maze_map.map[i][j] == FOOD:
                    if self.current_position.position[0] == i and self.current_position.position[1] == j:
                        dc.SetPen(self.maze_map.penPath)
                        self.maze_map.drawCell(dc, i, j)
                        self.score += 20
                        continue
                    self.maze_map.drawBitmap(dc, self.maze_map.diamonIcon, i, j)
                    self.score -= 1

        if type(self.old_position) == type(self.current_position):
            dc.SetPen(self.maze_map.penPath)
            self.maze_map.drawCell(dc, self.old_position.position[0], self.old_position.position[1])

        self.maze_map.drawBitmap(dc, self.maze_map.pacman[newDirection - 1], \
                                 self.current_position.position[0], self.current_position.position[1])

        for monster in self.monster_positions:
            if type(monster.old_position) is not tuple or \
                    type(monster.old_position) is not None:
                dc.SetPen(self.maze_map.penPath)
                self.maze_map.drawCell(dc, monster.old_position[0], monster.old_position[1])
            monster_direction = changeDirection(Node(position=(monster.old_position[0], monster.old_position[1])), \
                                                Node(position=(monster.position[0], monster.position[1])))
            self.maze_map.drawBitmap(dc, self.maze_map.ghost[monster_direction - 1],
                                     monster.position[0], monster.position[1])

    def isHit(self, pacman_pos, monster_pos):
        if type(pacman_pos) is Node and type(monster_pos) is Node and pacman_pos == monster_pos:
            return True
        return False

    def start(self):
        while True:
            # Update agent postion.
            self.old_position = self.current_position
            self.current_position = self.agent.get_next_step()
            # Update each monster agent position.
            for position_index, monster_position in enumerate(self.monster_positions):
                if type(self.monster_agent[position_index]) is AStarGhostAgent:
                    self.monster_agent[position_index].start_node = \
                        Node(position=self.monster_positions[position_index].position)
                    self.monster_agent[position_index].end_node = self.current_position
                # Update position.
                self.monster_positions[position_index].old_position = \
                    self.monster_positions[position_index].position
                self.monster_positions[position_index].position = \
                    self.monster_agent[position_index].get_next_step()
                # Check colission.

                if self.isHit(self.old_position, self.monster_positions[position_index].old_position):
                    return None

            # Change agent's direction.
            newDirection = changeDirection(self.old_position, self.current_position)
            # Update graphics.
            self.paint(newDirection)
            self.SetStatusText("Score: {}".format(self.score))

            if self.agent.is_finished():
                break
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
        self.old_position = None
        self.position = position
        self.direction = None
        self.obj_under = 0


class StandStillAgent:
    def __init__(self, maze_map):
        self.start_position = None

    def get_next_step(self):
        return self.start_position


class RandomAroundInitialAgent:
    def __init__(self, maze_map):
        self.maze_map = maze_map
        self.start_position = None
        self.current_position = None

    def get_next_step(self):
        if self.current_position != self.start_position:
            self.current_position = self.start_position
        else:
            random_number = randrange(0, 3, 1)
            coor = None
            if random_number == 0:
                coor = (self.start_position[0] + 1, self.start_position[1])
                if self.maze_map[coor[0]][coor[1]] != 1:
                    self.current_position = coor

            if random_number == 1:
                coor = (self.start_position[0] - 1, self.start_position[1])
                if self.maze_map[coor[0]][coor[1]] != 1:
                    self.current_position = coor

            if random_number == 2:
                coor = (self.start_position[0], self.start_position[1] + 1)
                if self.maze_map[coor[0]][coor[1]] != 1:
                    self.current_position = coor

            if random_number == 3:
                coor = (self.start_position[0], self.start_position[1] - 1)
                if self.maze_map[coor[0]][coor[1]] != 1:
                    self.current_position = coor

        return self.current_position


def StartGame(level = 0):
    try:
        if level == 0:
            return None
        map_matrix, start_position = read_map(".\\test\\maps\\demo06.txt")
        game_frame = GameFrame(None, title="Test", style=wx.DEFAULT_FRAME_STYLE ^\
            wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        game_frame.maze_map = Map(map_matrix)
        game_frame.current_position = start_position
        monster_positions = GameFrame.find_monster(map_matrix)
        # game_frame.agent = AStarAgent(map_matrix, start_position, monster_positions)
        game_frame.agent = HillClimbing(map_matrix, start_position, monster_positions)
        game_frame.monster_positions = monster_positions
        monster_agents = []
        if level == 1 or level == 2:
            for i in range(len(monster_positions)):
                agent = StandStillAgent(maze_map=map_matrix)
                agent.start_position = monster_positions[i].position
                monster_agents.append(agent)

        if level == 3:
            for i in range(len(monster_positions)):
                agent = RandomAroundInitialAgent(maze_map=map_matrix)
                agent.start_position = monster_positions[i].position
                agent.current_position = copy.deepcopy(agent.start_position)
                monster_agents.append(agent)

        if level == 4:
            for i in range(len(monster_positions)):
                agent = AStarGhostAgent(maze_map=map_matrix)
                agent.start_position = monster_positions[i].position
                monster_agents.append(agent)

        game_frame.monster_agent = monster_agents
        game_frame.Show()
        thread = threading.Thread(target=game_frame.start)
        thread.start()
    except RuntimeError:
        pass


class MenuFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MenuFrame, self).__init__(*args, **kwargs)
        self.SetSize(MENU_WIDTH, MENU_HEIGHT)
        self.Show()
        self.level = None

        dc = wx.ClientDC(self)

        bitmap = wx.Bitmap(".\\test\\icons\\logo.png")
        img = bitmap.ConvertToImage()
        img = img.Scale(280, 73, wx.IMAGE_QUALITY_HIGH)
        bitmap = wx.Bitmap(img)

        dc.DrawBitmap(bitmap, 0, 40, True)

        self.button = []

        for i in range(5):
            self.button.append(wx.Button(self, label = 'Press {}'.format(i),\
                size = (BUTTON_WIDTH, BUTTON_HEIGHT),\
                pos = (100, 150 + (BUTTON_HEIGHT + BUTTON_PADDING) * i)))
            self.button[i].myname = "{}".format(i)
            self.Bind(wx.EVT_BUTTON, self.on_press, self.button[i])

    def on_press(self, event):
        self.level = int(event.GetEventObject().myname)
        self.Close()
        StartGame(self.level)


if __name__ == '__main__':
    try:
        app = wx.App()
        menuframe = MenuFrame(None, title = "Pacman AI",\
            style = wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER ^ wx.MAXIMIZE_BOX)
        app.MainLoop()
    except RuntimeError:
        pass

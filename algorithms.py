# Algorithms.

from Node import *
from Constants import *


# A-Star
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

                for node in open_list:
                    if child == node and child.g > current_node.g:
                        continue
                open_list.append(child)

    def is_finished(self):
        return self.stepCount == len(self.path) - 1

from main import *


class AStarFlexPacmanAgent:
    def __init__(self, maze_map, start_pos, monsters_list):

        self.map = maze_map

        self.start_node = None
        self.end_node = None

        self.monsters = monsters_list
        self.start_node = Node(position=start_pos)
        self.end_node = AStarFlexPacmanAgent.__choose_food(self.start_node, maze_map)
        # self.path = self.__a_star(maze_map, self.start_node, self.end_node, self.monsters)

    def get_next_step(self):
        path = self.__a_star(self.map, self.start_node, AStarFlexPacmanAgent.__choose_food(self.start_node, self.map), self.monsters)
        if path is None:
            self.end_node = None
            return self.start_node.position
        self.start_node = path[1]
        self.start_node.parent = None
        return path[1]

    @staticmethod
    def __choose_food(start_node, maze_map):
        foods = AStarFlexPacmanAgent.__find_foods(maze_map)
        result = foods[0]
        for food in foods:
            if AStarFlexPacmanAgent.__manhattan_heuristic(start_node, food) \
                    < AStarFlexPacmanAgent.__manhattan_heuristic(start_node, result):
                result = food
        return result

    @staticmethod
    def __find_foods(maze_map):
        foods = []
        if maze_map is None:
            return None
        height = len(maze_map)
        width = len(maze_map[0])
        for i in range(height):
            for j in range(width):
                if maze_map[i][j] == FOOD:
                    foods.append(Node(position=(i, j)))
        return foods

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
    def __generate_childs(maze_map, monsters, current_node):
        childs = []
        x = current_node.position[0]
        y = current_node.position[1]
        monster_positions = [monster.position for monster in monsters]

        child = maze_map[x][y + 1]
        if ((child is not WALL) or (child is FOOD)) and ((x, y + 1) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y + 1)))

        child = maze_map[x][y - 1]
        if ((child is not WALL) or (child is FOOD)) and ((x, y - 1) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x, y - 1)))

        child = maze_map[x + 1][y]
        if ((child is not WALL) or (child is FOOD)) and ((x + 1, y) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x + 1, y)))

        child = maze_map[x - 1][y]
        if ((child is not WALL) or (child is FOOD)) and ((x - 1, y) not in monster_positions):
            childs.append(Node(parent=current_node,
                               position=(x - 1, y)))
        return childs

    @staticmethod
    # a* search alg
    def __a_star(maze_map, start_node, end_node, monsters):
        open_list = []
        closed_list = []
        path = []

        if start_node is not end_node:
            open_list.append(start_node)

        while len(open_list) > 0:
            current_node = AStarFlexPacmanAgent.__find_least_f(open_list)
            closed_list.append(open_list.pop(open_list.index(current_node)))

            if current_node == end_node:
                while current_node is not None:
                    path.append(current_node)
                    current_node = current_node.parent
                return path[::-1]

            childs = AStarFlexPacmanAgent.__generate_childs(maze_map, monsters, current_node)

            for child in childs:
                if child in closed_list:
                    continue
                child.g = current_node.g + 1
                child.h = AStarFlexPacmanAgent.__manhattan_heuristic(child, end_node)
                child.f = child.g + child.h

                for node in open_list:
                    if child == node and child.g > current_node.g:
                        continue
                open_list.append(child)

    # For Testing Purporse
    def is_finished(self):
        if self.__choose_food(self.start_node, self.map) is None:
            return True
        return False

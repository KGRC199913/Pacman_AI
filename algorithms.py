from main import *


class AStarFlexPacmanAgent:
    def __init__(self, maze_map, start_pos, monsters_list):

        self.map = maze_map

        self.start_node = None
        self.end_node = None

        self.monsters = monsters_list
        self.start_node = Node(position=start_pos)
        self.end_node = AStarFlexPacmanAgent.__choose_food(self.start_node, self.map, self.monsters)
        # self.path = self.__a_star(maze_map, self.start_node, self.end_node, self.monsters)

    def get_next_step(self):
        if self.start_node == self.end_node:
            self.map = self.__update_map_and_food(self.start_node, self.map, self.monsters, True)
        path = self.__a_star(self.map, self.start_node,
                             AStarFlexPacmanAgent.__choose_food(self.start_node, self.map, self.monsters),
                             self.monsters)
        #if path is None:
        #    # self.end_node = None
        #    path = self.__a_star(self.map, self.start_node,
        #                         AStarFlexPacmanAgent.__choose_food(self.start_node, self.map, self.monsters),
        #                         self.monsters)
        #    self.start_node = path[1]
        #    self.start_node.parent = None
        #    self.map = self.__update_map_and_food(self.start_node, self.map, self.monsters)
        #    return path[1]
        self.start_node = path[1]
        self.start_node.parent = None
        self.map = self.__update_map_and_food(self.start_node, self.map, self.monsters)
        return path[1]

    @staticmethod
    def __update_map_and_food(current_node, maze_map, monsters, is_feeded=False):
        new_map = maze_map
        x = current_node.position[0]
        y = current_node.position[1]
        if maze_map[x][y] == FOOD:
            new_map[x][y] = WALL - 1  # Road

        height = len(maze_map)
        width = len(maze_map[0])
        monster_position = [monster.position for monster in monsters]
        for i in range(height):
            for j in range(width):
                if (maze_map[i][j] == MONSTER) and ((i, j) not in monster_position):
                    new_map[i][j] = 0
        if is_feeded:
            new_map[x][y] = 0
        return new_map

    @staticmethod
    def __choose_food(start_node, maze_map, monsters):
        foods = AStarFlexPacmanAgent.__find_foods(maze_map)

        if foods is None:
            return None
        monsters_position = [monster.position for monster in monsters]
        result = foods[0]
        # for food in foods:
        #    if (food.position[0], food.position[1]) not in monsters_position:
        #        result = food
        #        break

        # monsters_position = [monster.position for monster in monsters]
        # while (result.position[0], result.position[1]) not in monsters_position:
        #    result = foods[foods.index(result) + 1]
        for food in foods:
            if AStarFlexPacmanAgent.__manhattan_heuristic(start_node, food) \
                    < AStarFlexPacmanAgent.__manhattan_heuristic(start_node, result):
                for monster in monsters:
                    if food.position is not monster.position:
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
        if start_node is end_node:
            path = None
            return path

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
        if self.__choose_food(self.start_node, self.map, self.monsters) is None:
            return True
        if self.start_node in self.monsters:
            return True
        self.map = self.__update_map_and_food(self.start_node, self.map, self.monsters, False)
        if self.__a_star(self.map, self.start_node,
                         AStarFlexPacmanAgent.__choose_food(self.start_node, self.map, self.monsters),
                         self.monsters) is None:

            return True
        return False

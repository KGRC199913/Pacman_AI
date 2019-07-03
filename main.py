import wx
import numpy


def readMap(mapname):
    map_file = open(mapname, "r", encoding='utf8')
    # meow viet doc file o day :3
    # Read 2 number as size of map N x M.
    lines = map_file.readlines()
    map_file.close()
    map_matrix = list()
    if lines:
        map_height, map_width = map(int(lines[0].split()))
        map_matrix.extend(list(lines))
        map_matrix.remove(map_matrix[0])
        map_matrix.remove(map_matrix[len(map_matrix) - 1])
    return map_matrix


class AStarAgent:
    def __init__(self, map):
        self.map = map
        self.path = self.__a_star(self.map)
        self.stepCount = -1

    def get_next_step(self):
        self.stepCount += 1
        return self.path[self.stepCount]

    @staticmethod
    def __a_star(map):
        return []


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
        self.SetSize(800, 600)
        self.panel = DrawPanel(self)
        self.panel.Bind(wx.EVT_PAINT, self.onPaint)

    def onPaint(self, event):
        drawer = wx.PaintDC(self.panel)
        drawer.DrawLine(0, 10, 10, 10)


class DrawPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        super(DrawPanel, self).__init__(*args, **kwargs)


if __name__ == '__main__':
    app = wx.App()
    game_frame = GameFrame(None, title="Test")
    game_frame.Show()

    app.MainLoop()

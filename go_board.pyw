from tkinter import *
import time

class Board(Frame):

    def __init__(self, master=None):
        super().__init__(master)
        self.colors = ['white', 'black', 'blue']
        self.turn = False
        self.records = [[] for i in self.colors]
        self.grid = [[None]*20]*20
        self.pack()
        self.create_widgets()

    def px2cm(self, pxs=0):
        ratio = self.winfo_fpixels( '1c' )
        return pxs / ratio

    def cm2px(self, cms=0):
        ratio = self.winfo_fpixels( '1c' )
        return cms * ratio

    def snap2grid(self, v=0):
        v = self.px2cm(v)
        if v < 1: v = 1
        elif v > 19: v = 19
        return int(self.cm2px(round(v)))

    def create_widgets(self):
        self.canvas = Canvas(self, height='20c', width='20c')
        self.draw_grid()
        self.canvas.bind('<Button-1>', self.__play)
        self.canvas.pack()

    def draw_stone(self, x, y, R, *args, **kargs):
        R = self.cm2px(R)
        x, y = self.snap2grid(x), self.snap2grid(y)
        x0, y0 = x - R, y - R
        x1, y1 = x + R, y + R
        stone = self.canvas.create_oval(x0, y0, x1, y1, *args, **kargs)
        return x, y, stone

    def play(self, x, y, turn=False, R=0.5):
        color = self.colors[turn]
        x, y, stone = self.draw_stone(x, y, R, fill=color, tags=str(turn))
        self.records[turn].append(stone)
        pos_x, pos_y = int(self.px2cm(x)), int(self.px2cm(y))
        self.grid[pos_x][pos_y] = stone
        self.kill_surrounded(not turn, (x, y))

    def adjacents(self, x, y):
        stones = []
        for i, j, c in [(1, 0, 'green'), (0, 1, 'blue'),
                        (-1, 0, 'red'), (0, -1, 'yellow')]:
            new_x, new_y = x + self.cm2px(i), y + self.cm2px(j)
            new_x, new_y = self.snap2grid(new_x), self.snap2grid(new_y)
            stones.append((new_x, new_y))
        return stones

    def draw_grid(self):
        start, stop, step = 1, 19, 1
        for i in range(start, stop+1, step):
            x0 = str(start) + 'c'
            y0 = str(i) + 'c'
            x1 = str(stop) + 'c'
            y1 = str(i) + 'c'
            self.canvas.create_line(x0, y0, x1, y1)
            self.canvas.create_line(y0, x0, y1, x1)

    def kill_surrounded(self, turn, near):
        groups = self.groups(turn, near)
        for group in groups:
            if not self.isfree(group):
                for x, y in group:
                    self.canvas.delete(self.grid[x][y])

    def group(self, turn, near, done=[]):
        x, y = near
        adjacents = self.adjacents(x, y)
        right_turn = self.records[turn]
        right_turn = [self.canvas.coords(i) for i in right_turn]
        right_turn = [(int((a+c)/2), int((b+d)/2)) for a, b, c, d in
                      right_turn]
        suspects = set(done)
        for x, y in adjacents:
            if (x, y) in right_turn and (x, y) not in suspects:
                suspects.add((x, y))
                suspects = self.group(turn, (x, y), suspects)
        return suspects

    def groups(self, turn, near):
        self.group(turn, near)
        return []

    def degrees(self, group):
        border = set()
        for stone in group:
            for side in self.adjacents(*stone):
                if side not in group:
                    border.add(side)
        return border

    def isfree(self, group):
        degrees = self.degrees(group)
        N = len(degrees)
        for x, y in degrees:
            pos_x, pos_y = int(self.px2cm(x)), int(self.px2cm(y))
            if self.grid[pos_x][pos_y]: N -= 1
        return N

    def __play(self, event):
        x, y = event.x, event.y
        self.play(x, y, self.turn)
        self.turn = not self.turn

def main():
    root = Tk()
    board = Board(root)
    board.mainloop()

if __name__ == '__main__':
    main()

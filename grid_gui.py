import sys
import tkinter
import grid


# Grid és user közötti interakciók kezelése
class GridCanvas(tkinter.Canvas):
    def __init__(self, master, grid_map, start_and_goal):
        self.rows, self.columns = len(grid_map), len(grid_map[0])
        self.square_size = min(40, 500 / self.rows, 500 / self.columns)
        tkinter.Canvas.__init__(self, master,
                                height=self.square_size * self.rows + 1,
                                width=self.square_size * self.columns + 1, background="white")
        self.grid_map = grid_map
        self.start_and_goal = start_and_goal
        self.draw_grid(grid_map)
        self.bind("<Button-1>", self.left_click)
        self.bind("<Button-2>", self.right_click)
        self.bind("<Button-3>", self.right_click)
        self.focus_set()
        self.configure(highlightthickness=0)

    # Input txt alapján megrajzolja a teret
    def draw_grid(self, grid_map):
        for row in range(len(grid_map)):
            for col in range(len(grid_map[0])):
                x0, y0 = col * self.square_size, row * self.square_size
                x1, y1 = x0 + self.square_size, y0 + self.square_size
                color = "black" if grid_map[row][col] else "white"
                self.create_rectangle(x0, y0, x1, y1, width=1, outline="black", fill=color)

    # Bal egérgombra beállítja kezdőpontot
    def left_click(self, event):
        row, col = point = self.reverse_transform(event)
        if 0 <= row < self.rows and 0 <= col < self.columns:
            if not self.grid_map[row][col]:
                self.delete("start")
                self.draw_point(point, color="red", tags="start")
                self.start_and_goal[0] = point

    # Jobb egérgombra beállítja célponotot
    def right_click(self, event):
        row, col = point = self.reverse_transform(event)
        if 0 <= row < self.rows and 0 <= col < self.columns:
            if not self.grid_map[row][col]:
                self.delete("goal")
                self.draw_point(point, color="green", tags="goal")
                self.start_and_goal[1] = point

    # Pontot rajzol
    def draw_point(self, point, color="black", tags=""):
        x, y = self.transform(point[0], point[1])
        radius = self.square_size / 4.0
        self.create_oval(x - radius, y - radius, x + radius, y + radius, fill=color, tags=tags)

    # Grid koordináták canvas koordinává alakítás a rajzoláshoz
    def transform(self, row, col):
        x = self.square_size * (col + 0.5)
        y = self.square_size * (row + 0.5)
        return (x, y)

    # Egérklikkel adott canvas koordináták grid koordinátákká alakítása
    def reverse_transform(self, event):
        row = int(event.y / self.square_size)
        col = int(event.x / self.square_size)
        return (row, col)

    # Útrajzolás
    def draw_path(self, path):
        self.delete("path")
        for i in range(1, len(path)):
            row1, col1 = path[i - 1]
            row2, col2 = path[i]
            x1, y1 = self.transform(row1, col1)
            x2, y2 = self.transform(row2, col2)
            self.create_line(x1, y1, x2, y2, fill="green", width=5, tags="path")

    # Út törlése
    def clear_path(self):
        self.delete("path")


# GUI a grid navigálásához
class GridNavigationGUI(tkinter.Frame):
    def __init__(self, master, grid_map):
        tkinter.Frame.__init__(self, master)
        self.grid_map = grid_map
        self.start_and_goal = [None, None]

        self.title_label = tkinter.Label(self, text="Grid Navigation", font=("Roboto", 16, "bold"))
        self.title_label.pack(pady=10)

        self.grid_canvas = GridCanvas(self, grid_map, self.start_and_goal)
        self.grid_canvas.pack(side=tkinter.LEFT, padx=10, pady=10)

        menu = tkinter.Frame(self, padx=20, pady=10)

        tkinter.Label(menu, text="Left click: Set start point.", font=("Roboto", 10)).grid(row=0, column=0, sticky=tkinter.W, pady=5)
        tkinter.Label(menu, text="Right click: Set goal point.", font=("Roboto", 10)).grid(row=1, column=0, sticky=tkinter.W, pady=5)

        tkinter.Button(menu, text="Search Path", command=self.search_path, width=20, height=2, bg="green", font=("Roboto", 12)).grid(row=2, column=0, pady=10)
        tkinter.Button(menu, text="Clear Path", command=self.clear_path, width=20, height=2, bg="red", font=("Roboto", 12)).grid(row=3, column=0, pady=10)

        separator = tkinter.Frame(self, height=2, bd=1, relief="sunken")
        separator.pack(fill=tkinter.X, padx=5, pady=5)

        menu.pack(side=tkinter.RIGHT, fill=tkinter.Y, padx=10, pady=10)

        self.pack_propagate(False)
        self.configure(width=800, height=600)

    # Út megkeresése és megrajzolása
    def search_path(self):
        start, goal = self.start_and_goal
        if start is not None and goal is not None:
            path = grid.find_optimal_path(start, goal, self.grid_map)
            if path:
                self.grid_canvas.draw_path(path)

    # Út törlése
    def clear_path(self):
        self.grid_canvas.clear_path()


# Térkép betöltése a txt fájlból
def load_grid_map(grid_map_file):
    grid_map = []
    with open(grid_map_file) as infile:
        for row_index, row_data in enumerate(infile, start=1):
            grid_map.append([])
            for col_index, char in enumerate(row_data.strip(), start=1):
                if char == ".":
                    grid_map[-1].append(False)  # Üres
                elif char == "X":
                    grid_map[-1].append(True)  # Akadály
                else:
                    print(f"Unknown character '{char}' at row {row_index}, column {col_index}.")
                    return None
    if len(grid_map) < 1:
        print("The grid map must have at least one row.")
        return None
    if len(grid_map[0]) < 1:
        print("The grid map must have at least one column.")
        return None
    if not all(len(row) == len(grid_map[0]) for row in grid_map):
        print("Not all rows are of equal length.")
        return None
    return grid_map


if __name__ == "__main__":
    root = tkinter.Tk()
    root.title("Grid Navigation")
    grid_map = load_grid_map(sys.argv[1])
    if grid_map is not None:
        GridNavigationGUI(root, grid_map).pack()
        root.resizable(height=False, width=False)
        root.mainloop()

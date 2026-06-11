import random


class MazeGenerator:
    """Generates and renders a maze using a randomised iterative backtracker.

    The maze is stored as a 2D grid of integers where each value encodes which
    walls are closed using a 4-bit bitmask (N=bit0, E=bit1, S=bit2, W=bit3).
    """

    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], rng: random.Random) -> None:
        """Set up an empty maze grid ready to be generated.

        All cells start with all four walls closed (value 15 = 0b1111).
        No paths are carved yet; call generate() to do that.

        Args:
            width: Number of columns in the maze.
            height: Number of rows in the maze.
            entry: Starting cell for the generation algorithm as (row, col).
            rng: A seeded random.Random instance for reproducible generation.
        """

        self.width = width
        self.height = height
        self.entry = entry
        self.rng = rng
        self.matrix = [[15 for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]
        self.movements: dict[int, tuple[tuple[int, int], int]] = {
            0: ((-1, 0), 2),
            1: ((0, 1), 3),
            2: ((1, 0), 0),
            3: ((0, -1), 1)
        }

    def generate(self) -> None:
        """Carve paths through the maze using a randomised iterative
        backtracker.

        Starts from the entry cell and repeatedly moves to a random unvisited
        neighbour, removing the wall between them. When no unvisited neighbours
        are available, it backtracks to the previous cell. This continues until
        every cell has been visited, producing a perfect maze.
        """

        bag: list[tuple[int, int]] = []
        y_actual = self.entry[0]
        x_actual = self.entry[1]
        self.visited[y_actual][x_actual] = True
        bag.append((y_actual, x_actual))

        while bag:
            possible: list[tuple[int, int, int]] = []
            for direction, data in self.movements.items():
                move_y = data[0][0]
                move_x = data[0][1]
                new_y = y_actual + move_y
                new_x = x_actual + move_x
                if (0 <= new_y < self.height and 0 <= new_x < self.width
                        and self.visited[new_y][new_x] is False):
                    possible.append((new_y, new_x, direction))

            if possible:
                selected = self.rng.choice(possible)
                next_y = selected[0]
                next_x = selected[1]
                selected_move = selected[2]
                opposite_move = self.movements[selected_move][1]
                self.matrix[y_actual][x_actual] &= ~(1 << selected_move)
                self.matrix[next_y][next_x] &= ~(1 << opposite_move)
                bag.append((next_y, next_x))
                self.visited[next_y][next_x] = True
                y_actual = next_y
                x_actual = next_x

            else:
                bag.pop()
                if bag:
                    y_actual = bag[-1][0]
                    x_actual = bag[-1][1]

    def apply_imperfection(self) -> None:
        """Remove some walls to create loops and multiple paths in the maze.

        Iterates over a sparse grid of cells (every 3 rows and columns) and
        randomly removes the south wall of each cell, connecting it to the one
        below. Cells inside or adjacent to the 42 pattern area are skipped to
        keep the pattern intact.
        """

        start_y = (self.height - 5) // 2
        start_x = (self.width - 7) // 2

        for y in range(1, self.height - 1, 3):
            for x in range(1, self.width - 1, 3):
                if (start_y <= y < start_y + 5 and start_x <= x < start_x
                    + 7) or (start_y <= y + 1 < start_y + 5 and start_x <=
                             x < start_x + 7):
                    continue

                if self.rng.randint(0, 100) < 50:
                    self.matrix[y][x] &= ~4
                    self.matrix[y + 1][x] &= ~1

    def format_as_hex(self) -> str:
        """Convert the maze matrix to a hex string ready for the output file.

        Each cell value (0-15) is written as a single uppercase hex character.
        Rows are separated by newlines.

        Returns:
            A multiline string with one hex character per cell.
        """

        lines: list[str] = []
        for line in self.matrix:
            hex_numbers: list[str] = []
            for num in line:
                hex_numbers.append(f"{num:X}")
            line_str = "".join(hex_numbers)
            lines.append(line_str)

        return "\n".join(lines)

    def get_letters(self, solution: list[tuple[int, int]]) -> str:
        """Convert a solution path into a string of direction letters.

        Compares consecutive cells in the path and determines whether each
        step goes North, South, East, or West.

        Args:
            solution: Ordered list of (row, col) cells from entry to exit.

        Returns:
            A string of direction letters, e.g. "SSEENW...".
        """

        letters: list[str] = []
        for cell_index in range(len(solution) - 1):
            current_y, current_x = solution[cell_index]
            next_y, next_x = solution[cell_index + 1]
            if next_y - current_y == -1:
                letters.append("N")
            elif next_y - current_y == 1:
                letters.append("S")
            elif next_x - current_x == 1:
                letters.append("E")
            elif next_x - current_x == -1:
                letters.append("W")

        return "".join(letters)

    def get_solution_char(self, y: int, x: int,
                          solution: list[tuple[int, int]]) -> str:
        """Return the Unicode box-drawing character for a cell on the
        solution path.

        Looks at where the path comes from and where it goes next for this
        cell, and picks the right character (straight line, corner, etc.) to
        draw a connected visual path through the maze.

        Args:
            y: Row of the cell.
            x: Column of the cell.
            solution: Full solution path as a list of (row, col) cells.

        Returns:
            A 3-character string with the appropriate box-drawing character.
        """

        cell_index = solution.index((y, x))
        current_y, current_x = solution[cell_index]
        coming_from = ""
        going_to = ""

        if cell_index > 0:
            previous_y, previous_x = solution[cell_index - 1]
            if previous_y - current_y == -1:
                coming_from = "N"
            elif previous_y - current_y == 1:
                coming_from = "S"
            elif previous_x - current_x == 1:
                coming_from = "E"
            elif previous_x - current_x == -1:
                coming_from = "W"

        if cell_index < len(solution) - 1:
            next_y, next_x = solution[cell_index + 1]
            if next_y - current_y == -1:
                going_to = "N"
            elif next_y - current_y == 1:
                going_to = "S"
            elif next_x - current_x == 1:
                going_to = "E"
            elif next_x - current_x == -1:
                going_to = "W"

        directions = frozenset([coming_from, going_to])
        char_map = {
            frozenset(["W", "E"]): "───",
            frozenset(["N", "S"]): " │ ",
            frozenset(["N", "E"]): " └─",
            frozenset(["N", "W"]): "─┘ ",
            frozenset(["S", "E"]): " ┌─",
            frozenset(["S", "W"]): "─┐ ",
            frozenset(["", "E"]): "───",
            frozenset(["", "W"]): "───",
            frozenset(["", "N"]): " │ ",
            frozenset(["", "S"]): " │ ",
        }

        return char_map.get(directions, " * ")

    def render(self, exit_coords: tuple[int, int],
               solution: list[tuple[int, int]] | None = None,
               wall_color: str = "", pattern_color: str = "",
               use_colors: bool = True) -> str:
        """Build the full ASCII visual of the maze as a string.

        Draws each cell row by row using box-drawing characters for walls. The
        entry cell is marked as S (green), the exit as E (red), fully walled
        cells as filled blocks, and the solution path in cyan if provided.

        Args:
            exit_coords: Exit cell as (row, col), used to mark it red.
            solution: Optional list of (row, col) cells to draw as a path.
            wall_color: ANSI escape code string for wall colour.
            pattern_color: ANSI escape code string for the 42 pattern colour.
            use_colors: If False, all colour codes are removed (plain text).

        Returns:
            A multiline string ready to be printed to the terminal.
        """

        reset = "\033[0m"
        cyan = "\033[96m"
        green = "\033[92m"
        red = "\033[91m"

        if use_colors is False:
            reset = ""
            cyan = ""
            green = ""
            red = ""

        def coloring(text: str) -> str:
            """Wrap text with the wall colour code, or return it unchanged if
            no colour is set.
            """

            return f"{wall_color}{text}{reset}" if wall_color else text

        def coloring_pattern(text: str) -> str:
            """Wrap text with the 42 pattern colour code, or return it
            unchanged if no colour is set.
            """

            return f"{pattern_color}{text}{reset}" if pattern_color else text

        lines: list[str] = []

        for y, line in enumerate(self.matrix):
            top_line = ""
            mid_line = ""
            for x, cell in enumerate(line):
                if (cell & (1 << 0)) != 0:
                    top_line = top_line + coloring("+━━━")
                else:
                    top_line = top_line + coloring("+") + "   "

                if solution and (y, x) in solution:
                    solution_char = self.get_solution_char(y, x, solution)
                    if (y, x) == self.entry:
                        solution_char = f"{green}{solution_char}{reset}"
                    elif (y, x) == exit_coords:
                        solution_char = f"{red}{solution_char}{reset}"
                    else:
                        solution_char = f"{cyan}{solution_char}{reset}"

                    if (cell & (1 << 3)) != 0:
                        mid_line = mid_line + coloring("┃") + solution_char
                    else:
                        mid_line = mid_line + " " + solution_char

                else:
                    if (cell & (1 << 3)) != 0:
                        left_wall = coloring("┃")
                    else:
                        left_wall = " "
                    if (y, x) == self.entry:
                        content = f"{green} S {reset}"
                    elif (y, x) == exit_coords:
                        content = f"{red} E {reset}"
                    elif cell == 15:
                        content = coloring_pattern(" █ ")
                    else:
                        content = "   "
                    mid_line = mid_line + left_wall + content

            top_line = top_line + coloring("+")
            if (line[-1] & (1 << 1)) != 0:
                mid_line = mid_line + coloring("┃")
            else:
                mid_line = mid_line + " "

            lines.append(top_line)
            lines.append(mid_line)

        bottom_line = ""
        for cell in self.matrix[-1]:
            if (cell & (1 << 2)) != 0:
                bottom_line = bottom_line + coloring("+━━━")
            else:
                bottom_line = bottom_line + coloring("+") + "   "

        bottom_line = bottom_line + coloring("+")
        lines.append(bottom_line)

        return "\n".join(lines)

    def apply_42(self) -> str:
        """Stamp the number 42 into the centre of the maze grid.

        Marks a 5x7 area of cells in the centre of the maze to represent
        the digits 4 and 2. Cells that are part of the pattern are set to
        fully walled (value 15) and marked as visited so the generator
        will not carve through them. Their neighbours are also walled off
        to keep the pattern isolated.

        Returns:
            An empty string on success, or an error message string if the
            maze is too small to fit the pattern.
        """

        pattern = [
            [1, 0, 1, 0, 1, 1, 1],
            [1, 0, 1, 0, 0, 0, 1],
            [1, 1, 1, 0, 1, 1, 1],
            [0, 0, 1, 0, 1, 0, 0],
            [0, 0, 1, 0, 1, 1, 1]
        ]

        if self.height < 7 or self.width < 9:
            return ("Error: 42 pattern will be omitted since the maze is "
                    "smaller than it")

        start_y = (self.height - 5) // 2
        start_x = (self.width - 7) // 2

        for pattern_y in range(5):
            for pattern_x in range(7):
                real_y = start_y + pattern_y
                real_x = start_x + pattern_x
                if pattern[pattern_y][pattern_x] == 1:
                    self.matrix[real_y][real_x] = 15
                    self.visited[real_y][real_x] = True
                else:
                    self.matrix[real_y][real_x] = 15
                    self.visited[real_y][real_x] = False

        for pattern_y in range(5):
            for pattern_x in range(7):
                if pattern[pattern_y][pattern_x] == 1:
                    real_y = start_y + pattern_y
                    real_x = start_x + pattern_x
                    if real_y > 0:
                        self.matrix[real_y - 1][real_x] |= (1 << 2)
                    if real_y < self.height - 1:
                        self.matrix[real_y + 1][real_x] |= (1 << 0)
                    if real_x > 0:
                        self.matrix[real_y][real_x - 1] |= (1 << 1)
                    if real_x < self.width - 1:
                        self.matrix[real_y][real_x + 1] |= (1 << 3)

        return ""

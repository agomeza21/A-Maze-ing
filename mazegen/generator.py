import random


class MazeGenerator:
    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], rng: random.Random) -> None:
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
        lines: list[str] = []
        for line in self.matrix:
            hex_numbers: list[str] = []
            for num in line:
                hex_numbers.append(f"{num:X}")
            line_str = "".join(hex_numbers)
            lines.append(line_str)
        return "\n".join(lines)

    def get_letters(self, solution: list[tuple[int, int]]) -> str:
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
            return f"{wall_color}{text}{reset}" if wall_color else text

        def coloring_pattern(text: str) -> str:
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

    def apply_42(self, before_generating: bool = True) -> str:
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

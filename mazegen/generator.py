import random


class MazeGenerator:
    def __init__(self, width: int, height: int,
                 entry: tuple[int, int]) -> None:
        self.width = width
        self.height = height
        self.entry = entry
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
                selected = random.choice(possible)
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

    def format_as_hex(self) -> str:
        lines: list[str] = []
        for line in self.matrix:
            hex_numbers: list[str] = []
            for num in line:
                hex_numbers.append(f"{num:X}")
            line_str = "".join(hex_numbers)
            lines.append(line_str)
        return "\n".join(lines)

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

    def render(self, solution: list[tuple[int, int]] | None = None) -> str:
        lines: list[str] = []

        for y, line in enumerate(self.matrix):
            top_line = ""
            mid_line = ""
            for x, cell in enumerate(line):
                if (cell & (1 << 0)) != 0:
                    top_line = top_line + "+---"
                else:
                    top_line = top_line + "+   "
                if solution and (y, x) in solution:
                    solution_char = self.get_solution_char(y, x, solution)
                    if (cell & (1 << 3)) != 0:
                        mid_line = mid_line + f"|{solution_char}"
                    else:
                        mid_line = mid_line + f" {solution_char}"
                else:
                    if (cell & (1 << 3)) != 0:
                        mid_line = mid_line + "|   "
                    else:
                        mid_line = mid_line + "    "
            top_line = top_line + "+"
            if (line[-1] & (1 << 1)) != 0:
                mid_line = mid_line + "|"
            else:
                mid_line = mid_line + " "
            lines.append(top_line)
            lines.append(mid_line)

        bottom_line = ""
        for cell in self.matrix[-1]:
            if (cell & (1 << 2)) != 0:
                bottom_line = bottom_line + "+---"
            else:
                bottom_line = bottom_line + "+   "
        bottom_line = bottom_line + "+"
        lines.append(bottom_line)

        return "\n".join(lines)

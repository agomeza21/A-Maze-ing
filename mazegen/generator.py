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
                hex_numbers.append(f"{num:x}")
            line_str = " ".join(hex_numbers)
            lines.append(line_str)
        return "\n".join(lines)

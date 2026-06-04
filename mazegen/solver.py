class MazeSolver:
    def __init__(self, matrix: list[list[int]], entry: tuple[int, int],
                 exit: tuple[int, int]) -> None:
        self.matrix = matrix
        self.entry = entry
        self.exit = exit
        self.height = len(matrix)
        self.width = len(matrix[0]) if self.height > 0 else 0
        self.visited = [[False for _ in range(self.width)]
                        for _ in range(self.height)]
        self.movements: dict[int, tuple[tuple[int, int], int]] = {
            0: ((-1, 0), 2),
            1: ((0, 1), 3),
            2: ((1, 0), 0),
            3: ((0, -1), 1)
        }

    def solve(self) -> list[tuple[int, int]]:
        bag: list[tuple[int, int]] = []
        bag.append(self.entry)
        y_actual = self.entry[0]
        x_actual = self.entry[1]
        self.visited[y_actual][x_actual] = True

        while bag:
            if y_actual == self.exit[0] and x_actual == self.exit[1]:
                return bag

            possible: list[tuple[int, int, int]] = []
            for direction, data in self.movements.items():
                move_y = data[0][0]
                move_x = data[0][1]
                new_y = y_actual + move_y
                new_x = x_actual + move_x
                if (0 <= new_y < self.height and 0 <= new_x < self.width
                        and self.visited[new_y][new_x] is False
                        and (self.matrix[y_actual][x_actual]
                             & (1 << direction)) == 0):
                    possible.append((new_y, new_x, direction))
            if possible:
                selected = possible[0]
                next_y = selected[0]
                next_x = selected[1]
                bag.append((next_y, next_x))
                self.visited[next_y][next_x] = True
                y_actual = next_y
                x_actual = next_x
            else:
                bag.pop()
                if bag:
                    y_actual = bag[-1][0]
                    x_actual = bag[-1][1]

        return []

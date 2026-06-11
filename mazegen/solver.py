class MazeSolver:
    """Finds the shortest path through a maze from entry to exit.

    Uses a simple DFS for perfect mazes (one unique path) and a cost-based
    exhaustive search for imperfect mazes (multiple possible paths).
    """

    def __init__(self, matrix: list[list[int]], entry: tuple[int, int],
                 exit: tuple[int, int], perfect: bool = True) -> None:
        """Set up the solver with the maze data and start/end positions.

        Args:
            matrix: The maze grid as a 2D list of wall bitmask integers.
            entry: Entry cell as (row, col).
            exit: Exit cell as (row, col).
            perfect: If True, uses the faster DFS solver. If False, uses
                     the cost-based solver that finds the shortest path
                     even when multiple routes exist.
        """

        self.matrix = matrix
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
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

    def solve_perfect(self) -> list[tuple[int, int]]:
        """Find the unique path from entry to exit in a perfect maze.

        Uses an iterative DFS with backtracking. Because the maze is perfect,
        there's only one possible path, so the first one found is the shortest.

        Returns:
            An ordered list of (row, col) cells from entry to exit,
            or an empty list if no path exists.
        """

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

    def solve_imperfect(self) -> list[tuple[int, int]]:
        """Find the shortest path from entry to exit in an imperfect maze.

        Uses a cost-based exhaustive search. Every time a cell is reached,
        the cost (number of steps taken) is recorded. A neighbour is only
        explored if the new cost to reach it is lower than any previously
        recorded cost. This guarantees the shortest path is found even when
        multiple routes exist.

        Returns:
            An ordered list of (row, col) cells representing the shortest
            path from entry to exit, or an empty list if no path exists.
        """

        cost = [[float('inf') for _ in range(self.width)]
                for _ in range(self.height)]
        best_solution: list[tuple[int, int]] = []
        cost[self.entry[0]][self.entry[1]] = 0
        bag: list[tuple[int, int]] = []
        bag.append(self.entry)
        y_actual = self.entry[0]
        x_actual = self.entry[1]

        while bag:
            if y_actual == self.exit[0] and x_actual == self.exit[1]:
                if not best_solution or len(bag) < len(best_solution):
                    best_solution = list(bag)
                bag.pop()
                if bag:
                    y_actual = bag[-1][0]
                    x_actual = bag[-1][1]
                continue

            possible: list[tuple[int, int, int]] = []
            for direction, data in self.movements.items():
                move_y = data[0][0]
                move_x = data[0][1]
                new_y = y_actual + move_y
                new_x = x_actual + move_x
                if (0 <= new_y < self.height and 0 <= new_x < self.width
                    and (self.matrix[y_actual][x_actual]
                         & (1 << direction)) == 0):
                    if cost[y_actual][x_actual] + 1 < cost[new_y][new_x]:
                        possible.append((new_y, new_x, direction))

            if possible:
                selected = possible[0]
                next_y = selected[0]
                next_x = selected[1]
                cost[next_y][next_x] = cost[y_actual][x_actual] + 1
                bag.append((next_y, next_x))
                y_actual = next_y
                x_actual = next_x

            else:
                bag.pop()
                if bag:
                    y_actual = bag[-1][0]
                    x_actual = bag[-1][1]

        return best_solution

    def solve(self) -> list[tuple[int, int]]:
        """Solve the maze using the appropriate algorithm.

        Calls solve_perfect() if the maze is perfect, or solve_imperfect()
        otherwise.

        Returns:
            An ordered list of (row, col) cells from entry to exit.
        """

        if self.perfect:
            return self.solve_perfect()
        else:
            return self.solve_imperfect()

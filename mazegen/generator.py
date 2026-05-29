class MazeGenerator:
    def __init__(self, width: int, height: int, entry: tuple[int, int]) -> None:
        self.width = width
        self.height = height
        self.matriz = [[15 for _ in range(width)] for _ in range(height)]
        self.visited = [[False for _ in range(width)] for _ in range(height)]

    def generate(self) -> None:
        bag: list[tuple[int, int]] = []

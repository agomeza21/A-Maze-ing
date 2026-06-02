import sys
from mazegen.generator import MazeGenerator


def parse_config(file: str) -> dict[str, str]:
    content: dict[str, str] = {}
    try:
        with open(file, "r") as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    key, value = stripped_line.split("=", 1)
                    content[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: configuration file '{file}' not found.")
        sys.exit(1)
    return content


def main() -> None:
    if len(sys.argv) not in [2, 3]:
        print("Usage: python3 a_maze_ing.py <config_file> [output_file.maze]")
        sys.exit(1)

    content = parse_config(sys.argv[1])
    width = int(content["WIDTH"])
    height = int(content["HEIGHT"])

    entry_x, entry_y = map(int, content["ENTRY"].split(","))
    entry = (entry_y, entry_x)

    generator = MazeGenerator(width, height, entry)
    generator.generate()
    print(generator.render())


if __name__ == "__main__":
    main()

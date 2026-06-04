import sys
from mazegen.generator import MazeGenerator


def parse_config(file: str) -> dict[str, str]:
    content: dict[str, str] = {}
    try:
        with open(file, "r") as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    if "=" in stripped_line:
                        key, value = stripped_line.split("=", 1)
                        content[key.strip().upper()] = value.strip()
                    else:
                        print(f"Error: Invalid configuration "
                              f"format -> '{stripped_line}'")
                        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: configuration file '{file}' not found.")
        sys.exit(1)
    return content


def load_maze(file_path: str) -> list[list[int]]:
    try:
        with open(file_path, "r") as f:
            matrix: list[list[int]] = []
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    continue
                row: list[int] = []
                for char in stripped_line:
                    row.append(int(char, 16))
                matrix.append(row)
    except FileNotFoundError:
        print(f"Error: Maze file '{file_path}' not found.")
        sys.exit(1)
    except ValueError:
        print(f"Error: Invalid character found in maze file '{file_path}'."
              f"Must be hexadecimal.")
        sys.exit(1)

    return matrix


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    content = parse_config(sys.argv[1])

    try:
        width = int(content["WIDTH"])
        height = int(content["HEIGHT"])
        entry_x, entry_y = map(int, content["ENTRY"].split(","))
    except (KeyError, ValueError):
        print("Error: Invalid or missing numeric values in "
              "configuration file.")
        sys.exit(1)

    if not (0 <= entry_x < width and 0 <= entry_y < height):
        print("Error: ENTRY coordinates are out of maze bounds.")
        sys.exit(1)

    entry = (entry_y, entry_x)

    output_filename = content.get("OUTPUT_FILE")
    key, value = output_filename.split(".", -1)  # type: ignore
    if value != "txt":
        print("Error: outputfile is not a '.txt'")
        sys.exit(1)
    if not output_filename:
        output_filename = "maze.txt"

    generator = MazeGenerator(width, height, entry)
    generator.generate()

    try:
        with open(output_filename, "w") as f:
            f.write(generator.format_as_hex())
        print("Maze generated correctly!")
        print(f"File saved as '{output_filename}'.")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)

    print("\n--- GRAPHIC RENDER ---")
    print(generator.render())


if __name__ == "__main__":
    main()

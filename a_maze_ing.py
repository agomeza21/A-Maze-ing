import sys
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver


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


def validate(content: dict[str, str]) -> tuple[int, int, tuple[int, int],
                                               tuple[int, int], str, bool]:
    try:
        width = int(content["WIDTH"])
        height = int(content["HEIGHT"])
        entry_x, entry_y = map(int, content["ENTRY"].split(","))
    except (KeyError, ValueError):
        print("Error: Invalid or missing ENTRY in configuration file.")
        sys.exit(1)
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        print("Error: ENTRY coordinates are out of maze bounds.")
        sys.exit(1)
    entry = (entry_y, entry_x)

    try:
        exit_x, exit_y = map(int, content["EXIT"].split(","))
    except (KeyError, ValueError):
        print("Error: Invalid or missing EXIT in configuration file.")
        sys.exit(1)
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        print("Error: EXIT coordinates are out of maze bounds.")
        sys.exit(1)
    exit_coords = (exit_y, exit_x)

    output_filename = content.get("OUTPUT_FILE")
    if not output_filename:
        output_filename = "maze.txt"
    if not output_filename.endswith(".txt"):
        print("Error: outputfile is not a '.txt'")
        sys.exit(1)

    try:
        perfect_str = content.get("PERFECT")
        if not perfect_str:
            perfect_str = "True"
        if perfect_str.upper() == "TRUE":
            perfect = True
        elif perfect_str.upper() == "FALSE":
            perfect = False
    except ValueError:
        print("Error: Invalid PERFECT in configuration file.")
        sys.exit(1)

    return width, height, entry, exit_coords, output_filename, perfect


def save_maze_file(output_filename: str, data: str, entry: tuple[int, int],
                   exit_coords: tuple[int, int], letters: str) -> None:
    try:
        with open(output_filename, "w") as f:
            f.write(data)
            f.write("\n\n")
            entry_str = f"{entry[1]},{entry[0]}\n"
            f.write(entry_str)
            exit_str = f"{exit_coords[1]},{exit_coords[0]}\n"
            f.write(exit_str)
            f.write(f"{letters}")
        print("Maze generated correctly!")
        print(f"File saved as '{output_filename}'.")
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)


def load_maze(file_path: str) -> list[list[int]]:
    try:
        with open(file_path, "r") as f:
            matrix: list[list[int]] = []
            for line in f:
                stripped_line = line.strip()
                if not stripped_line:
                    break
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
    width, height, entry, exit_coords, out_file, perfect = validate(content)

    show_solution = False

    while True:
        print("\n--- A-MAZE-ING MENU ---\n")
        print("1. Generate and save maze")
        print("2. Show/Hide solution to maze")
        print("3. Change wall colours")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        if choice == "1":
            generator = MazeGenerator(width, height, entry)
            generator.generate()
            if not perfect:
                generator.apply_imperfection()
            solver = MazeSolver(generator.matrix, entry,
                                exit_coords, perfect=perfect)
            solution = solver.solve()
            save_maze_file(out_file, generator.format_as_hex(),
                           entry, exit_coords, generator.get_letters(solution))
            print(generator.render())
        elif choice == "2":
            show_solution = not show_solution
            matrix = load_maze(out_file)
            if matrix:
                renderer = MazeGenerator(width, height, entry)
                renderer.matrix = matrix
                if show_solution:
                    solver = MazeSolver(matrix, entry,
                                        exit_coords, perfect=perfect)
                    solution = solver.solve()
                    print(renderer.render(solution))
                else:
                    print(renderer.render(None))
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()

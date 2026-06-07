import sys
import os
import random
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
                                               tuple[int, int], str, bool,
                                               str | None]:
    try:
        width = int(content["WIDTH"])
        height = int(content["HEIGHT"])
        if width > 52 or height > 20:
            print("Error: Maximum dimensions are WIDTH=52 and HEIGHT=20.")
            sys.exit(1)
        if width < 5 or height < 5:
            print("Error: Minimum dimensions are 5x5.")
    except (KeyError, ValueError):
        print("Error: Invalid or missing WIDTH/HEIGHT in configuration file.")
        sys.exit(1)
    try:
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

    if height >= 5 and width >= 7:
        start_y = (height - 5) // 2
        start_x = (width - 7) // 2
        if (start_y <= entry[0] < start_y
                + 5) and (start_x <= entry[1] < start_x + 7):
            print("Error: ENTRY coordinates cannot be "
                  "inside the central 42 pattern.")
            sys.exit(1)
        if (start_y <= exit_coords[0] < start_y
                + 5) and (start_x <= exit_coords[1] < start_x + 7):
            print("Error: EXIT coordinates cannot be "
                  "inside the central 42 pattern.")
            sys.exit(1)

    output_filename = content.get("OUTPUT_FILE")
    if not output_filename:
        output_filename = "maze.txt"
    if not output_filename.endswith(".txt"):
        print("Error: outputfile is not a '.txt'")
        sys.exit(1)

    perfect_str = content.get("PERFECT")
    if not perfect_str:
        perfect_str = "True"
    else:
        val = perfect_str.upper()
        if val == "TRUE":
            perfect = True
        elif val == "FALSE":
            perfect = False
        else:
            print("Error: Invalid PERFECT in configuration file.")
            sys.exit(1)

    seed = content.get("SEED")

    return width, height, entry, exit_coords, output_filename, perfect, seed


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
            f.write(f"{letters}\n")
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
    width, height, entry, exit_c, out_file, perfect, seed_v = validate(content)

    show_solution = False

    seed_msg = "Maze seed in memory: Unknown"

    themes = [
        ("", ""),
        ("\033[38;5;203m", "\033[38;5;88m"),
        ("\033[38;5;88m", "\033[38;5;203m"),
        ("\033[38;5;120m", "\033[38;5;28m"),
        ("\033[38;5;28m", "\033[38;5;120m"),
        ("\033[38;5;25m", "\033[38;5;117m"),
        ("\033[38;5;228m", "\033[38;5;130m"),
        ("\033[38;5;130m", "\033[38;5;228m"),
        ("\033[38;5;219m", "\033[38;5;90m"),
        ("\033[38;5;90m", "\033[38;5;219m"),
    ]
    current_theme = 0

    while True:
        print("\n--- A-MAZE-ING MENU ---\n")
        print("1. Generate and save maze")
        print("2. Show/Hide solution to maze")
        print("3. Change wall colours")
        print("4. Exit")

        choice = input("\nSelect an option: ").strip()

        c_wall, c_pattern = themes[current_theme]

        if choice == "1":
            show_solution = False
            if seed_v is None:
                current_seed = random.randint(1, 9999999)
                seed_msg = f"\n[INFO] Playing with seed: '{current_seed}'"
                random.seed(current_seed)
            else:
                seed_msg = (f"\n[INFO] Playing with config "
                            f"seed: '{seed_v}'")
                random.seed(seed_v)
            generator = MazeGenerator(width, height, entry)
            generator.apply_42()
            generator.generate()
            if not perfect:
                generator.apply_imperfection()
            solver = MazeSolver(generator.matrix, entry,
                                exit_c, perfect=perfect)
            solution = solver.solve()
            save_maze_file(out_file, generator.format_as_hex(),
                           entry, exit_c, generator.get_letters(solution))
            print(seed_msg)
            print(generator.render(exit_c, solution if show_solution
                                   else None, wall_color=c_wall,
                                   pattern_color=c_pattern))

        elif choice == "2":
            show_solution = not show_solution
            if os.path.exists(out_file):
                matrix = load_maze(out_file)
                if matrix:
                    renderer = MazeGenerator(width, height, entry)
                    renderer.matrix = matrix
                    if show_solution:
                        solver = MazeSolver(matrix, entry,
                                            exit_c, perfect=perfect)
                        solution = solver.solve()
                        print(seed_msg)
                        print(renderer.render(exit_c, solution,
                                              wall_color=c_wall,
                                              pattern_color=c_pattern))
                    else:
                        print(seed_msg)
                        print(renderer.render(exit_c, None,
                                              wall_color=c_wall,
                                              pattern_color=c_pattern))
            else:
                print("\n(There is no maze generated. "
                      "Click 1 to generate one).")

        elif choice == "3":
            current_theme = (current_theme + 1) % len(themes)
            c_wall, c_pattern = themes[current_theme]
            if os.path.exists(out_file):
                matrix = load_maze(out_file)
                if matrix:
                    renderer = MazeGenerator(width, height, entry)
                    renderer.matrix = matrix
                    if show_solution:
                        solver = MazeSolver(matrix, entry, exit_c,
                                            perfect=perfect)
                        solution = solver.solve()
                        print(seed_msg)
                        print(renderer.render(exit_c, solution,
                                              wall_color=c_wall,
                                              pattern_color=c_pattern))
                    else:
                        print(seed_msg)
                        print(renderer.render(exit_c, None,
                                              wall_color=c_wall,
                                              pattern_color=c_pattern))
            else:
                print("\n(There is no maze generated. "
                      "Click 1 to generate one).")

        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()

import sys
import random
import time
from mazegen.generator import MazeGenerator
from mazegen.solver import MazeSolver


def parse_config(file: str) -> dict[str, str]:
    """Read the configuration file and return its contents as a dictionary.

    Each line in the file must follow the KEY=VALUE format.
    Lines starting with '#' are treated as comments and ignored.
    If a key appears more than once, or the format is wrong, the program exits.

    Args:
        file: Path to the configuration file.

    Returns:
        A dictionary where each key is a config parameter and each value
        is the corresponding string value from the file.
    """

    content: dict[str, str] = {}
    try:
        with open(file, "r") as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line and not stripped_line.startswith("#"):
                    if "=" in stripped_line:
                        key, value = stripped_line.split("=", 1)
                        key = key.strip().upper()
                        if key in content:
                            print(f"Error: Duplicate parameter '{key}' "
                                  "in configuration file.")
                            sys.exit(1)
                        content[key] = value.strip()
                    else:
                        print(f"Error: Invalid configuration "
                              f"format -> '{stripped_line}'")
                        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: configuration file '{file}' not found.")
        sys.exit(1)
    except PermissionError:
        print(f"Error: Permission denied reading configuration file '{file}'.")
        sys.exit(1)
    return content


def validate(content: dict[str, str]) -> tuple[int, int, tuple[int, int],
                                               tuple[int, int], str, bool,
                                               str | None, str | None,
                                               str | None]:
    """Check that config values are correct and return them as usable types.

    Reads the raw string dictionary from parse_config and converts each value
    to its proper type (int, bool, tuple...). Raises ValueError with a clear
    message if any value is missing, has the wrong type, or is out of range.

    Args:
        content: Raw config dictionary as returned by parse_config.

    Returns:
        A tuple with: width, height, entry (row, col), exit (row, col),
        output filename, perfect flag, seed string, ANSI wall colour code,
        and ANSI pattern colour code. Colour codes are None if not set.

    Raises:
        ValueError: If any config value is invalid or missing.
    """

    try:
        width = int(content["WIDTH"])
        height = int(content["HEIGHT"])
    except (KeyError, ValueError):
        raise ValueError("Error: Invalid or missing WIDTH/HEIGHT in "
                         "configuration file.")
    if width > 52 or height > 20:
        raise ValueError("Error: Maximum dimensions are WIDTH=52 and "
                         "HEIGHT=20.")
    if width < 5 or height < 5:
        raise ValueError("Error: Minimum dimensions are 5x5.")

    try:
        entry_x, entry_y = map(int, content["ENTRY"].split(","))
    except (KeyError, ValueError):
        raise ValueError("Error: Invalid or missing ENTRY in "
                         "configuration file.")
    if not (0 <= entry_x < width and 0 <= entry_y < height):
        raise ValueError("Error: ENTRY coordinates are out of maze bounds.")
    entry = (entry_y, entry_x)

    try:
        exit_x, exit_y = map(int, content["EXIT"].split(","))
    except (KeyError, ValueError):
        raise ValueError("Error: Invalid or missing EXIT in "
                         "configuration file.")
    if not (0 <= exit_x < width and 0 <= exit_y < height):
        raise ValueError("Error: EXIT coordinates are out of maze bounds.")
    exit_coords = (exit_y, exit_x)

    if entry_x == exit_x and entry_y == exit_y:
        raise ValueError("Error: ENTRY and EXIT can't be the same.")

    if height >= 5 and width >= 7:
        start_y = (height - 5) // 2
        start_x = (width - 7) // 2
        if (start_y <= entry[0] < start_y
                + 5) and (start_x <= entry[1] < start_x + 7):
            raise ValueError("Error: ENTRY coordinates cannot be "
                  "inside the central 42 pattern.")
        if (start_y <= exit_coords[0] < start_y
                + 5) and (start_x <= exit_coords[1] < start_x + 7):
            raise ValueError("Error: EXIT coordinates cannot be "
                  "inside the central 42 pattern.")

    output_filename = content.get("OUTPUT_FILE")
    if not output_filename:
        output_filename = "maze.txt"
    if ("/" in output_filename or "\\" in output_filename
            or ".." in output_filename):
        raise ValueError("Error: OUTPUT_FILE must be a simple filename, "
                         "not a path.")
    if not output_filename.endswith(".txt"):
        raise ValueError("Error: outputfile is not a '.txt'")
    if (output_filename == "maze_blueprint.txt"
            or output_filename == "config.txt"):
        raise ValueError("Error: OUTPUT_FILE can't have that name.")

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
            raise ValueError("Error: Invalid PERFECT in configuration file.")

    seed = content.get("SEED")

    color_wall = content.get("COLOR_WALL")
    if color_wall is not None:
        try:
            color_wall_int = int(color_wall)
        except ValueError:
            raise ValueError("Error: COLOR_WALL must be a number.")
        if not (0 <= color_wall_int <= 255):
            raise ValueError("Error: COLOR_WALL must be between 0 and 255.")
        ansi_wall = f"\033[38;5;{color_wall}m"
    else:
        ansi_wall = None

    color_pattern = content.get("COLOR_PATTERN")
    if color_pattern is not None:
        try:
            color_pattern_int = int(color_pattern)
        except ValueError:
            raise ValueError("Error: COLOR_PATTERN must be a number.")
        if not (0 <= color_pattern_int <= 255):
            raise ValueError("Error: COLOR_PATTERN must be between 0 and 255.")
        ansi_pattern = f"\033[38;5;{color_pattern}m"
    else:
        ansi_pattern = None

    return (width, height, entry, exit_coords, output_filename,
            perfect, seed, ansi_wall, ansi_pattern)


def save_maze_file(output_filename: str, data: str, entry: tuple[int, int],
                   exit_coords: tuple[int, int], letters: str) -> str:
    """Write the maze data to a text file in the required output format.

    The file contains the hex grid, then an empty line, then the entry
    coordinates, exit coordinates, and the shortest path as a string of
    direction letters (N, E, S, W).

    Args:
        output_filename: Name of the file to write.
        data: The maze grid formatted as a hex string.
        entry: Entry cell as (row, col).
        exit_coords: Exit cell as (row, col).
        letters: Shortest path directions, e.g. "SSEENW...".

    Returns:
        A success message string if the file was saved correctly.
    """

    try:
        with open(output_filename, "w") as f:
            f.write(data)
            f.write("\n\n")
            entry_str = f"{entry[1]},{entry[0]}\n"
            f.write(entry_str)
            exit_str = f"{exit_coords[1]},{exit_coords[0]}\n"
            f.write(exit_str)
            f.write(f"{letters}")
        return f"Maze generated correctly!\nFile saved as '{output_filename}'."

    except PermissionError:
        print(f"Error: Permission denied writing to "
              f"maze file '{output_filename}'.")
        sys.exit(1)
    except Exception as e:
        print(f"Error saving file: {e}")
        sys.exit(1)


def load_maze(file_path: str) -> list[list[int]]:
    """Read a maze file and return its grid as a matrix of integers.

    Reads the hex characters from the file line by line and converts each
    character to an integer. Stops at the first empty line (the rest of
    the file contains coordinates and path, not the grid).

    Args:
        file_path: Path to the maze output file.

    Returns:
        A 2D list of integers where each value encodes the walls of one cell.
    """

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
    except PermissionError:
        print(f"Error: Permission denied reading maze file '{file_path}'.")
        sys.exit(1)
    except ValueError:
        print(f"Error: Invalid character found in maze file '{file_path}'."
              f"Must be hexadecimal.")
        sys.exit(1)

    return matrix


def handle_generation_flow(width: int, height: int, entry: tuple[int, int],
                           exit_c: tuple[int, int], out_file: str,
                           perfect: bool, seed_v: str | None) -> str:
    """Generate a new maze, solve it, and save it to the output file.

    Creates the generator with the given parameters, stamps the 42 pattern,
    runs the backtracker algorithm, optionally applies imperfection, solves
    the maze, and writes the result to disk.

    Args:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        entry: Entry cell as (row, col).
        exit_c: Exit cell as (row, col).
        out_file: Name of the output file to write.
        perfect: If True, generates a perfect maze (one unique path).
        seed_v: Seed string for reproducibility. If None, a random one is used.

    Returns:
        A string with info messages (seed used, save confirmation).
    """

    info_msgs = []

    if seed_v is None:
        current_seed = str(random.randint(1, 9999999))
        seed_msg = f"\n[INFO] Playing with seed: '{current_seed}'\n"
    else:
        current_seed = seed_v
        seed_msg = (f"\n[INFO] Playing with config "
                    f"seed: '{current_seed}'\n")

    maze_rng = random.Random(current_seed)
    generator = MazeGenerator(width, height, entry, rng=maze_rng)
    omission_msg = generator.apply_42()
    if omission_msg:
        info_msgs.append(omission_msg)
    generator.generate()

    if not perfect:
        generator.apply_imperfection()

    solver = MazeSolver(generator.matrix, entry,
                        exit_c, perfect=perfect)
    solution = solver.solve()
    save_msg = save_maze_file(out_file, generator.format_as_hex(),
                              entry, exit_c, generator.get_letters(solution))
    info_msgs.append(save_msg)
    info_msgs.append(seed_msg)

    return "\n".join(info_msgs)


def handle_display_flow(out_file: str, width: int, height: int,
                        entry: tuple[int, int], exit_c: tuple[int, int],
                        perfect: bool, show_solution: bool, seed_msg: str,
                        c_wall: str, c_pattern: str, show_steps: bool) -> None:
    """Load the maze from disk and print it to the terminal.

    Reads the current maze file, renders it as ASCII art, and optionally
    overlays the solution path with an animation. Also prints the seed info
    and the number of steps if requested.

    Args:
        out_file: Name of the maze file to load.
        width: Expected number of columns (used to validate the file).
        height: Expected number of rows (used to validate the file).
        entry: Entry cell as (row, col).
        exit_c: Exit cell as (row, col).
        perfect: Used to choose the right solver (perfect or imperfect).
        show_solution: If True, the solution path is drawn on the maze.
        seed_msg: Info string with the current seed to print above the maze.
        c_wall: ANSI colour code for the walls.
        c_pattern: ANSI colour code for the 42 pattern cells.
        show_steps: If True, prints the number of steps in the shortest path.
    """

    matrix = load_maze(out_file)

    if matrix:
        if len(matrix) != height or len(matrix[0]) != width:
            print("\n[ERROR] The maze.txt has been modified. The dimensions "
                  "are not the same.")
            return

        print("\033[2J\033[H", end="")
        renderer = MazeGenerator(width, height, entry, rng=random.Random())

        renderer.matrix = matrix
        solution = None

        if show_solution or show_steps:
            solver = MazeSolver(matrix, entry, exit_c, perfect=perfect)
            solution = solver.solve()
        steps_msg = ""
        if show_steps and solution:
            steps_msg = (f"[CLUE] Shortest path: {len(solution) - 1} "
                         f"steps\n")
        if show_solution and solution:
            for i in range(1, len(solution) + 1):
                print("\033[H")
                print(seed_msg)
                if steps_msg:
                    print(steps_msg)
                print(renderer.render(exit_c, solution[:i], wall_color=c_wall,
                                      pattern_color=c_pattern))
                time.sleep(0.03)

            return

        print(seed_msg)
        if steps_msg:
            print(steps_msg)
        print(renderer.render(exit_c, None, wall_color=c_wall,
                              pattern_color=c_pattern))


def handle_parameter_modification(content: dict[str, str],
                                  themes: list[tuple[str, str]],
                                  current_theme: int) -> tuple[bool, int]:
    """Show a submenu to let the user change config parameters at runtime.

    The user can modify any valid config key or reset all values back to
    the original config file. Each change is validated before being applied.
    If validation fails, the previous value is restored automatically.

    Args:
        content: The current config dictionary (modified in place).
        themes: List of available wall/pattern colour theme pairs.
        current_theme: Index of the currently active theme.

    Returns:
        A tuple of (any_changes, current_theme) where any_changes is True
        if at least one parameter was successfully changed.
    """

    any_changes = False

    while True:
        print("\n--- PARAMETERS MODIFICATION ---\n")
        print("1. Modify a configuration parameter")
        print("2. Reset to original config.txt values")
        print("3. Return to main menu")

        try:
            sub_choice = input("\nSelect an option "
                               "(or type 'BACK'): ").strip().upper()
        except (EOFError, KeyboardInterrupt):
            print("[CONTROLED EXIT] See you soon!")
            sys.exit(0)

        if sub_choice == "3" or sub_choice == "BACK":
            print("Returning to main menu...")
            break

        if sub_choice == "1":
            valid_keys = [
                "WIDTH", "HEIGHT", "ENTRY", "EXIT",
                "OUTPUT_FILE", "PERFECT", "SEED",
                "COLOR_WALL", "COLOR_PATTERN"
            ]

            print("\nNOTICE: If you want to REDUCE WIDTH or HEIGHT, "
                  "make sure to modify ENTRY and EXIT first so "
                  "they fit within the new smaller boundaries!")

            print("\nCurrent configuration:")
            for key in valid_keys:
                print(f"  - {key}: {content.get(key, 'Not defined')}")

            try:
                param = input("\nEnter the parameter name to "
                              "change (or 'BACK'): ").strip().upper()
            except (EOFError, KeyboardInterrupt):
                print("[CONTROLED EXIT] See you soon!")
                sys.exit(0)

            if param == "BACK":
                continue
            if param not in valid_keys:
                print("Error: Invalid parameter name.")
                continue

            try:
                new_value = input(f"Enter new value for {param}: ").strip()
            except (EOFError, KeyboardInterrupt):
                print("[CONTROLED EXIT] See you soon!")
                sys.exit(0)

            old_value = content.get(param)
            content[param] = new_value

            try:
                (_, _, _, _, _, _, _, ansi_wall,
                 ansi_pattern) = validate(content)

                print(f"\n[SUCCESS] {param} updated successfully!")
                any_changes = True

                if param in ["COLOR_WALL", "COLOR_PATTERN"]:
                    current_theme = 0

                if ansi_wall is not None or ansi_pattern is not None:
                    if ansi_wall is not None:
                        w_final = ansi_wall
                    else:
                        w_final = ""
                    if ansi_pattern is not None:
                        p_final = ansi_pattern
                    else:
                        p_final = ""
                    themes[0] = (w_final, p_final)
            except ValueError as e:
                print(f"\n[INVALID VALUE] {e}")
                print("Your change was rejected. "
                      "Restoring previous valid state.")

                if old_value is not None:
                    content[param] = old_value
                else:
                    content.pop(param, None)

        elif sub_choice == "2":
            try:
                fresh_content = parse_config(sys.argv[1])
                (_, _, _, _, _, _, _, ansi_wall,
                 ansi_pattern) = validate(fresh_content)
                content.clear()
                content.update(fresh_content)

                w_final = ansi_wall if ansi_wall is not None else ""
                p_final = ansi_pattern if ansi_pattern is not None else ""
                themes[0] = (w_final, p_final)
                current_theme = 0

                print("\n[SUCCESS] Configuration reset to factory "
                      "values!")
                any_changes = True
            except ValueError as e:
                print(f"\nError resetting: {e}")

    return any_changes, current_theme


def main() -> None:
    """Entry point of the program.

    Reads the config file path from the command line, validates it, generates
    the first maze, and starts the interactive menu loop where the user can
    regenerate, solve, recolour, save the maze as a drawing, show the steps,
    modify the config file, and exit.
    """

    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    try:
        content = parse_config(sys.argv[1])
        (width, height, entry, exit_c, out_file, perfect, seed_v,
         ansi_wall, ansi_pattern) = validate(content)
    except ValueError as e:
        print(e)
        sys.exit(1)

    show_solution = False
    show_steps = False
    current_theme = 0

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

    if ansi_wall is not None or ansi_pattern is not None:
        w_final = ansi_wall if ansi_wall is not None else ""
        p_final = ansi_pattern if ansi_pattern is not None else ""
        themes[0] = (w_final, p_final)

    c_wall, c_pattern = themes[current_theme]

    seed_msg = handle_generation_flow(width, height, entry, exit_c, out_file,
                                      perfect, seed_v)
    handle_display_flow(out_file, width, height, entry, exit_c, perfect,
                        show_solution, seed_msg, c_wall, c_pattern, show_steps)

    while True:
        print("\n--- A-MAZE-ING MENU ---\n")
        print("1. Re-generate and save maze")
        print("2. Show/Hide solution to maze")
        print("3. Change wall colours")
        print("4. Save maze as drawing")
        print("5. Clue: Show/Hide path steps")
        print("6. Modify parameters / Reset config")
        print("7. Exit")

        try:
            choice = input("\nSelect an option: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("[CONTROLED EXIT] See you soon!")
            sys.exit(0)

        c_wall, c_pattern = themes[current_theme]

        if choice == "1":
            show_solution = False
            seed_msg = handle_generation_flow(width, height, entry, exit_c,
                                              out_file, perfect, seed_v)
            handle_display_flow(out_file, width, height, entry, exit_c,
                                perfect, show_solution, seed_msg, c_wall,
                                c_pattern, show_steps)

        elif choice == "2":
            show_solution = not show_solution
            handle_display_flow(out_file, width, height, entry, exit_c,
                                perfect, show_solution, seed_msg, c_wall,
                                c_pattern, show_steps)

        elif choice == "3":
            current_theme = (current_theme + 1) % len(themes)
            c_wall, c_pattern = themes[current_theme]
            handle_display_flow(out_file, width, height, entry, exit_c,
                                perfect, show_solution, seed_msg, c_wall,
                                c_pattern, show_steps)

        elif choice == "4":
            matrix_txt = load_maze(out_file)
            drawing = MazeGenerator(width, height, entry, rng=random.Random())
            drawing.matrix = matrix_txt
            blueprint = drawing.render(exit_c, use_colors=False)
            try:
                with open("maze_blueprint.txt", "w") as f:
                    f.write(blueprint)
                    print("[BONUS] Blueprint saved as maze_blueprint.txt")
            except PermissionError:
                print("Error: Permission denied writing 'maze_blueprint.txt'.")

        elif choice == "5":
            show_steps = not show_steps
            handle_display_flow(out_file, width, height, entry, exit_c,
                                perfect, show_solution, seed_msg, c_wall,
                                c_pattern, show_steps)

        elif choice == "6":
            any_changes, current_theme = handle_parameter_modification(
                content, themes, current_theme
            )

            if any_changes:
                (width, height, entry, exit_c, out_file, perfect,
                 seed_v, _, _) = validate(content)

                c_wall, c_pattern = themes[current_theme]
                seed_msg = handle_generation_flow(width, height, entry, exit_c,
                                                  out_file, perfect, seed_v)
                handle_display_flow(out_file, width, height, entry, exit_c,
                                    perfect, show_solution, seed_msg,
                                    c_wall, c_pattern, show_steps)

        elif choice == "7":
            print("Goodbye!")
            break

        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()

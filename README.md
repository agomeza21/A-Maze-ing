*This project has been created as part of the 42 curriculum by agomez-a, jcamarer.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator and solver written in Python 3.10+. Given a configuration file, the program randomly generates a maze, saves it to a text file in hexadecimal wall encoding, and renders it visually in the terminal with an interactive menu.

Key features:

- Perfect maze generation (exactly one path between any two cells) or imperfect (multiple paths, loops).
- The number **42** is always drawn in the centre of the maze using fully walled cells.
- Shortest path solver displayed as an ASCII overlay with directional arrows.
- Nine built-in colour themes for walls and the 42 pattern, plus custom colours via the config file.
- Reproducible generation via an optional seed.
- `MazeGenerator` and `MazeSolver` packaged as the reusable `mazegen` library, installable with `pip`.

---

## Instructions

### Requirements

- Python 3.10 or later
- `pip`, `build`, `flake8`, `mypy` (installed automatically with `make install`)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd <repo-folder>

# (Recommended) Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies and build the mazegen package
make install
```

### Running the program

```bash
make run

# or explicitly:
python3 a_maze_ing.py config.txt
```

### Other Makefile targets

| Command | Description |
|---|---|
| `make install` | Installs `build`, `flake8`, `mypy` and builds the `mazegen` package |
| `make run` | Runs the program with the default `config.txt` |
| `make debug` | Runs the program under `pdb` for step-by-step debugging |
| `make clean` | Removes `__pycache__`, `.mypy_cache`, `dist/`, `build/` |
| `make lint` | Runs `flake8` and `mypy` with the mandatory flags |
| `make lint-strict` | Runs `flake8` and `mypy --strict` |

### Interactive menu

Once the maze is displayed, the menu offers:

1. **Re-generate and save maze** — generates a new random maze and overwrites the output file.
2. **Show/Hide solution** — toggles the shortest path overlay on the maze.
3. **Change wall colours** — cycles through nine built-in colour themes.
4. **Save maze as drawing** — saves a colour-free ASCII rendering to `maze_blueprint.txt`.
5. **Clue: Show/Hide path steps** — shows step numbers along the solution path.
6. **Modify parameters / Reset config** — changes any config key at runtime without restarting.
7. **Exit** — quits the program.

---

## Configuration file

The configuration file must contain one `KEY=VALUE` pair per line. Lines starting with `#` are treated as comments and ignored.

### Mandatory keys

| Key | Description | Example |
|---|---|---|
| `WIDTH` | Maze width in cells (5–52) | `WIDTH=20` |
| `HEIGHT` | Maze height in cells (5–20) | `HEIGHT=15` |
| `ENTRY` | Entry cell coordinates as `x,y` | `ENTRY=0,0` |
| `EXIT` | Exit cell coordinates as `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | Output filename (must end in `.txt`) | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Whether the maze is perfect (`True`/`False`) | `PERFECT=True` |

### Optional keys

| Key | Description | Example |
|---|---|---|
| `SEED` | Integer seed for reproducible generation | `SEED=42` |
| `COLOR_WALL` | ANSI 256-colour index (0–255) for walls | `COLOR_WALL=46` |
| `COLOR_PATTERN` | ANSI 256-colour index (0–255) for the 42 pattern | `COLOR_PATTERN=196` |

### Notes

- Coordinates are expressed as `x,y` (column, row), both zero-indexed from the top-left.
- `ENTRY` and `EXIT` must be different cells and must lie within the maze bounds.
- Neither `ENTRY` nor `EXIT` may be placed inside the central 42 pattern area.
- If `SEED` is omitted, a random seed is generated and printed to the console.
- When `COLOR_WALL` or `COLOR_PATTERN` are set, they override theme slot 0 (the default theme).

### Default `config.txt`

```
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

---

## Output file format

The program writes a text file where each cell is encoded as a single hexadecimal digit. Each bit of the digit indicates whether a wall is **closed** (1) or open (0):

| Bit | Direction |
|---|---|
| 0 | North |
| 1 | East |
| 2 | South |
| 3 | West |

Cells are written row by row, one row per line. After an empty line, three additional lines are appended:

1. Entry coordinates (`x,y`)
2. Exit coordinates (`x,y`)
3. Shortest path from entry to exit using the letters `N`, `E`, `S`, `W`

All lines end with `\n`.

Example:

```
9F1C3A...
...
1,1
19,14
SSEENEESSWW...
```

---

## Maze generation algorithm

The project uses a **randomised iterative backtracker** (also known as recursive backtracker or depth-first search with backtracking).

### How it works

1. Start at the entry cell and mark it as visited. Push it onto a stack.
2. While the stack is not empty:
   - Look at the current cell. Collect all unvisited neighbours.
   - If at least one unvisited neighbour exists, pick one at random, remove the wall between the current cell and the chosen neighbour, mark the neighbour as visited, and push it onto the stack.
   - If no unvisited neighbour exists, pop the current cell from the stack and backtrack to the previous one.

This produces a **perfect maze** by default. When `PERFECT=False`, an additional pass removes extra walls in regions away from the 42 pattern to create loops and alternate paths.

### Why this algorithm

The iterative backtracker was chosen for several reasons:

- It generates mazes with **long, winding corridors** that feel challenging and natural to navigate.
- It is straightforward to implement iteratively (avoiding Python recursion-depth limits for large mazes).
- It guarantees **full connectivity** in a single pass, making it easy to verify correctness.
- Controlling visited cells as a simple boolean grid is very memory-efficient.
- It is easy to extend: imperfect mazes are produced by a post-processing step without touching the core algorithm.

---

## Reusable Module Documentation (`mazegen`)

The core maze logic is fully encapsulated within the `mazegen` package. Below is the
technical specification demonstrating how to integrate and reuse the module, using exact
code snippets extracted from our main program (`a_maze_ing.py`).

### 1. Instantiate the generator and pass custom parameters

To use the generator, import it, initialise a random engine with your desired seed, and
pass the custom parameters (`width`, `height`, `entry`, `rng`) to the `MazeGenerator`
class.

Here is how we do it in our `handle_generation_flow` function:

```python
# Extracted from: handle_generation_flow() in a_maze_ing.py
maze_rng = random.Random(current_seed)
generator = MazeGenerator(width, height, entry, rng=maze_rng)

omission_msg = generator.apply_42()  # stamps the 42 pattern; returns an error message if the maze is too small
if omission_msg:
    print(omission_msg)

generator.generate()

if not perfect:
    generator.apply_imperfection()  # removes extra walls to create loops
```

### 2. Access the generated structure and compute a solution

Once `generate()` has run, the raw maze structure is accessible via `generator.matrix`
(a `list[list[int]]` where each integer encodes the walls of one cell as a bitmask).
To find the shortest path, pass the matrix to `MazeSolver` and call `solve()`.

Here is the exact implementation from our `handle_generation_flow` function:

```python
# Extracted from: handle_generation_flow() in a_maze_ing.py
solver = MazeSolver(generator.matrix, entry, exit_c, perfect=perfect)
solution = solver.solve()  # returns a list of (row, col) tuples

letters = generator.get_letters(solution)  # e.g. "SSEENEESSWW..."
hex_data = generator.format_as_hex()       # hex string ready for the output file
```

---

## Team and project management

### Roles

Both team members contributed equally to all parts of the project, from the generation
algorithm to the interactive menu, error handling, packaging, and documentation.

### Planning

The project started on May 28th and was developed gradually, tackling one feature at a
time: first the generation algorithm, then the solver, then the visual layer, and finally
packaging and documentation.

### What worked well

The algorithmic side came naturally to both of us. Implementing the backtracker, the
solver, and the 42 pattern required little iteration and produced correct results early on.

### What could be improved

Error handling was by far the most time-consuming part. Making the program robust
against every possible invalid input — bad config format, out-of-bounds coordinates,
wrong types, file permission errors — took significantly more effort than anticipated.

### Tools used

- **Python 3.10** — language
- **VS Code** — editor
- **Git** (feature branches) — version control
- **flake8** — style linter
- **mypy** — static type checker
- **pdb** — debugger (`make debug`)

---

## Resources

### Maze generation

- [Wikipedia — Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Wikipedia — Spanning tree](https://en.wikipedia.org/wiki/Spanning_tree)

### Python packaging

- [Python Packaging User Guide](https://packaging.python.org/en/latest/)
- [pyproject.toml reference](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### AI usage

Claude and Gemini was used for the following tasks:

- **README structure and drafting**: generating an initial outline and filling in sections based on our notes, then reviewed and corrected by both team members.
- **Docstring templates**: providing PEP 257 / Google-style docstring skeletons for functions, which were then filled in with project-specific content.
- **Edge case discussion**: discussing potential issues with the bitmask encoding (wall coherence between adjacent cells) and the behaviour of the solver on imperfect mazes.

Claude was not used to write core logic (generation algorithm, solver, rendering). All AI-generated content was verified, understood, and revised by the team before inclusion in the project.
import sys


def main() -> None:
    file = "config.txt"
    content = {}
    try:
        with open(file, "r") as f:
            for line in f:
                striped_line = line.strip()
                if striped_line:
                    key, value = striped_line.split("=")
                    content[key] = value
            width = int(content["WIDTH"])       # ANCHO
            height = int(content["HEIGHT"])     # ALTO
            matriz = [[15 for _ in range(width)] for _ in range(height)]
    except FileNotFoundError:
        print(f"Error: configuration file '{file}' not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()



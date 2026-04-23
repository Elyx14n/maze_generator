from .constants import Config, Tuple, Grid


def in_bounds(row: int, col: int, rows: int, cols: int):
    return 0 <= col < cols and 0 <= row < rows


def parse_config(filepath: str) -> Config:
    """parse and validate config file"""
    data = {}

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()

                # skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                if "=" not in line:
                    raise ValueError(f"Invalid line: {line}")

                key, value = line.split("=", 1)
                data[key.strip()] = value.strip()

    except FileNotFoundError:
        raise ValueError(f"Config file not found: {filepath}")

    # requirements
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    for key in required:
        if key not in data:
            raise ValueError(f"Missing required key: {key}")

    # parsing
    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])

        parts = data["ENTRY"].split(",")
        if len(parts) != 2:
            raise ValueError("Invalid ENTRY format")
        ex, ey = map(int, parts)
        entry = (ex, ey)

        parts = data["EXIT"].split(",")
        if len(parts) != 2:
            raise ValueError("Invalid EXIT format")
        tx, ty = map(int, parts)
        exit_ = (tx, ty)

        output_file = data["OUTPUT_FILE"]

        perfect = data["PERFECT"].lower() == "true"

    except ValueError as e:
        raise ValueError(f"Invalid config values: {e}")

    # validation
    if width <= 0 or height <= 0:
        raise ValueError("WIDTH and HEIGHT must be positive")

    if entry == exit_:
        raise ValueError("ENTRY and EXIT cannot be the same")

    for x, y in [entry, exit_]:
        if not in_bounds(y, x, height, width):
            raise ValueError(f"Point {(x, y)} is out of bounds")

    return Config(width, height, entry, exit_, output_file, perfect)

def write_maze(
        filename: str,
        grid: Grid,
        entry: Tuple[int, int],
        exit: Tuple[int, int],
        path: str,
        ) -> None:
    try:
        with open(filename, "w", encoding="utf-8") as f:
            for row in grid:
                f.write("".join(format(cell.walls, "X") for cell in row) + "\n")
            f.write("\n")
            f.write(f"{entry[0]},{entry[1]}\n")
            f.write(f"{exit[0]},{exit[1]}\n")
            f.write(path + "\n")
    except Exception as e:
        raise RuntimeError(f"Failed to write maze file: {e}") from e
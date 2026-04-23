import sys
from mazegen.utils import parse_config
from mazegen.maze import Maze
from mazegen.renderer import render_maze
from mazegen.utils import write_maze
from mazegen.constants import Colors


def main() -> None:
    try:
        if len(sys.argv) > 3:
            raise ValueError(
                "Usage: python a_maze_ing.py [config_file] [seed— Optional]")

        config_file = (
            sys.argv[1]
            if len(sys.argv) == 2
            else "default_config.txt"
        )
        config = parse_config(config_file)
        seed = int(sys.argv[2]) if len(sys.argv) == 3 else None
        if seed is not None:
            config.seed = seed

        m = Maze(config)
        m.generate()
        write_maze(config.output_file, m.grid, config.entry, config.exit, m.path)
        show_path = True
        color = Colors.WHITE

        while True:
            render_maze(m.grid, color, show_path)
            print("\nSolution (N/E/S/W):")
            print(m.path)
            print("\n[r] regenerate  [p] toggle path  [c] colour  [q] quit")
            cmd = input("> ").strip().lower()

            if cmd == "q":
                break

            elif cmd == "r":
                m.reset()
                m.generate()
                write_maze(config.output_file, m.grid, config.entry, config.exit, m.path)

            elif cmd == "p":
                show_path = not show_path

            elif cmd == "c":
                colors = list(Colors)
                color = colors[(colors.index(color) + 1) % len(colors)]
                print(f"Colour mode: {color}")

            else:
                print("Unknown command")

    except ValueError as e:
        print("Error:", e)


if __name__ == "__main__":
    main()

from .constants import Grid, Colors, S, E


def render_maze(grid: Grid, color: Colors = Colors.WHITE, show_path: bool = True) -> None:
    h, w = len(grid), len(grid[0])
    reset = Colors.WHITE.value
    
    print(f"{color.value}+{'---+' * w}{reset}")

    for row in range(h):
        line1 = "|"
        line2 = "+"
        for col in range(w):
            cell = grid[row][col]
            if cell.is_42:
                line1 += f"{Colors.GREEN.value}███{reset}"
            elif cell.is_path and show_path:
                line1 += f"{Colors.YELLOW.value}🐾 {reset}"
            else:
                line1 += "   "

            if cell.walls & E:
                line1 += f"{color.value}|{reset}"
            else:
                line1 += " "
            if cell.walls & S:
                line2 += f"{color.value}---+{reset}"
            else:
                line2 += f"{color.value}   +{reset}"

        print(f"{color.value}" + line1)
        print(f"{color.value}" + line2)

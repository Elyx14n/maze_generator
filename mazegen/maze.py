import random
from collections import deque
from typing import List, Tuple, Dict
from .constants import Config, Grid, Cell, FORTY_TWO, N, S, E, W
from .utils import in_bounds

DIR_CHAR = {N: "N", E: "E", S: "S", W: "W"}
CHAR_DIR = {v: k for k, v in DIR_CHAR.items()}

DC = {E: 1, W: -1, N: 0, S: 0}
DR = {E: 0, W: 0, N: -1, S: 1}
OPPOSITE = {N: S, S: N, E: W, W: E}


class Maze:
    def __init__(self, config: Config) -> None:
        self.cols = config.width
        self.rows = config.height
        self.random = random.Random(config.seed)
        self.perfect = config.perfect
        self.grid: Grid = [
            [Cell(row=row, col=col) for col in range(self.cols)]
            for row in range(self.rows)
        ]
        self.entry_col, self.entry_row = config.entry
        self.exit_col, self.exit_row = config.exit
        self.path: str = ""

    def generate(self) -> None:
        while True:
            self._apply_42()
            self._dfs()
            if not self.perfect:
                self._add_loops()
            if not self._solve():
                self.reset()
                continue
            break

    def reset(self) -> None:
        self.grid: Grid = [
            [Cell(row=row, col=col) for col in range(self.cols)]
            for row in range(self.rows)
        ]
        self.path = ""

    def _apply_42(self) -> None:
        if self.cols < 12 or self.rows < 7:
            raise ValueError("Maze too small for 42 pattern")

        cx = self.cols // 2 - 4
        cy = self.rows // 2 - 2

        for dx, dy in FORTY_TWO:
            col, row = cx + dx, cy + dy
            if in_bounds(row, col, self.rows, self.cols):
                self.grid[row][col].is_42 = True

        if self.grid[self.entry_row][self.entry_col].is_42:
            raise ValueError("Entry point overlaps the 42 pattern")
        if self.grid[self.exit_row][self.exit_col].is_42:
            raise ValueError("Exit point overlaps the 42 pattern")

    def _dfs(self) -> None:
        visited = [[False] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col].is_42:
                    visited[row][col] = True

        non_42 = [cell for row in self.grid for cell in row if not cell.is_42]
        start = self.random.choice(non_42)
        stack: List[Cell] = [start]
        visited[start.row][start.col] = True

        while stack:
            curr = stack[-1]
            valid = []
            for d in [N, E, S, W]:
                nr, nc = curr.row + DR[d], curr.col + DC[d]
                if in_bounds(nr, nc, self.rows, self.cols) and not visited[nr][nc]:
                    valid.append(d)

            if not valid:
                stack.pop()
                continue

            self.random.shuffle(valid)
            d = valid[0]
            nr, nc = curr.row + DR[d], curr.col + DC[d]

            curr.walls &= ~d
            self.grid[nr][nc].walls &= ~OPPOSITE[d]

            visited[nr][nc] = True
            stack.append(self.grid[nr][nc])

    def _add_loops(self) -> None:
        ratio = min(0.5, 2.0 / (self.rows * self.cols) ** 0.5)
        candidates = []
        for row in range(self.rows):
            for col in range(self.cols):
                cell = self.grid[row][col]
                if cell.is_42:
                    continue
                for d in [E, S]:
                    nr, nc = row + DR[d], col + DC[d]
                    if in_bounds(nr, nc, self.rows, self.cols) and not self.grid[nr][nc].is_42:
                        if cell.walls & d:
                            candidates.append((row, col, d))

        self.random.shuffle(candidates)
        count = max(1, int(len(candidates) * ratio))
        for row, col, d in candidates[:count]:
            nr, nc = row + DR[d], col + DC[d]
            self.grid[row][col].walls &= ~d
            self.grid[nr][nc].walls &= ~OPPOSITE[d]

    def _solve(self) -> bool:
        start = (self.entry_row, self.entry_col)
        queue = deque([start])
        visited = {start}
        parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], int]] = {}

        while queue:
            row, col = queue.popleft()
            if (row, col) == (self.exit_row, self.exit_col):
                path = []
                curr = (self.exit_row, self.exit_col)
                while curr != start:
                    prev, d = parent[curr]
                    path.append(DIR_CHAR[d])
                    curr = prev
                self.path = "".join(reversed(path))
                r, c = self.entry_row, self.entry_col
                self.grid[r][c].is_path = True
                for ch in self.path:
                    d = CHAR_DIR[ch]
                    r, c = r + DR[d], c + DC[d]
                    self.grid[r][c].is_path = True
                return True

            for d in [N, E, S, W]:
                if not (self.grid[row][col].walls & d):
                    nr, nc = row + DR[d], col + DC[d]
                    if in_bounds(nr, nc, self.rows, self.cols) and (nr, nc) not in visited and not self.grid[nr][nc].is_42:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        parent[(nr, nc)] = ((row, col), d)

        return False

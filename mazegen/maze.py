import random
from collections import deque
from typing import List, Tuple, Dict
from .constants import Config, Grid, Cell, FORTY_TWO, N, S, E, W
from .utils import in_bounds

DIR_CHAR = {N: "N", E: "E", S: "S", W: "W"}
DX_CHAR = {"E": 1, "W": -1, "N": 0, "S": 0}
DY_CHAR = {"E": 0, "W": 0, "N": -1, "S": 1}

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
            if self.grid[self.entry_row][self.entry_col].is_42 or self.grid[self.exit_row][self.exit_col].is_42:
                self.reset()
                continue
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

    def _dfs(self) -> None:
        visited = [[False] * self.cols for _ in range(self.rows)]
        for row in range(self.rows):
            for col in range(self.cols):
                if self.grid[row][col].is_42:
                    visited[row][col] = True

        stack: List[Cell] = []

        start = self.grid[self.random.randrange(
            self.rows)][self.random.randrange(self.cols)]
        while start.is_42:
            start = self.grid[self.random.randrange(
                self.rows)][self.random.randrange(self.cols)]
        stack.append(start)
        visited[start.row][start.col] = True

        while (stack):
            curr = stack[-1]
            dirs = [N, E, S, W]
            valid = []
            for d in dirs:
                nr = curr.row + DR[d]
                nc = curr.col + DC[d]
                if in_bounds(nr, nc, self.rows, self.cols) and not visited[nr][nc]:
                    valid.append(d)

            if not valid:
                stack.pop()
                continue

            self.random.shuffle(valid)
            d = valid[0]
            nr = curr.row + DR[d]
            nc = curr.col + DC[d]

            # carve walls between curr and neighbor
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
        start = (self.grid[self.entry_row][self.entry_col].row,
                 self.grid[self.entry_row][self.entry_col].col)
        queue = deque([start])
        visited = set([start])
        parent: Dict[Tuple[int, int], Tuple[Tuple[int, int], int]] = {}

        found = False
        while queue:
            row, col = queue.popleft()
            if (row, col) == (self.exit_row, self.exit_col):
                found = True
                break

            for d in [N, E, S, W]:
                if not (self.grid[row][col].walls & d):
                    nr = row + DR[d]
                    nc = col + DC[d]
                    if in_bounds(nr, nc, self.rows, self.cols) and (nr, nc) not in visited and not self.grid[nr][nc].is_42:
                        visited.add((nr, nc))
                        queue.append((nr, nc))
                        parent[(nr, nc)] = ((row, col), d)

        if not found:
            return False

        path = []
        curr = (self.exit_row, self.exit_col)

        while curr != start:
            prev, d = parent[curr]
            path.append(DIR_CHAR[d])
            curr = prev

        self.path = "".join(reversed(path))
        r, c = self.entry_row, self.entry_col
        self.grid[r][c].is_path = True
        for dir in self.path:
            r += DY_CHAR[dir]
            c += DX_CHAR[dir]
            self.grid[r][c].is_path = True

        return True

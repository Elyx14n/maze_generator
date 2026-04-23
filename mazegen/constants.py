from typing import List, Tuple
from enum import Enum
from dataclasses import dataclass

N, E, S, W = 1, 2, 4, 8

FORTY_TWO = [
    # 4
    (0, 0), (0, 1), (0, 2),
    (1, 2),
    (2, 0), (2, 1), (2, 2), (2, 3),
    (2, 4),

    # 2
    (4, 0), (5, 0), (6, 0),
    (6, 1),
    (5, 2),
    (4, 3),
    (4, 4), (5, 4), (6, 4),
]

class Colors(Enum):
    WHITE = "\033[0m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[33m"


@dataclass
class Cell():
    col: int
    row: int
    is_42: bool = False
    is_path: bool = False
    walls: int = N | E | S | W


@dataclass
class Config:
    width: int
    height: int
    entry: Tuple[int, int]
    exit: Tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


Grid = List[List[Cell]]

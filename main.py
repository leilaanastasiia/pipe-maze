from collections import deque
from typing import List, Tuple, Dict, Set


class PipeMaze:
    """
    Solves a pipe maze puzzle.

    Flow:
    1. Find start of the puzzle.
    2. Search for the valid connections of the starting point.
    3. Determine the shape of the starting pipe.
    4. Calculate the farthest distance along the loop from the start.
    5. Count the enclosed tiles within the loop.
    6. Print clear main loop.
    """

    # grid[row][column]
    DIRS: Dict[str, Tuple[int, int]] = {
        "N": (-1, 0),  # ↑
        "S": (1, 0),   # ↓
        "W": (0, -1),  # ←
        "E": (0, 1),   # →
    }

    OPPOSITE: Dict[str, str] = {
        "N": "S",
        "S": "N",
        "W": "E",
        "E": "W",
    }

    # the pipes are arranged in a two-dimensional grid of tiles
    CONNECTIONS: Dict[str, Set[str]] = {
        "|": {"N", "S"},
        "-": {"E", "W"},
        "L": {"N", "E"},
        "J": {"N", "W"},
        "7": {"S", "W"},
        "F": {"S", "E"},
        ".": set(),
    }

    # 3x3 grid
    EXPANDED_PATTERN: Dict[str, List[Tuple[int, int]]] = {
        "|": [(0, 1), (1, 1), (2, 1)],
        "-": [(1, 0), (1, 1), (1, 2)],
        "L": [(0, 1), (1, 1), (1, 2)],  # N, E
        "J": [(0, 1), (1, 1), (1, 0)],  # N, W
        "7": [(1, 0), (1, 1), (2, 1)],  # S, W
        "F": [(1, 2), (1, 1), (2, 1)],  # S, E
    }

    RED = "\033[91m"
    RESET = "\033[0m"

    def __init__(self, grid: List[str]) -> None:
        self.grid = grid
        self.rows = len(grid)
        self.cols = len(grid[0]) if grid else 0
        self.start = self._find_start()
        self.start_dirs = self._find_start_connections()
        self.start_pipe = self._detect_start_pipe()

    def _find_start(self) -> Tuple[int, int]:
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == "S":
                    return r, c
        raise ValueError("No start point was found")

    def _find_start_connections(self) -> Set[str]:
        """
        Searches for 2 valid connections of the starting point.
        """
        sr, sc = self.start
        result = set()

        for direction, (dr, dc) in self.DIRS.items():
            nr, nc = sr + dr, sc + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                neighbor = self.grid[nr][nc]
                if self.OPPOSITE[direction] in self.CONNECTIONS.get(neighbor, set()):
                    result.add(direction)

        if len(result) != 2:
            raise ValueError(f"Starting point has to have exactly 2 connections, but found {len(result)}: {result}")

        return result

    def _detect_start_pipe(self) -> str:
        for pipe, dirs in self.CONNECTIONS.items():
            if dirs == self.start_dirs:
                return pipe
        raise ValueError("Unable to determine the shape of the pipe for the starting point.")

    def _get_dirs(self, r: int, c: int) -> Set[str]:
        ch = self.grid[r][c]
        return self.start_dirs if ch == "S" else self.CONNECTIONS.get(ch, set())

    def neighbors(self, r: int, c: int) -> List[Tuple[int, int]]:
        """
        Returns only those neighbors that have a correct connection.
        """
        result = []

        for direction in self._get_dirs(r, c):
            dr, dc = self.DIRS[direction]
            nr, nc = r + dr, c + dc

            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if self.OPPOSITE[direction] in self._get_dirs(nr, nc):
                    result.append((nr, nc))

        return result

    def find_main_loop(self) -> Dict[Tuple[int, int], int]:
        """
        Breadth-first search of the distance for the main loop.
        """
        distance: Dict[Tuple[int, int], int] = {self.start: 0}
        queue = deque([self.start])

        while queue:
            r, c = queue.popleft() # bfs

            for nr, nc in self.neighbors(r, c):
                if (nr, nc) not in distance:
                    distance[(nr, nc)] = distance[(r, c)] + 1
                    queue.append((nr, nc))

        return distance

    def farthest_distance(self) -> int:
        distance = self.find_main_loop()
        return max(distance.values())

    def enclosed_tiles(self) -> int:
        loop_cells = set(self.find_main_loop().keys())
        inside_count = 0

        for r in range(self.rows):
            inside = False
            pending_corner = None

            for c in range(self.cols):
                if (r, c) in loop_cells:
                    item = self.grid[r][c]

                    if item == "S":
                        item = self.start_pipe

                    if item == "|":
                        inside = not inside

                    # start of a corner
                    elif item in "FL":
                        pending_corner = item

                    # end of a corner
                    elif item in "J7":
                        if pending_corner:
                            pair = pending_corner + item

                            if pair in ("FJ", "L7"): # └...┐ and ┌...┘
                                inside = not inside

                        pending_corner = None

                else:
                    if inside:
                        inside_count += 1

        return inside_count


    def print_clean_loop(self) -> None:
        pretty_map = {
            "|": "│",
            "-": "─",
            "L": "└",
            "J": "┘",
            "7": "┐",
            "F": "┌",
        }

        loop_cells = set(self.find_main_loop().keys())

        for r in range(self.rows):
            line = []
            for c in range(self.cols):
                if (r, c) not in loop_cells:
                    line.append(" ")
                    continue

                if (r, c) == self.start:
                    line.append(f"{self.RED}S{self.RESET}")  # reset color to default
                    continue

                item = self.grid[r][c]
                line.append(pretty_map.get(item, item))

            print("".join(line))


def solve(data: str) -> Tuple[int, int]:
    grid = [line.rstrip("\n") for line in data.splitlines() if line.strip()]
    maze = PipeMaze(grid)

    print(f"Farthest distance: {maze.farthest_distance()}")
    print(f"Enclosed tiles: {maze.enclosed_tiles()}\n")

    print("Main Loop:")
    maze.print_clean_loop()



if __name__ == "__main__":
    with open("puzzle_input.txt", "r", encoding="utf-8") as f:
        data = f.read()

    solve(data)

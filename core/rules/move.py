# @api: A* pathfinder; pure function returns path (including start and goal)
from heapq import heappush, heappop
from typing import Iterable, Tuple, Optional, Dict, List
from ..state import GameState

Pos = Tuple[int,int]

def neighbors4(p: Pos) -> Iterable[Pos]:
    x,y = p
    yield x+1,y; yield x-1,y; yield x,y+1; yield x,y-1

def terrain_cost(s: GameState, p: Pos) -> int:
    t = s.map.tile(p)
    return t.move_cost  # v1; include elevation penalty inside tile if you prefer

def heuristic(a: Pos, b: Pos) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def a_star(s: GameState, start: Pos, goal: Pos, max_cost: int) -> Optional[List[Pos]]:
    open_: List[Tuple[int, Pos]] = []
    heappush(open_, (0, start))
    came_from: Dict[Pos, Optional[Pos]] = {start: None}
    g: Dict[Pos, int] = {start: 0}

    while open_:
        _, cur = heappop(open_)
        if cur == goal: break
        for nxt in neighbors4(cur):
            if not s.map.in_bounds(nxt) or s.map.blocked(nxt): 
                continue
            new_g = g[cur] + terrain_cost(s, nxt)
            if new_g > max_cost: 
                continue
            if nxt not in g or new_g < g[nxt]:
                g[nxt] = new_g
                came_from[nxt] = cur
                f = new_g + heuristic(nxt, goal)
                heappush(open_, (f, nxt))
    if goal not in came_from: 
        return None
    # reconstruct
    path: List[Pos] = []
    current: Optional[Pos] = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

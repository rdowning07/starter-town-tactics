import random

class Rng:
    def __init__(self, seed: int) -> None:
        self._r = random.Random(seed)
    
    def randint(self, a: int, b: int) -> int:
        return self._r.randint(a, b)

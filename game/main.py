# game/main.py

"""Main entry point to run a sample game session."""

from game.game import Game
from game.unit import Unit

def main():
    game = Game(5, 5)

    # Add a hero unit
    hero = Unit("Hero", 2, 2, team="Red")
    game.add_unit(hero)

    # Optionally add more units
    enemy = Unit("Goblin", 1, 1, team="Blue")
    game.add_unit(enemy)

    # Print the initial game state
    game.print_state()

    # Advance a turn and reprint state
    game.next_turn()
    print(f"\nTurn: {game.current_turn}")
    game.print_state()

if __name__ == "__main__":
    main()

# Emberward Clone (Pathfinding Algorithm Visualizer)

A tower defense game with a twist, inspired by Emberward. This project emphasizes dynamic pathfinding by challenging the player to build a maze for enemies using Tetris-like pieces. You can switch between different pathfinding algorithms (A*, Dijkstra, Greedy BFS, DFS) in real-time to see how they affect the enemies' routes.

## Gameplay

The core gameplay loop combines maze-building and tower defense with roguelite progression.

1. **Build Your Maze**: Before and during waves, place Tetris-shaped pieces on the grid to create a long, winding path for enemies. The path from the enemy spawn to your core is always visible.
2. **Place Towers**: Build towers on the pieces you've placed. Each tower has unique stats for damage, range, and fire rate.
3. **Defend the Core**: Click "Start Wave" and watch your defenses hold off incoming enemies. Earn gold for each enemy defeated.
4. **Progress**: Survive all waves to win the level. You'll return to a map screen where you can choose your next battle, carrying over your core HP. If your core's HP drops to zero, the run ends.

## Controls

### General

- **Pan Camera**: Hold `Right Mouse Button` and drag.
- **Zoom Camera**: Use the `Mouse Wheel` or `+` / `-` keys.
- **Return to Map**: Press `Escape` during a fight.
- **Switch Pathfinding Algorithm**: Press `TAB` to cycle through A*, Dijkstra, etc.

### Placement

- **Toggle Piece Placement**: Press `P`.
- **Toggle Tower Placement**: Press `T`.
- **Rotate Piece**: Press `Q` (counter-clockwise) or `E` (clockwise).
- **Select Tower Type**: Press `1`, `2`, or `3`.
- **Place / Select**: `Left-click` to place a piece/tower or to select an existing tower to view its stats and sell it.

## Features

- **Dynamic Pathfinding**: Enemies constantly recalculate their path to your core as you build your maze. Switch between four different algorithms on the fly:
  - **A***: An intelligent, efficient search that balances path length and distance to the goal.
  - **Dijkstra**: Finds the absolute shortest path, but explores more nodes than A*.
  - **Greedy Best-First**: A "shortsighted" algorithm that always moves to the node closest to the goal, which may not be the optimal path.
  - **DFS**: A simple depth-first search that finds a path, but often a very inefficient one.
- **Tetris-like Maze Building**: Use a deck of familiar puzzle pieces to construct your defenses. You can't block the path completely!
- **Multiple Tower Types**: Deploy different towers, each with its own cost, damage, range, and fire rate.
- **Wave-Based Survival**: Face increasingly challenging waves of enemies with varying stats.
- **Roguelite Progression**: Move between level on a map, with your core HP persisting between fights. Each level provides a set amount of gold for the battle.
- **Interactive UI**: A clean sidebar provides all necessary information, including gold, core HP, wave status, and tower selection.

## How to Run

1. **Install Dependencies**: Make sure you have Python and Pygame installed.

    ```sh
    pip install pygame
    ```

2. **Run the Game**: Execute the `main.py` file.

    ```sh
    python main.py
    ```

## Developer Notes

- **Performance**: Pathfinding is a critical component. A* is re-calculated for enemies only when their path is obstructed by a newly placed piece.
- **Game Data**: Enemy waves, tower stats, and piece shapes are all defined in easy-to-edit `.json` files in the `data/` directory.

## Future Ideas

- Tower upgrades for damage, range, and special effects.
- More enemy types (e.g., flying, armored, fast).
- Special map levels with unique challenges or rewards.
- Visual effects for projectiles, impacts, and enemy deaths.
- Sound effects and music.

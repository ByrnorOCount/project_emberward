# Emberward clone that highlights A* search

## Flow recap

Start Menu → click Play → calls start_new_run() → goes to Map Screen
Map Screen → player chooses next node → loads fight map via load_map_layout()
Fight Map → spawn waves → player places pieces/towers, defends core → on victory → return to Map Screen
Core HP persists → losing all HP ends run → back to Start Menu

## Flow pt 2

### Core Game Flow

Start Menu
 Title display
 Play button → starts a new run
 Options button → placeholder menu for now
 Quit button → exits the game

Roguelite Map Screen
 Procedural or predefined node map with branching paths
 Node selection with different rewards (gold, upgrades, map layouts)
 Show player progress and upcoming path

Run State Management
 Persistent core HP across fights
 Player gold carries between fights
 Track cleared nodes, current node, next node choices

### Fight / Tower Defense Phase

Map & Obstacles
 Load fixed obstacles layout for each map
 Distinguish unplaceable terrain vs. player-placed tetris pieces
 Core in center with HP visible
 Multiple enemy spawn points at map edges

Player Actions
 Place tetris pieces before/during wave to shape paths
 Place towers on top of player-placed tetris pieces
 Upgrade towers (cost scaling, stats improvement)
 Gold income from killing enemies
 Zoom/pan controls for large maps

### Enemies

Enemy attributes: HP, speed, gold reward
Enemy pathfinding with A* that updates when player places blocks
Waves system with scaling difficulty
Multiple enemy types (fast, tanky, etc.)

### Towers

Tower attributes: cost, damage, range, fire rate, gimmick (e.g., splash, slow)
Targeting logic (closest, first, strongest)
Projectile handling (optional or instant hit)
Upgrade system for damage/range/special effects

### UI & Rendering

Info bars: core HP, gold, wave, upcoming enemies
Tetris piece preview when placing
Tower range indicator when placing
Dashed path lines with arrowheads for enemy routes
Sidebar for wave start, pause, etc.

### Game Systems

Game states: MENU → MAP → FIGHT → MAP → WIN/LOSS
Gold economy balancing
Difficulty scaling across nodes
Victory/loss conditions → back to menu

## Performance tips & scaling

Recompute only when necessary. Cache each enemy's path and only recalc if obstructed or if placed block intersects the path.
Spread A\* work across frames: run at most M pathfinds per frame using a queue.
For big maps, consider hierarchical pathfinding or jump point search later.
Use integer grid coords for A* to keep it fast.

## Extras that could be added later

Conveyor obstacles (special obstacle cell type that forces direction) to actively redirect enemies instead of just blocking — would require adding directional edges or movement penalty modifiers.
Enemy formation smoothing: enemy follows path centers but avoid overlapping using simple separation steering.
Tower upgrades, projectile visuals, damage, and range circle.

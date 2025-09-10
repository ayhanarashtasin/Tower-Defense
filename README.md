## Tower Defense Playground (PyOpenGL)

Arcade-style 3D tower defense prototype built with Python, PyOpenGL, and FreeGLUT. Defend your blue side against waves of pink-side enemies using three archer towers, manual shots, a purchasable sweeping wave attack, and spawnable allied troops.

This document explains every feature in detail, how to run the game, controls, tweakable settings, and ways to extend it.

### Quick Start

- **Requirements**:
  - Python 3.8+ (64-bit recommended)
  - PyOpenGL and PyOpenGL-accelerate
  - A GPU/driver capable of running OpenGL 2.1+

- **Install dependencies**:
  ```bash
  pip install PyOpenGL PyOpenGL-accelerate
  ```

- **Run**:
  ```bash
  python Hello_openGL.py
  ```

- The project bundles FreeGLUT DLLs under `OpenGL/DLLS/` (from the PyOpenGL distribution). Running from this folder on Windows should work out-of-the-box.

## Controls

- **Space**: Pause/Resume
- **B**: Start/Resume (clears pause)
- **R**: Restart game
- **Enter**: Proceed to the next wave (after you clear the current wave)
- **C**: Toggle Cheat Mode (auto-fire from all living towers using their own fire rates)
- **A / S / D**: Manually fire from Tower 1 / 2 / 3
- **W**: Trigger the sweeping Wave Attack (cost doubles each use)
- **T**: Spawn allied troops (cost shown in HUD)
- **Arrow Keys**: Move the camera (Left/Right pans X, Up/Down raises/lowers Y)
- **Mouse Left-Click**: Upgrade the nearest tower along the X-axis (spends points)
- **ESC**: Quit, only available after Game Over

## Gameplay Features (Detailed)

### 1) Towers and Upgrades

- You start with three archer towers positioned along the back of the blue side (`z = GRID_LENGTH - 100`), at `x = -300, 0, 300`.
- Each tower has:
  - `health` starting at `TOWER_HEALTH_MAX` (default 100).
  - `level` starting at 1.
  - `fire_interval` starting at `TOWER_BASE_FIRE_INTERVAL` (default 1.2 s).
  - `cooldown` to gate shots.
  - `upgrade_cost` starting at `TOWER_UPGRADE_BASE_COST` (default 50 points), doubling per upgrade.
- **Upgrading a tower** (Left-click on the playfield):
  - Spends points if you have enough.
  - Increases `level` by 1.
  - Reduces `fire_interval` by `TOWER_COOLDOWN_REDUCTION_PER_LEVEL` (10% default), clamped to 0.25 s min.
  - Doubles `upgrade_cost` for the next upgrade.
- **Damage scaling**: Tower level increases bullet damage by `TOWER_DAMAGE_MULT_PER_LEVEL` per level (25% per level by default). Damage is computed when a bullet hits an enemy. The bullet’s “author” is approximated by the nearest living tower to the hit point.

### 2) Manual Shots (Bullets)

- Press `A`, `S`, `D` to fire from Tower 1, 2, or 3 respectively.
- Bullets spawn from the person’s gun barrel on the tower and are initially aimed toward the enemy side (−Z).
- Each bullet:
  - Has homing behavior when a target was locked at fire time; it will steer toward that enemy each frame.
  - Moves at `ARROW_SPEED` (default 320 units/sec), lasts for `ARROW_TTL` seconds (default 4.0), and is rendered as a small GLU sphere.
  - On impact, deals `ARROW_DAMAGE * damageMultiplierFromTowerLevel`.
  - Spawns a brief spark/ring hit effect.
- **Misses**:
  - If a bullet expires or hits a wall/boundary, it counts as a miss.
  - Each miss subtracts `MISSED_BULLET_DAMAGE` (default 0.5) health from the nearest living tower.
  - Misses are tracked in the HUD as “Missed Bullets”.

### 3) Enemies and Types

- Enemies spawn on the pink side (negative Z) each wave. Base models are “bomb-like” characters.
- Base stats scale per wave (see Waves section). Every enemy has `health`, `alive`, `speed_mult`, optional height offset `y`, color, size scale, and hit radius scale.
- Types:
  - **grunt**: baseline enemy; default visuals.
  - **fast**: higher `speed_mult` (`1.6 + wave*0.05`); orange color.
  - **armored**: higher health multiplier (`2.0 + wave*0.15`); gray color.
  - **flying**: moves above ground (`y = 35 + wave*2`), slightly faster (`1.2 + wave*0.04`); purple color.
  - **big**: special heavies starting at certain waves (see below); large size and hit radius, moves slower, very high health.
- Targeting/Movement:
  - Enemies prioritize attacking your allied troops if any are alive; otherwise they path to the nearest tower.
  - Upon contact with a target (troop or tower), they deal `ENEMY_DAMAGE` (default 10).

### 4) Waves and Progression

- The first wave starts automatically.
- After clearing a wave, the game prompts “Press Enter for the next wave”.
- Per wave scaling:
  - Enemy count: `3 + 3*(wave-1)` (adds +3 per wave)
  - Enemy base HP: `10 + 2*(wave-1)` (adds +2 per wave)
- Special “big” enemies:
  - Spawn 2 per wave starting from wave 4, then every 3 waves (4, 7, 10, ...).
  - Health is `9x` the current wave’s base HP.
  - Larger model (`scale_mult = 2.0`) and larger hit radius (`hit_radius_mult = 2.0`), slower (`speed_mult = 0.6`).

### 5) Wave Attack (Sweeping Band)

- Press `W` to launch a sweeping wave attack from your blue back line toward the enemy back line.
- Cost starts at `WAVE_COST_BASE` (default 50 points) and **doubles each time**.
- The wave is visualized as a wide band sweeping across the field.
- Effects on enemies inside the swept region:
  - Normal enemies are instantly killed and award points.
  - “Big” enemies are only chipped for a fraction of their max HP: `max(30, 25% of max)`, possibly requiring multiple waves or follow-up damage to finish.

### 6) Allied Troops (UFO-like Spiked Crafts)

- Press `T` to spawn friendly troops on your blue side. Cost is shown in HUD (`TROOP_SPAWN_COST`, default 30 points).
- Each press spawns more units than the previous press:
  - Count = `TROOP_BASE_COUNT + (presses-1) * TROOP_COUNT_INCREMENT` (defaults: 5, +2 each press)
- Behavior:
  - Troops move toward the nearest enemy. If within `TROOP_ATTACK_RADIUS` they deal DPS (`TROOP_DPS`, default 20) to that enemy.
  - Troops have `TROOP_HEALTH` (default 25) and can be killed by enemies.
  - Enemies target troops first if any are alive.

### 7) Scoring, Costs, and HUD

- You earn `POINTS_PER_KILL` (default 5) per enemy kill.
- Points are spent on Tower Upgrades, Wave Attack, and Troop Spawns.
- HUD shows:
  - Title, sides, wave, points, next wave/wave cost, troop cost, missed bullets, troop count.
  - “CHEAT MODE ON” when cheat mode is active.
  - “PAUSED” when paused.
  - After a wave is cleared, a prompt to press Enter for the next wave.
  - Tower stats panel (per tower): Level, damage multiplier, fire interval, next upgrade cost.
  - “Towers Alive” counter.

### 8) Camera and Viewport

- Perspective: `gluPerspective(fovY=120, aspect=1.25, near=0.1, far=3000)`.
- Camera position starts at `(0, 800, 1000)` looking at origin.
- Arrow keys adjust X and Y for quick framing of the larger field.

### 9) Playground and Walls

- Play area is divided along Z=0:
  - Blue side: `z ∈ [0, +GRID_LENGTH]` rendered with cool gradients.
  - Pink side: `z ∈ [-GRID_LENGTH, 0]` rendered with warm gradients.
- Decorative walls enclose the field, and a center line marks the division.
- Bullets that leave bounds or hit walls are considered misses (sparks appear where they hit).

### 10) Cheat Mode

- Toggle with `C`.
- All living towers auto-fire respecting each tower’s `fire_interval` and own cooldowns.

### 11) Game Over and Restart

- The game ends when all towers are destroyed.
- HUD shows “GAME OVER”, final score, and the highest wave reached.
- Press `R` to restart. `ESC` exits from the Game Over screen.

## Configuration Reference (Edit in `Hello_openGL.py`)

Adjust these constants near the top of the file to tune gameplay:

- **Field/Camera**:
  - `GRID_LENGTH` (default 800): half-length of each side along Z; also sets X extent.
  - `fovY` (default 120): field of view in degrees.
  - `WALL_HEIGHT` (default 90): height of decorative perimeter walls.

- **Towers**:
  - `TOWER_SCALE` (default 1.6): visual scale of tower models.
  - `TOWER_HEALTH_MAX` (default 100)
  - `TOWER_BASE_FIRE_INTERVAL` (default 1.2 s)
  - `TOWER_DAMAGE_MULT_PER_LEVEL` (default 0.25)
  - `TOWER_COOLDOWN_REDUCTION_PER_LEVEL` (default 0.10)
  - `TOWER_UPGRADE_BASE_COST` (default 50)

- **Projectiles**:
  - `ARROW_SPEED` (default 320)
  - `ARROW_TTL` (default 4.0)
  - `ARROW_DAMAGE` (default 10)
  - `ARROW_HIT_RADIUS_3D` (default 40)

- **Enemies**:
  - `ENEMY_SPEED` (default 120)
  - `ENEMY_DAMAGE` (default 10)

- **Waves & Scoring**:
  - `WAVE_COST_BASE` (default 50), doubles after each activation.
  - `POINTS_PER_KILL` (default 5)
  - Big wave chip rules: `BIG_WAVE_DAMAGE_PERCENT` (default 0.25) and `BIG_WAVE_DAMAGE_MIN` (default 30)

- **Miss Penalty**:
  - `MISSED_BULLET_DAMAGE` (default 0.5): health lost by the nearest living tower per miss.

- **Allied Troops**:
  - `TROOP_SPAWN_COST` (default 30)
  - `TROOP_BASE_COUNT` (default 5)
  - `TROOP_COUNT_INCREMENT` (default 2)
  - `TROOP_SPEED` (default 110)
  - `TROOP_HEALTH` (default 25)
  - `TROOP_DPS` (default 20)
  - `TROOP_ATTACK_RADIUS` (default 30)

## Rendering & Architecture Overview

- `showScreen()` draws the frame:
  - Clears color and depth buffers; draws a 2D gradient background in orthographic mode, then clears depth to render 3D.
  - Sets perspective/camera via `setupCamera()`.
  - Draws playground, towers with health bars, enemies, your troops, bullets, and hit effects.
  - Draws HUD text overlays.
- `idle()` is GLUT’s idle callback that computes delta time (dt), advances the simulation via `update_game(dt)`, and requests a redraw.
- `update_game(dt)` advances AI and mechanics:
  - Spawns first wave automatically, and sets `awaiting_next_wave` when a wave is cleared.
  - Moves enemies toward troops or towers; applies contact damage.
  - Moves troops toward nearest enemy and applies DPS in-range.
  - Updates tower cooldowns and handles cheat-mode auto-fire.
  - Advances the sweeping wave and applies damage/chip to enemies it intersects.
  - Updates bullets: lifetime, homing, movement, collisions, miss penalties, and hit effects.
  - Cleans up dead entities and checks Game Over conditions.

## Troubleshooting

- "No module named OpenGL": run `pip install PyOpenGL PyOpenGL-accelerate` in your environment.
- Blank/black window: ensure GPU drivers are up to date and a compatible OpenGL context is available.
- DLL not found (Windows): run from the project folder so `OpenGL/DLLS` can be located. Make sure you’re using 64‑bit Python with 64‑bit DLLs.
- Window closes immediately: run from a terminal to see errors; resolve missing dependencies.
- Very slow performance: install `PyOpenGL-accelerate`, close other GPU-heavy apps, or reduce `GRID_LENGTH` and spawn counts.

## Extending the Game

- Add a new enemy type: extend the selection logic in `start_next_wave()` and define its stats/visuals.
- Make troops persistent across waves: remove the clearing behavior or keep existing `player_troops` between waves.
- Change difficulty: tweak wave formulas, `ENEMY_SPEED`, damage values, and costs.
- New weapons/abilities: add new keyboard bindings and corresponding spawn/behavior logic, plus HUD text.
- Visual polish: add blending, textures, or more sophisticated models; add sound with a Python audio library.

## File Map

- `Hello_openGL.py`: main game, rendering, input, and mechanics.
- `OpenGL/`: PyOpenGL package (vendored) and FreeGLUT DLLs (Windows).

Enjoy defending your side!



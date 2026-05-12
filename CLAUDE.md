# Avolition — Project Instructions

> Powered by [ClaudeMaxPower](https://github.com/michelbr84/ClaudeMaxPower)

## Project Identity

Avolition is an open-source 3D isometric action game built with **Panda3D** and **Python**.
Originally created by Grzegorz 'Wezu' Kalinski (2014), licensed under GPLv3.

## Tech Stack

- **Engine**: Panda3D 1.10.15
- **Language**: Python 3.13
- **Dependencies**: panda3d, numpy, pillow, pygame
- **Virtual Environment**: `avolition_env/` (Windows venv)

## Project Structure

```
Avolition/
├── main.py                         # Minimal bootstrap (loads config -> launches GUI)
├── requirements.txt
├── CLAUDE.md
├── LICENSE.md
├── .gitignore
│
├── src/                            # Source code (Python package)
│   ├── core/                       # Game core
│   │   ├── app.py                  # Game class (scene management, bloom, shadows)
│   │   ├── engine.py               # Interactive, Monster, Spawner, MusicPlayer, LevelLoader
│   │   ├── config.py               # Unified GameConfig (JSON + legacy autoconfig)
│   │   └── constants.py            # Centralized asset path constants
│   │
│   ├── player/                     # Player system (refactored from monolithic player.py)
│   │   ├── base.py                 # PlayerBase - common code (~800 lines)
│   │   ├── warrior.py              # PC1 - Sword warrior (melee + shield)
│   │   ├── mage.py                 # PC2 - Female mage (plasma + lightning)
│   │   ├── ranger.py               # PC3 - Archer (bow + arrows + barbs)
│   │   ├── paladin.py              # PC4 - Magma mage (magma + teleport)
│   │   └── chargen.py              # Character generation/selection screen
│   │
│   ├── world/                      # World and level data
│   │   ├── data.py                 # Game data (monsters, items, levels)
│   │   └── demo_data.py            # Demo level data
│   │
│   ├── ai/                         # AI and pathfinding
│   │   ├── pathfinding.py          # Dijkstra algorithm (ex-dijkstra2.py)
│   │   └── visibility.py           # Visibility polygons (ex-vis_ninth.py)
│   │
│   ├── graphics/                   # Rendering and VFX
│   │   ├── vfx.py                  # VFX system (billboard sprites)
│   │   ├── particles.py            # Modern particle system
│   │   └── shaders.py              # Modern shader manager (PBR, bloom, SSAO)
│   │
│   ├── audio/                      # Audio system
│   │   ├── manager.py              # Modern audio manager (3D spatial)
│   │   └── soundpool.py            # Sound pool for monster SFX
│   │
│   └── ui/                         # User interface
│       ├── config_gui.py           # Configuration GUI (resolution, controls, audio)
│       └── launcher.py             # Modern tkinter launcher
│
├── assets/                         # Game assets (organized by type)
│   ├── shaders/                    # GLSL shaders (.sha)
│   ├── textures/ui/                # UI textures
│   ├── textures/environment/       # Environment textures
│   ├── fonts/                      # Fonts (Bitter-Bold.otf)
│   ├── icons/{cursors,hud,items,skills}/  # Categorized icons
│   ├── models/{characters,environment,tiles,vfx}/  # 3D models
│   ├── levels/                     # Level files (.bam, .egg)
│   ├── music/                      # Music tracks
│   ├── sfx/{combat,movement,abilities,environment,ui}/  # Categorized SFX
│   └── vfx/                        # VFX textures
│
├── tools/                          # Development tools
│   ├── editor/naive_editor.py      # Level editor
│   └── launcher/start_game.py      # CLI launcher
│
├── tests/                          # Test suite
│   ├── test_pathfinding.py
│   ├── test_config.py
│   └── test_data.py
│
├── docs/                           # Documentation
│   └── manual.pdf
│
├── config/                         # Configuration (gitignored)
└── saves/                          # Save files (gitignored)
```

## Legacy Files (kept for backward compatibility)

The original flat files (`game.py`, `engine.py`, `player.py`, `data.py`, etc.) still exist in the root.
The restructured code lives in `src/` with updated imports and asset paths.

## Core Coding Conventions

- Python 3 compatible (print functions, not statements)
- Panda3D conventions for scene graph, GUI, and shader management
- New code uses `src/` package structure with `from src.xxx import yyy`
- Asset paths use `assets/` prefix (e.g., `assets/shaders/tiles.sha`)
- Config via unified `GameConfig` class (JSON) with legacy `autoconfig.txt` fallback

## Running the Game

```bash
# Activate venv first
source avolition_env/Scripts/activate  # or avolition_env\Scripts\activate on Windows
python main.py
```

Or use the launcher:
```bash
python tools/launcher/start_game.py
```

## Running Tests

```bash
python tests/test_pathfinding.py
python tests/test_config.py
python tests/test_data.py
```

## Absolute Rules

- NEVER commit `.env`, `save.dat`, `autoconfig.txt`, or `config/game_config.json`
- NEVER push to `main` or `master` directly without review
- NEVER modify original game assets without backup
- Preserve GPLv3 license headers in source files

## Skills Available

| Skill | Command | Purpose |
|-------|---------|---------|
| fix-issue | `/fix-issue` | Fix a GitHub issue end-to-end |
| review-pr | `/review-pr` | Full PR review workflow |
| refactor-module | `/refactor-module` | Safe module refactor with tests |
| tdd-loop | `/tdd-loop` | Autonomous TDD loop until green |
| pre-commit | `/pre-commit` | Intelligent pre-commit checks |
| generate-docs | `/generate-docs` | Auto-generate docs from code |
| assemble-team | `/assemble-team` | Assemble an agent team for the project |

## Agents Available

- `code-reviewer` — strict code review with project memory
- `security-auditor` — OWASP-based vulnerability scanning
- `doc-writer` — documentation generation
- `team-coordinator` — orchestrates agent teams

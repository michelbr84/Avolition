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

| Directory/File | Purpose |
|----------------|---------|
| `main.py` | Configuration GUI (resolution, controls, audio) |
| `game.py` | Main game logic and scene management |
| `engine.py` | Rendering engine, shaders, lighting |
| `player.py` | Player controller and input handling |
| `vfx.py` | Visual effects system |
| `data.py` | Game data and level definitions |
| `chargen.py` | Character generation |
| `soundpool.py` | Audio management |
| `start_game.py` | Modern launcher with venv detection |
| `modern_launcher.py` | GUI launcher alternative |
| `models/` | 3D model assets (.egg, .bam) |
| `music/` | Music tracks |
| `sfx/` | Sound effects |
| `vfx/` | Visual effect assets |
| `*.sha` | Custom GLSL shaders |

## Core Coding Conventions

- Python 3 compatible (print functions, not statements)
- Panda3D conventions for scene graph, GUI, and shader management
- Config via `autoconfig.txt` (auto-generated) and `config.txt` (user custom)
- Game assets referenced by relative paths from project root

## Running the Game

```bash
# Activate venv first
source avolition_env/Scripts/activate  # or avolition_env\Scripts\activate on Windows
python main.py
```

Or use the launcher:
```bash
python start_game.py
```

## Absolute Rules

- NEVER commit `.env`, `save.dat`, or `autoconfig.txt` (auto-generated)
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

# Reestruturacao Completa do Projeto Avolition

## Estrutura Atual (problemas)

```
Avolition/                          # RAIZ POLUIDA - 50+ arquivos misturados
├── main.py                         # Config GUI + ponto de entrada
├── game.py                         # Logica do jogo
├── engine.py                       # Motor de renderizacao
├── player.py                       # 4 classes de personagem em 1 arquivo (4000+ linhas)
├── chargen.py                      # Geracao de personagem
├── data.py                         # Dados do jogo
├── demo_data.py                    # Dados da demo
├── vfx.py                          # Efeitos visuais
├── soundpool.py                    # Pool de audio
├── dijkstra2.py                    # Algoritmo pathfinding
├── vis_ninth.py                    # Visibilidade
├── naive_editor.py                 # Editor de niveis
├── start_game.py                   # Launcher CLI
├── modern_launcher.py              # Launcher GUI
├── config_modern.py                # Config moderno
├── modern_audio.py                 # Audio moderno
├── modern_particles.py             # Particulas modernas
├── modern_shaders.py               # Shaders modernos
├── *.sha (10 arquivos)             # Shaders soltos na raiz
├── *.png (15+ arquivos)            # Imagens de UI soltas na raiz
├── Bitter-Bold.otf                 # Fonte solta na raiz
├── Avolition Manual.pdf            # Manual solto na raiz
├── autoconfig.txt                  # Config auto-gerado
├── modern_config.json              # Config JSON
├── save.dat                        # Save do jogo
├── models/                         # OK - mas subpastas sem organizacao clara
│   ├── pc/                         # Modelos + animacoes + texturas misturados
│   ├── npc/                        # Idem
│   ├── tiles/
│   ├── *.egg / *.bam               # Modelos de nivel soltos
│   └── *.png                       # Texturas soltas
├── music/                          # OK
├── sfx/                            # OK - mas sem subcategorias
├── vfx/                            # OK
├── icon/                           # OK
├── .claude/                        # ClaudeMaxPower
├── skills/                         # ClaudeMaxPower skills
└── scripts/                        # ClaudeMaxPower scripts
```

### Problemas Identificados

1. **Raiz poluida**: 50+ arquivos misturados (codigo, shaders, imagens, fontes, docs)
2. **player.py monolitico**: 4000+ linhas com 4 classes quase identicas (PC1-PC4)
3. **Shaders soltos**: 10 arquivos `.sha` na raiz sem organizacao
4. **Assets de UI soltos**: 15+ imagens PNG na raiz (glass.png, config.png, etc.)
5. **Sem separacao src/assets**: Codigo Python misturado com assets
6. **Sem testes**: Nenhum diretorio de testes
7. **Sem separacao de concerns**: `main.py` faz config GUI E bootstrap do jogo
8. **Pathfinding/utilidades misturados**: `dijkstra2.py`, `vis_ninth.py` sem contexto
9. **Duplicacao massiva**: 4 classes de player quase identicas copiadas e coladas
10. **Editor misturado com jogo**: `naive_editor.py` no mesmo nivel que o jogo

---

## Estrutura Proposta

```
Avolition/
│
├── main.py                         # Ponto de entrada unico (bootstrap minimo)
├── requirements.txt                # Dependencias
├── CLAUDE.md                       # Instrucoes ClaudeMaxPower
├── LICENSE.md                      # Licenca GPLv3
├── README.md                       # Documentacao principal
├── .gitignore
├── .gitattributes
│
├── src/                            # === CODIGO FONTE ===
│   ├── __init__.py
│   │
│   ├── core/                       # Nucleo do jogo
│   │   ├── __init__.py
│   │   ├── app.py                  # Classe principal do jogo (ex-game.py)
│   │   ├── engine.py               # Motor de renderizacao
│   │   ├── config.py               # Configuracao (unificado: main.py config + config_modern.py)
│   │   └── constants.py            # Constantes globais (resolucoes, limites, etc.)
│   │
│   ├── player/                     # Sistema de jogador
│   │   ├── __init__.py
│   │   ├── base.py                 # Classe base PlayerBase (codigo comum das 4 PCs)
│   │   ├── warrior.py              # PC1 - Guerreiro (apenas diferencas)
│   │   ├── ranger.py               # PC2 - Arqueiro (apenas diferencas)
│   │   ├── mage.py                 # PC3 - Mago (apenas diferencas)
│   │   ├── paladin.py              # PC4 - Paladino (apenas diferencas)
│   │   └── chargen.py              # Geracao/selecao de personagem
│   │
│   ├── world/                      # Mundo e niveis
│   │   ├── __init__.py
│   │   ├── data.py                 # Dados do jogo (monstros, itens, niveis)
│   │   ├── demo_data.py            # Dados da demo
│   │   └── level_loader.py         # Carregamento de niveis (extraido de engine.py)
│   │
│   ├── ai/                         # Inteligencia artificial e pathfinding
│   │   ├── __init__.py
│   │   ├── pathfinding.py          # Algoritmo Dijkstra (ex-dijkstra2.py)
│   │   └── visibility.py           # Poligonos de visibilidade (ex-vis_ninth.py)
│   │
│   ├── graphics/                   # Renderizacao e efeitos visuais
│   │   ├── __init__.py
│   │   ├── vfx.py                  # Sistema de efeitos visuais
│   │   ├── particles.py            # Sistema de particulas (ex-modern_particles.py)
│   │   └── shaders.py              # Gerenciador de shaders (ex-modern_shaders.py)
│   │
│   ├── audio/                      # Sistema de audio
│   │   ├── __init__.py
│   │   ├── manager.py              # Gerenciador de audio (ex-modern_audio.py)
│   │   └── soundpool.py            # Pool de sons
│   │
│   └── ui/                         # Interface do usuario
│       ├── __init__.py
│       ├── config_gui.py           # GUI de configuracao (ex-main.py Config class)
│       ├── hud.py                  # HUD in-game (extraido de player.py/engine.py)
│       └── launcher.py             # Launcher moderno (ex-modern_launcher.py)
│
├── assets/                         # === ASSETS DO JOGO ===
│   │
│   ├── shaders/                    # Shaders GLSL
│   │   ├── black_parts.sha
│   │   ├── blur.sha
│   │   ├── floor.sha
│   │   ├── gaussian_blur.sha
│   │   ├── glow.sha               # (ex-glowShader.sha)
│   │   ├── invert_threshold.sha    # (ex-invert_threshold_r_blur.sha)
│   │   ├── lens_flare.sha
│   │   ├── shader1.sha
│   │   ├── shader2.sha
│   │   ├── shadow.sha
│   │   └── tiles.sha
│   │
│   ├── textures/                   # Texturas gerais
│   │   ├── ui/                     # Texturas de interface
│   │   │   ├── config.png
│   │   │   ├── config2.png
│   │   │   ├── config_keys.png
│   │   │   ├── config_press.png
│   │   │   ├── glass.png
│   │   │   ├── glass1.png
│   │   │   ├── glass2.png
│   │   │   ├── glass3.png
│   │   │   ├── glass4.png
│   │   │   ├── inside.png
│   │   │   ├── outside.png
│   │   │   ├── loading2.png
│   │   │   ├── select.png
│   │   │   ├── mp_logo.png
│   │   │   └── fog2.png
│   │   └── environment/            # Texturas de ambiente (atualmente em models/)
│   │       ├── ground.png
│   │       ├── ground_ns.png
│   │       ├── rock.png
│   │       ├── rock_n.png
│   │       ├── rock_ns.png
│   │       ├── wood.png
│   │       ├── wood_n.png
│   │       ├── lava_cg.png
│   │       └── lava_n.png
│   │
│   ├── fonts/                      # Fontes
│   │   └── Bitter-Bold.otf
│   │
│   ├── icons/                      # Icones de HUD e habilidades (ex-icon/)
│   │   ├── cursors/
│   │   │   ├── cursor1.png
│   │   │   ├── cursor_lightning.png
│   │   │   └── cursor_plasma.png
│   │   ├── hud/
│   │   │   ├── health_frame.png
│   │   │   ├── health_frame2.png
│   │   │   ├── heart.png
│   │   │   ├── heart1.png
│   │   │   ├── arc_grow.png
│   │   │   ├── arc_grow2.png
│   │   │   ├── arc_shrink.png
│   │   │   └── glass*.png
│   │   ├── items/
│   │   │   ├── icon_flask.png
│   │   │   ├── icon_key.png
│   │   │   └── icon_lock.png
│   │   └── skills/
│   │       ├── amp.png
│   │       ├── armor.png
│   │       ├── blast.png
│   │       ├── bleed.png
│   │       ├── critical.png
│   │       ├── damage.png
│   │       ├── lightning.png
│   │       ├── shield.png
│   │       ├── sword.png
│   │       └── ... (demais icones de habilidades)
│   │
│   ├── models/                     # Modelos 3D
│   │   ├── characters/
│   │   │   ├── player/             # Modelos de jogador (ex-models/pc/)
│   │   │   │   ├── male/
│   │   │   │   │   ├── male.egg
│   │   │   │   │   ├── male_attack1.egg
│   │   │   │   │   ├── male_run.egg
│   │   │   │   │   └── ...
│   │   │   │   └── female/
│   │   │   │       ├── female.egg
│   │   │   │       ├── female_attack1.egg
│   │   │   │       └── ...
│   │   │   └── enemies/            # Modelos de inimigos (ex-models/npc/)
│   │   │       ├── goblin/
│   │   │       ├── golem/
│   │   │       ├── skeleton/
│   │   │       ├── zombie/
│   │   │       └── monster/
│   │   ├── environment/            # Props e cenario
│   │   │   ├── wall_w_collision2.egg
│   │   │   ├── pointer.egg
│   │   │   ├── waypoint.egg
│   │   │   ├── plane.egg
│   │   │   ├── flask.egg
│   │   │   ├── key.egg
│   │   │   ├── lava.egg
│   │   │   └── camp3.egg
│   │   ├── tiles/                  # Tiles de mapa (ex-models/tiles/)
│   │   │   └── texture/
│   │   └── vfx/                    # Modelos de efeitos (ex-vfx/*.egg)
│   │       ├── short_vfx.egg
│   │       ├── vfx1.egg
│   │       ├── vfx2.egg
│   │       ├── vfx3.egg
│   │       ├── ring_anim.egg
│   │       ├── ring_morph.egg
│   │       └── green_ring_morph.egg
│   │
│   ├── levels/                     # Niveis do jogo (ex-models/*.bam)
│   │   ├── level1.bam
│   │   ├── level2.bam
│   │   ├── level3.bam
│   │   ├── level4.bam
│   │   ├── level4.egg              # Fonte editavel do nivel 4
│   │   ├── level5.bam
│   │   ├── level_a1.bam
│   │   ├── level_a2.bam
│   │   ├── level_a3.bam
│   │   ├── level_a4.bam
│   │   ├── level_a5.bam
│   │   ├── level_b1.bam
│   │   ├── level_b2.bam
│   │   ├── level_b3.bam
│   │   └── level_b4.bam
│   │
│   ├── music/                      # Trilha sonora
│   │   ├── Defying.ogg
│   │   ├── Descent.ogg
│   │   ├── HeroicDemise.ogg
│   │   ├── Wasteland.ogg
│   │   └── ...
│   │
│   ├── sfx/                        # Efeitos sonoros
│   │   ├── combat/                 # Sons de combate
│   │   │   ├── hit1.ogg
│   │   │   ├── hit2.ogg
│   │   │   ├── swing1.ogg
│   │   │   ├── block1.ogg
│   │   │   └── ...
│   │   ├── movement/               # Sons de movimento
│   │   │   ├── walk.ogg
│   │   │   ├── run1.ogg
│   │   │   └── ...
│   │   ├── abilities/              # Sons de habilidades
│   │   │   ├── heal.ogg
│   │   │   ├── plasma.ogg
│   │   │   ├── thunder.ogg
│   │   │   ├── forcefield.ogg
│   │   │   └── ...
│   │   ├── environment/            # Sons ambientais
│   │   │   ├── magma_flow.ogg
│   │   │   ├── door_open.ogg
│   │   │   └── ...
│   │   └── ui/                     # Sons de interface
│   │       ├── click_stereo.ogg
│   │       └── key_pickup.ogg
│   │
│   └── vfx/                        # Texturas de efeitos visuais
│       ├── aura.png
│       ├── blood_red.png
│       ├── boom_fire.png
│       ├── lightning.png
│       ├── sparks.png
│       └── ...
│
├── tools/                          # === FERRAMENTAS ===
│   ├── editor/                     # Editor de niveis
│   │   └── naive_editor.py
│   └── launcher/                   # Launcher externo
│       └── start_game.py
│
├── tests/                          # === TESTES ===
│   ├── __init__.py
│   ├── test_config.py              # Testes de configuracao
│   ├── test_pathfinding.py         # Testes do Dijkstra
│   ├── test_visibility.py          # Testes de visibilidade
│   ├── test_data.py                # Testes de dados do jogo
│   └── test_player_stats.py        # Testes de stats do jogador
│
├── docs/                           # === DOCUMENTACAO ===
│   ├── manual.pdf                  # Manual do jogo (ex-Avolition Manual.pdf)
│   ├── architecture.md             # Arquitetura do projeto
│   ├── modding.md                  # Guia de modding
│   └── controls.md                 # Referencia de controles
│
├── config/                         # === CONFIGURACAO ===
│   ├── default_config.json         # Config padrao (versionado)
│   └── autoconfig.txt              # Auto-gerado (gitignored)
│
├── saves/                          # === SAVES (gitignored) ===
│   └── save.dat
│
└── .claude/                        # === CLAUDEMAXPOWER ===
    ├── agents/
    ├── hooks/
    ├── settings.json
    └── skills/ -> ../../skills/
```

---

## Refatoracoes de Codigo Prioritarias

### 1. Extrair classe base do Player (CRITICO)

O arquivo `player.py` tem **4000+ linhas** com 4 classes quase identicas.
Extrair uma classe `PlayerBase` com todo o codigo comum:

```
player.py (4000+ linhas, 4 classes) -->
    src/player/base.py      (~800 linhas, classe PlayerBase)
    src/player/warrior.py   (~200 linhas, apenas override de ataque/stats)
    src/player/ranger.py    (~200 linhas, apenas override de projetil/stats)
    src/player/mage.py      (~200 linhas, apenas override de magia/stats)
    src/player/paladin.py   (~200 linhas, apenas override de habilidades/stats)
```

**Codigo comum** entre PC1-PC4 (estimativa 80%):
- Sistema de camera e movimento
- Sistema de colisao
- HUD e cursor
- Sistema de HP/dano/morte
- Keymap e input handling
- Setup de luz e sombra
- Zoom e waypoints

**Codigo diferente** entre PC1-PC4 (estimativa 20%):
- Ataque primario/secundario (melee vs ranged vs magic)
- Stats e formulas de dano
- Efeitos visuais especificos
- Animacoes especificas
- Setup de modelo/textura

### 2. Separar Config GUI do Bootstrap (ALTO)

```
main.py (Config GUI + bootstrap) -->
    src/ui/config_gui.py     (classe Config - janela de configuracao)
    src/core/config.py       (carregamento/salvamento de config unificado)
    main.py                  (bootstrap minimo: carrega config -> abre GUI ou jogo)
```

### 3. Unificar Sistemas de Configuracao (MEDIO)

Atualmente existem 3 sistemas paralelos:
- `autoconfig.txt` (formato Panda3D, gerado pelo main.py)
- `modern_config.json` (formato JSON, gerado pelo config_modern.py)
- Variaveis `ConfigVariable*` espalhadas pelo codigo

Unificar em um unico sistema:
```python
# src/core/config.py
class GameConfig:
    """Sistema unificado de configuracao"""
    def load(self) -> dict          # Carrega de JSON
    def save(self)                  # Salva em JSON
    def to_panda3d(self) -> str     # Exporta para formato Panda3D
    def apply(self)                 # Aplica via loadPrcFileData
```

### 4. Atualizar Paths de Assets (MEDIO)

Todos os caminhos de assets no codigo precisam ser atualizados.
Usar constantes centralizadas:

```python
# src/core/constants.py
from pathlib import Path

ASSETS_DIR = Path("assets")
SHADERS_DIR = ASSETS_DIR / "shaders"
TEXTURES_DIR = ASSETS_DIR / "textures"
MODELS_DIR = ASSETS_DIR / "models"
LEVELS_DIR = ASSETS_DIR / "levels"
MUSIC_DIR = ASSETS_DIR / "music"
SFX_DIR = ASSETS_DIR / "sfx"
VFX_DIR = ASSETS_DIR / "vfx"
ICONS_DIR = ASSETS_DIR / "icons"
FONTS_DIR = ASSETS_DIR / "fonts"
```

---

## Ordem de Execucao Recomendada

### Fase 1: Preparacao (sem quebrar nada)
1. Criar diretorios `src/`, `assets/`, `tools/`, `tests/`, `docs/`, `config/`, `saves/`
2. Mover assets (shaders, imagens, fontes, manual) para `assets/`
3. Mover `naive_editor.py` para `tools/editor/`
4. Mover `start_game.py` para `tools/launcher/`
5. Criar `docs/` com manual
6. Atualizar `.gitignore` para novos paths

### Fase 2: Reorganizar Assets
1. Reorganizar `models/` em subcategorias (characters/player, characters/enemies, environment)
2. Mover niveis `.bam` para `assets/levels/`
3. Reorganizar `sfx/` em subcategorias
4. Reorganizar `icon/` em subcategorias
5. Atualizar todos os paths de assets no codigo

### Fase 3: Refatorar Codigo (maior risco)
1. Criar `src/core/constants.py` com paths
2. Extrair `PlayerBase` de `player.py` (maior refatoracao)
3. Separar `main.py` em config GUI + bootstrap
4. Mover modulos para `src/` com `__init__.py`
5. Unificar sistema de configuracao
6. Criar `src/ai/` com pathfinding e visibilidade

### Fase 4: Qualidade
1. Criar testes basicos em `tests/`
2. Atualizar `README.md` completo
3. Documentar arquitetura em `docs/architecture.md`

---

## Impacto e Riscos

| Acao | Impacto | Risco | Mitigacao |
|------|---------|-------|-----------|
| Mover assets | Todos os paths quebram | ALTO | Atualizar com search/replace em batch |
| Extrair PlayerBase | Core gameplay afetado | ALTO | Testar cada classe individualmente |
| Reorganizar src/ | Todos os imports mudam | MEDIO | Usar imports relativos + __init__.py |
| Mover shaders | Rendering pode quebrar | MEDIO | Testar cada shader apos mover |
| Separar main.py | Fluxo de boot muda | BAIXO | Manter fallback para boot original |
| Criar testes | Nenhum | NENHUM | Comecar com testes de unidade simples |

---

## Metricas de Sucesso

- [ ] Zero arquivos `.py` na raiz (exceto `main.py`)
- [ ] Zero arquivos de assets na raiz (`.png`, `.sha`, `.otf`, `.pdf`)
- [ ] `player.py` reduzido de 4000+ para <1000 linhas
- [ ] Cada modulo em `src/` com responsabilidade unica
- [ ] Testes cobrindo pathfinding, config e stats do player
- [ ] Todos os assets organizados por tipo em `assets/`
- [ ] Documentacao atualizada refletindo nova estrutura

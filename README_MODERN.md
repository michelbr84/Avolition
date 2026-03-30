# 🎮 Avolition - Versão Modernizada

**Avolition** é um jogo de ação e aventura 3D desenvolvido com Panda3D que foi completamente modernizado com recursos avançados de gráficos, áudio e gameplay.

## ✨ Novos Recursos Implementados

### 🎨 Sistema de Shaders Modernos
- **PBR (Physically Based Rendering)**: Renderização baseada em física para materiais realistas
- **Bloom Effect**: Efeito de brilho para fontes de luz
- **Water Shaders**: Shaders avançados para água com reflexões e refrações
- **Motion Blur**: Efeito de desfoque de movimento
- **SSAO**: Screen Space Ambient Occlusion para sombras mais realistas

### 💥 Sistema de Partículas Avançado
- **Física Realista**: Partículas com gravidade, arrasto e colisões
- **Efeitos Específicos**: 
  - Fogo com movimento natural
  - Explosões com partículas em todas as direções
  - Efeitos mágicos com movimento espiral
  - Sangue com física baseada na direção do golpe
- **Soft Particles**: Suavização das bordas das partículas
- **Billboard Rendering**: Partículas sempre olhando para a câmera

### 🔊 Sistema de Áudio 3D
- **Áudio Posicional**: Sons 3D com atenuação baseada na distância
- **Fade In/Out**: Transições suaves entre músicas
- **Efeitos de Áudio**: Reverb, echo e filtros passa-baixa
- **Sons Contextuais**: 
  - Sons ambientes baseados no ambiente
  - Sons de combate específicos por arma
  - Sons de passos por tipo de superfície

### ⚙️ Sistema de Configuração Moderno
- **Interface Gráfica**: Launcher com interface moderna usando Tkinter
- **Configurações Avançadas**: 
  - Resolução e modo de tela
  - Qualidade gráfica detalhada
  - Controles de áudio independentes
  - Opções de gameplay
- **Persistência**: Configurações salvas em JSON
- **Compatibilidade**: Conversão automática para formato Panda3D

### 🎯 Melhorias de Gameplay
- **Dificuldades Múltiplas**: Fácil, Normal, Difícil, Pesadelo
- **Auto-save**: Sistema de salvamento automático
- **Interface Moderna**: HUD com informações detalhadas
- **Debug Mode**: Ferramentas para desenvolvedores

## 🚀 Como Usar

### Pré-requisitos
```bash
Python 3.8+
Panda3D 1.10+
Pillow
NumPy
Pygame
```

### Instalação
1. **Clone o repositório**:
   ```bash
   git clone <repository-url>
   cd Avolition
   ```

2. **Crie um ambiente virtual**:
   ```bash
   python -m venv avolition_env
   ```

3. **Ative o ambiente virtual**:
   - Windows: `.\avolition_env\Scripts\Activate.ps1`
   - Linux/Mac: `source avolition_env/bin/activate`

4. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

### Executando o Jogo

#### Opcao 1: Launcher com Menu (Recomendado)
```bash
python start_game.py
```
O launcher detecta automaticamente o ambiente virtual e instala dependencias faltantes.

#### Opcao 2: Launcher Moderno (GUI)
```bash
python start_game.py --launcher
```

#### Opcao 3: Jogo Direto
```bash
python main.py
```

## 📁 Estrutura de Arquivos

```
Avolition/
├── start_game.py           # Launcher principal (detecta venv automaticamente)
├── main.py                 # Configuracao e ponto de entrada do jogo
├── game.py                 # Logica principal do jogo
├── engine.py               # Motor de renderizacao
├── player.py               # Controlador do jogador
├── modern_launcher.py      # Launcher moderno (GUI Tkinter)
├── config_modern.py        # Sistema de configuracao moderno
├── modern_shaders.py       # Shaders avancados (PBR, Bloom, etc.)
├── modern_particles.py     # Sistema de particulas
├── modern_audio.py         # Sistema de audio 3D
├── requirements.txt        # Dependencias
├── CLAUDE.md               # Instrucoes para Claude Code (ClaudeMaxPower)
├── .claude/                # Agentes, hooks e configuracao ClaudeMaxPower
├── skills/                 # Skills reutilizaveis para Claude Code
└── [assets do jogo: models/, music/, sfx/, vfx/, *.sha]
```

## 🎮 Controles

### Movimento
- **WASD** ou **Setas**: Movimento do personagem
- **Mouse**: Controle da câmera
- **Q/E**: Rotação da câmera

### Ações
- **Mouse Esquerdo** ou **Enter**: Ação primária
- **Mouse Direito** ou **Espaço**: Ação secundária
- **Roda do Mouse** ou **R/F**: Zoom

## 🔧 Configurações Avançadas

### Gráficos
- **Resolução**: 1920x1080, 1600x900, 1366x768, 1280x720, 1024x768
- **Anti-aliasing**: 0-8x MSAA
- **Qualidade de Sombras**: Baixa, Média, Alta, Ultra
- **Efeitos de Partículas**: Habilitado/Desabilitado
- **Bloom**: Habilitado/Desabilitado

### Áudio
- **Volume Master**: 0-100%
- **Volume Música**: 0-100%
- **Volume Efeitos**: 0-100%
- **Volume Voz**: 0-100%
- **Reverb**: Habilitado/Desabilitado
- **Echo**: Habilitado/Desabilitado

### Gameplay
- **Dificuldade**: Fácil, Normal, Difícil, Pesadelo
- **Auto-save**: Habilitado/Desabilitado
- **Mostrar FPS**: Habilitado/Desabilitado
- **Mostrar Minimapa**: Habilitado/Desabilitado
- **Números de Dano**: Habilitado/Desabilitado

## 🛠️ Desenvolvimento

### Adicionando Novos Shaders
```python
from modern_shaders import shader_manager

# Aplicar shader PBR
shader_manager.apply_pbr_material(
    node, albedo_tex, normal_tex, metallic_roughness_tex, ao_tex
)

# Aplicar shader de água
shader_manager.apply_water_shader(node, water_tex, reflection_tex)
```

### Adicionando Efeitos de Partículas
```python
from modern_particles import particle_manager

# Criar sistema de partículas
system = particle_manager.create_system("fire_system")

# Emitir partículas
system.emit_fire(position, count=20)
system.emit_explosion(position, count=50)
system.emit_magic(position, count=30)
```

### Configurando Áudio
```python
from modern_audio import audio_manager

# Carregar sons
audio_manager.load_sound("sword_swing", "sfx/sword_swing.ogg")
audio_manager.load_music("battle_theme", "music/battle.ogg")

# Tocar sons
audio_manager.play_sound("sword_swing", position)
audio_manager.play_music("battle_theme")
```

## 🐛 Solução de Problemas

### Erro: "No module named 'panda3d'"
```bash
pip install panda3d
```

### Erro: "No module named 'PIL'"
```bash
pip install pillow
```

### Performance Baixa
1. Reduza a resolução nas configurações
2. Desabilite efeitos de partículas
3. Reduza a qualidade de sombras
4. Desabilite o bloom

### Áudio Não Funciona
1. Verifique se o dispositivo de áudio está funcionando
2. Teste com diferentes formatos de arquivo (.ogg, .wav)
3. Verifique as configurações de volume

## 📝 Changelog

### v2.0.0 - Modernização Completa
- ✨ Sistema de shaders PBR implementado
- 💥 Sistema de partículas avançado
- 🔊 Áudio 3D com efeitos
- ⚙️ Launcher moderno com interface gráfica
- 🎯 Configurações avançadas
- 📚 Documentação completa

### v1.0.0 - Versão Original
- 🎮 Jogo base funcional
- 🎨 Gráficos básicos
- 🔊 Áudio simples
- ⚙️ Configurações básicas

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a GNU General Public License v3.0 - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙏 Agradecimentos

- **Grzegorz 'Wezu' Kalinski**: Criador original do Avolition
- **Panda3D Team**: Engine 3D incrível
- **Comunidade Python**: Ferramentas e bibliotecas essenciais

---

**Divirta-se jogando Avolition! 🎮✨**

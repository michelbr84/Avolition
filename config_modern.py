"""
Configurações modernas para Avolition
Versão atualizada com recursos modernos
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class ModernConfig:
    # Configurações de vídeo
    resolution: str = "1920x1080"
    fullscreen: bool = False
    vsync: bool = True
    antialiasing: int = 4  # MSAA samples
    anisotropic_filtering: int = 16
    
    # Configurações de qualidade gráfica
    shadow_quality: str = "high"  # low, medium, high, ultra
    texture_quality: str = "high"
    draw_distance: int = 1000
    particle_effects: bool = True
    bloom_effect: bool = True
    motion_blur: bool = False
    
    # Configurações de áudio
    master_volume: int = 100
    music_volume: int = 80
    sfx_volume: int = 100
    voice_volume: int = 100
    
    # Configurações de controles
    mouse_sensitivity: float = 1.0
    invert_mouse_y: bool = False
    controller_enabled: bool = True
    
    # Configurações de interface
    ui_scale: float = 1.0
    show_fps: bool = True
    show_minimap: bool = True
    show_damage_numbers: bool = True
    
    # Configurações de gameplay
    difficulty: str = "normal"  # easy, normal, hard, nightmare
    auto_save: bool = True
    save_interval: int = 300  # segundos
    
    # Configurações avançadas
    debug_mode: bool = False
    developer_console: bool = False
    custom_shaders: bool = True
    
    def save(self, filename: str = "modern_config.json"):
        """Salva as configurações em arquivo JSON"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filename: str = "modern_config.json") -> 'ModernConfig':
        """Carrega configurações de arquivo JSON"""
        if os.path.exists(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Filter to only known fields
                valid_fields = {f.name for f in cls.__dataclass_fields__.values()}
                filtered = {k: v for k, v in data.items() if k in valid_fields}
                return cls(**filtered)
            except (json.JSONDecodeError, TypeError):
                pass
        return cls()
    
    def to_panda3d_config(self) -> Dict[str, Any]:
        """Converte para formato compatível com Panda3D"""
        return {
            'win-size': self.resolution.replace('x', ' '),
            'fullscreen': '1' if self.fullscreen else '0',
            'vsync': '1' if self.vsync else '0',
            'multisamples': str(self.antialiasing),
            'anisotropic-degree': str(self.anisotropic_filtering),
            'music-volume': str(self.music_volume),
            'sound-volume': str(self.sfx_volume),
            'show-frame-rate-meter': '1' if self.show_fps else '0',
        }

# Instância global de configuração
modern_config = ModernConfig.load()

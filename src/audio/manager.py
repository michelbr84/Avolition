"""
Sistema de Áudio Moderno para Avolition
Suporte a áudio 3D, efeitos e música dinâmica
"""

import os
import random
from panda3d.core import AudioSound, AudioManager, Point3, Vec3
from panda3d.core import ConfigVariableBool, ConfigVariableDouble
import pygame.mixer

class ModernAudioManager:
    def __init__(self):
        self.audio_manager = None
        self.sounds = {}
        self.music_tracks = {}
        self.current_music = None
        self.volume_master = 1.0
        self.volume_sfx = 1.0
        self.volume_music = 1.0
        self.volume_voice = 1.0
        
        # Configurações de áudio 3D
        self.listener_position = Point3(0, 0, 0)
        self.listener_forward = Vec3(0, 1, 0)
        self.listener_up = Vec3(0, 0, 1)
        
        # Efeitos de áudio
        self.reverb_enabled = True
        self.echo_enabled = False
        self.low_pass_filter = False
        
        self._initialize_audio()
    
    def _initialize_audio(self):
        """Inicializa o sistema de áudio"""
        try:
            # Configura o gerenciador de áudio do Panda3D
            self.audio_manager = AudioManager.create_AudioManager()
            self.audio_manager.set_active(True)
            
            # Configurações de qualidade
            self.audio_manager.set_concurrent_sound_limit(32)
            self.audio_manager.set_volume(1.0)
            
            print("Sistema de áudio inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar áudio: {e}")
    
    def load_sound(self, name, filepath, volume=1.0, loop=False):
        """Carrega um efeito sonoro"""
        try:
            if os.path.exists(filepath):
                sound = self.audio_manager.get_sound(filepath)
                if sound:
                    sound.set_volume(volume * self.volume_sfx)
                    sound.set_loop(loop)
                    self.sounds[name] = {
                        'sound': sound,
                        'volume': volume,
                        'filepath': filepath
                    }
                    print(f"Som carregado: {name}")
                    return True
        except Exception as e:
            print(f"Erro ao carregar som {name}: {e}")
        return False
    
    def load_music(self, name, filepath, volume=1.0):
        """Carrega uma música"""
        try:
            if os.path.exists(filepath):
                music = self.audio_manager.get_sound(filepath)
                if music:
                    music.set_volume(volume * self.volume_music)
                    music.set_loop(True)
                    self.music_tracks[name] = {
                        'music': music,
                        'volume': volume,
                        'filepath': filepath
                    }
                    print(f"Música carregada: {name}")
                    return True
        except Exception as e:
            print(f"Erro ao carregar música {name}: {e}")
        return False
    
    def play_sound(self, name, position=None):
        """Toca um efeito sonoro"""
        if name in self.sounds:
            sound_data = self.sounds[name]
            sound = sound_data['sound']
            
            # Configura posição 3D se fornecida
            if position:
                sound.set_3d_attributes(position, Vec3(0, 0, 0))
                sound.set_3d_min_distance(5.0)
                sound.set_3d_max_distance(50.0)
            
            sound.play()
            return True
        return False
    
    def play_music(self, name, fade_in=True):
        """Toca uma música"""
        if name in self.music_tracks:
            # Para a música atual se houver
            if self.current_music:
                self.stop_music(fade_out=True)
            
            music_data = self.music_tracks[name]
            self.current_music = music_data['music']
            
            if fade_in:
                self.current_music.set_volume(0.0)
                self.current_music.play()
                # Fade in gradual
                self._fade_music_in()
            else:
                self.current_music.play()
            
            return True
        return False
    
    def stop_music(self, fade_out=True):
        """Para a música atual"""
        if self.current_music:
            if fade_out:
                self._fade_music_out()
            else:
                self.current_music.stop()
                self.current_music = None
    
    def _fade_music_in(self, duration=2.0):
        """Fade in gradual da música"""
        if self.current_music:
            target_volume = self.volume_music
            current_volume = 0.0
            step = target_volume / (duration * 60)  # Assumindo 60 FPS
            
            def fade_step():
                nonlocal current_volume
                if current_volume < target_volume:
                    current_volume = min(current_volume + step, target_volume)
                    self.current_music.set_volume(current_volume)
                    taskMgr.doMethodLater(1.0/60.0, fade_step, 'fade_in_task')
            
            fade_step()
    
    def _fade_music_out(self, duration=2.0):
        """Fade out gradual da música"""
        if self.current_music:
            current_volume = self.current_music.get_volume()
            step = current_volume / (duration * 60)
            
            def fade_step():
                nonlocal current_volume
                if current_volume > 0:
                    current_volume = max(current_volume - step, 0.0)
                    self.current_music.set_volume(current_volume)
                    taskMgr.doMethodLater(1.0/60.0, fade_step, 'fade_out_task')
                else:
                    self.current_music.stop()
                    self.current_music = None
            
            fade_step()
    
    def set_master_volume(self, volume):
        """Define o volume master (0.0 a 1.0)"""
        self.volume_master = max(0.0, min(1.0, volume))
        self._update_all_volumes()
    
    def set_sfx_volume(self, volume):
        """Define o volume dos efeitos sonoros"""
        self.volume_sfx = max(0.0, min(1.0, volume))
        self._update_sfx_volumes()
    
    def set_music_volume(self, volume):
        """Define o volume da música"""
        self.volume_music = max(0.0, min(1.0, volume))
        self._update_music_volumes()
    
    def set_voice_volume(self, volume):
        """Define o volume das vozes"""
        self.volume_voice = max(0.0, min(1.0, volume))
        self._update_voice_volumes()
    
    def _update_all_volumes(self):
        """Atualiza todos os volumes"""
        self._update_sfx_volumes()
        self._update_music_volumes()
        self._update_voice_volumes()
    
    def _update_sfx_volumes(self):
        """Atualiza volumes dos efeitos sonoros"""
        for sound_data in self.sounds.values():
            sound = sound_data['sound']
            base_volume = sound_data['volume']
            sound.set_volume(base_volume * self.volume_sfx * self.volume_master)
    
    def _update_music_volumes(self):
        """Atualiza volumes das músicas"""
        for music_data in self.music_tracks.values():
            music = music_data['music']
            base_volume = music_data['volume']
            music.set_volume(base_volume * self.volume_music * self.volume_master)
        
        if self.current_music:
            current_volume = self.current_music.get_volume()
            # Mantém a proporção do fade
            if current_volume > 0:
                self.current_music.set_volume(current_volume * self.volume_master)
    
    def _update_voice_volumes(self):
        """Atualiza volumes das vozes"""
        # Implementar quando houver sistema de voz
        pass
    
    def set_listener_position(self, position, forward=None, up=None):
        """Define a posição do listener para áudio 3D"""
        self.listener_position = Point3(position)
        if forward:
            self.listener_forward = Vec3(forward)
        if up:
            self.listener_up = Vec3(up)
        
        if self.audio_manager:
            self.audio_manager.set_3d_listener_attributes(
                self.listener_position,
                self.listener_forward,
                self.listener_up,
                Vec3(0, 0, 0)
            )
    
    def play_ambient_sounds(self, environment_type):
        """Toca sons ambientes baseados no ambiente"""
        ambient_sounds = {
            'forest': ['wind', 'birds', 'leaves'],
            'cave': ['dripping', 'echo', 'wind'],
            'city': ['crowd', 'traffic', 'bells'],
            'dungeon': ['dripping', 'chains', 'wind'],
            'battlefield': ['wind', 'distant_battle', 'horns']
        }
        
        if environment_type in ambient_sounds:
            for sound_name in ambient_sounds[environment_type]:
                if sound_name in self.sounds:
                    self.play_sound(sound_name)
    
    def play_combat_sounds(self, weapon_type, hit_type):
        """Toca sons de combate"""
        sound_mapping = {
            'sword': {
                'swing': 'sword_swing',
                'hit': 'sword_hit',
                'block': 'sword_block'
            },
            'bow': {
                'draw': 'bow_draw',
                'release': 'bow_release',
                'hit': 'arrow_hit'
            },
            'magic': {
                'cast': 'magic_cast',
                'hit': 'magic_hit',
                'explosion': 'magic_explosion'
            }
        }
        
        if weapon_type in sound_mapping and hit_type in sound_mapping[weapon_type]:
            sound_name = sound_mapping[weapon_type][hit_type]
            if sound_name in self.sounds:
                self.play_sound(sound_name)
    
    def play_footstep_sounds(self, surface_type, position=None):
        """Toca sons de passos"""
        footstep_sounds = {
            'grass': 'footstep_grass',
            'stone': 'footstep_stone',
            'wood': 'footstep_wood',
            'metal': 'footstep_metal',
            'water': 'footstep_water'
        }
        
        if surface_type in footstep_sounds:
            sound_name = footstep_sounds[surface_type]
            if sound_name in self.sounds:
                self.play_sound(sound_name, position)
    
    def enable_reverb(self, enabled=True):
        """Habilita/desabilita reverb"""
        self.reverb_enabled = enabled
        # Implementar efeito de reverb
    
    def enable_echo(self, enabled=True):
        """Habilita/desabilita echo"""
        self.echo_enabled = enabled
        # Implementar efeito de echo
    
    def set_low_pass_filter(self, enabled=True, cutoff_freq=1000.0):
        """Configura filtro passa-baixa"""
        self.low_pass_filter = enabled
        # Implementar filtro passa-baixa
    
    def cleanup(self):
        """Limpa recursos de áudio"""
        if self.current_music:
            self.current_music.stop()
        
        for sound_data in self.sounds.values():
            sound_data['sound'].stop()
        
        for music_data in self.music_tracks.values():
            music_data['music'].stop()
        
        if self.audio_manager:
            self.audio_manager.shutdown()

# Instância global do gerenciador de áudio
audio_manager = ModernAudioManager()

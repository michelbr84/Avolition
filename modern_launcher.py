"""
Launcher Moderno para Avolition
Interface gráfica moderna para configurar e iniciar o jogo
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import subprocess
import sys
import threading
from PIL import Image, ImageTk
import config_modern

class ModernLauncher:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Avolition - Launcher Moderno")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        
        # Centraliza a janela na tela
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")
        
        # Carrega configurações
        self.config = config_modern.modern_config
        
        # Variáveis de controle
        self.resolution_var = tk.StringVar(value=self.config.resolution)
        self.fullscreen_var = tk.BooleanVar(value=self.config.fullscreen)
        self.vsync_var = tk.BooleanVar(value=self.config.vsync)
        self.antialiasing_var = tk.IntVar(value=self.config.antialiasing)
        self.master_volume_var = tk.DoubleVar(value=self.config.master_volume / 100.0)
        self.music_volume_var = tk.DoubleVar(value=self.config.music_volume / 100.0)
        self.sfx_volume_var = tk.DoubleVar(value=self.config.sfx_volume / 100.0)
        self.difficulty_var = tk.StringVar(value=self.config.difficulty)
        self.particles_var = tk.BooleanVar(value=self.config.particle_effects)
        self.bloom_var = tk.BooleanVar(value=self.config.bloom_effect)
        self.reverb_var = tk.BooleanVar(value=True)
        self.echo_var = tk.BooleanVar(value=False)
        self.voice_volume_var = tk.DoubleVar(value=self.config.voice_volume / 100.0)
        self.autosave_var = tk.BooleanVar(value=self.config.auto_save)
        self.fps_var = tk.BooleanVar(value=self.config.show_fps)
        self.minimap_var = tk.BooleanVar(value=self.config.show_minimap)
        self.damage_var = tk.BooleanVar(value=self.config.show_damage_numbers)
        self.debug_var = tk.BooleanVar(value=self.config.debug_mode)
        self.console_var = tk.BooleanVar(value=self.config.developer_console)
        self.shaders_var = tk.BooleanVar(value=self.config.custom_shaders)
        self.safe_mode_var = tk.BooleanVar(value=False)
        
        self.setup_ui()
        self.load_background_image()
    
    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        title_label = ttk.Label(main_frame, text="AVOLITION", 
                               font=("Arial", 24, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Notebook para abas
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))
        
        # Aba de Vídeo
        video_frame = ttk.Frame(notebook)
        notebook.add(video_frame, text="Vídeo")
        self.setup_video_tab(video_frame)
        
        # Aba de Áudio
        audio_frame = ttk.Frame(notebook)
        notebook.add(audio_frame, text="Áudio")
        self.setup_audio_tab(audio_frame)
        
        # Aba de Gameplay
        gameplay_frame = ttk.Frame(notebook)
        notebook.add(gameplay_frame, text="Gameplay")
        self.setup_gameplay_tab(gameplay_frame)
        
        # Aba Avançado
        advanced_frame = ttk.Frame(notebook)
        notebook.add(advanced_frame, text="Avançado")
        self.setup_advanced_tab(advanced_frame)
        
        # Botões de ação
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        
        # Botão Jogar
        play_button = ttk.Button(button_frame, text="JOGAR", 
                                command=self.launch_game, style="Accent.TButton")
        play_button.grid(row=0, column=0, padx=(0, 10))
        
        # Botão Salvar Configurações
        save_button = ttk.Button(button_frame, text="Salvar Configurações", 
                                command=self.save_config)
        save_button.grid(row=0, column=1, padx=(0, 10))
        
        # Botão Restaurar Padrões
        reset_button = ttk.Button(button_frame, text="Restaurar Padrões", 
                                 command=self.reset_config)
        reset_button.grid(row=0, column=2, padx=(0, 10))
        
        # Botão Sair
        exit_button = ttk.Button(button_frame, text="Sair", 
                                command=self.root.quit)
        exit_button.grid(row=0, column=3)
        
        # Configura grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
    
    def setup_video_tab(self, parent):
        """Configura a aba de vídeo"""
        # Resolução
        ttk.Label(parent, text="Resolução:").grid(row=0, column=0, sticky=tk.W, pady=5)
        resolution_combo = ttk.Combobox(parent, textvariable=self.resolution_var, 
                                       values=["1920x1080", "1600x900", "1366x768", "1280x720", "1024x768"])
        resolution_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Fullscreen
        fullscreen_check = ttk.Checkbutton(parent, text="Tela Cheia", 
                                          variable=self.fullscreen_var)
        fullscreen_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # V-Sync
        vsync_check = ttk.Checkbutton(parent, text="V-Sync", 
                                     variable=self.vsync_var)
        vsync_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Anti-aliasing
        ttk.Label(parent, text="Anti-aliasing:").grid(row=3, column=0, sticky=tk.W, pady=5)
        aa_scale = ttk.Scale(parent, from_=0, to=8, variable=self.antialiasing_var, 
                            orient=tk.HORIZONTAL)
        aa_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Qualidade de sombras
        ttk.Label(parent, text="Qualidade de Sombras:").grid(row=4, column=0, sticky=tk.W, pady=5)
        shadow_combo = ttk.Combobox(parent, values=["Baixa", "Média", "Alta", "Ultra"])
        shadow_combo.set("Alta")
        shadow_combo.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Efeitos de partículas
        particles_check = ttk.Checkbutton(parent, text="Efeitos de Partículas",
                                         variable=self.particles_var)
        particles_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Bloom
        bloom_check = ttk.Checkbutton(parent, text="Efeito Bloom",
                                     variable=self.bloom_var)
        bloom_check.grid(row=6, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configura grid
        parent.columnconfigure(1, weight=1)
    
    def setup_audio_tab(self, parent):
        """Configura a aba de áudio"""
        # Volume Master
        ttk.Label(parent, text="Volume Master:").grid(row=0, column=0, sticky=tk.W, pady=5)
        master_scale = ttk.Scale(parent, from_=0, to=1, variable=self.master_volume_var, 
                                orient=tk.HORIZONTAL)
        master_scale.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Volume Música
        ttk.Label(parent, text="Volume Música:").grid(row=1, column=0, sticky=tk.W, pady=5)
        music_scale = ttk.Scale(parent, from_=0, to=1, variable=self.music_volume_var, 
                               orient=tk.HORIZONTAL)
        music_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Volume Efeitos
        ttk.Label(parent, text="Volume Efeitos:").grid(row=2, column=0, sticky=tk.W, pady=5)
        sfx_scale = ttk.Scale(parent, from_=0, to=1, variable=self.sfx_volume_var, 
                             orient=tk.HORIZONTAL)
        sfx_scale.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Volume Voz
        ttk.Label(parent, text="Volume Voz:").grid(row=3, column=0, sticky=tk.W, pady=5)
        voice_scale = ttk.Scale(parent, from_=0, to=1, variable=self.voice_volume_var,
                               orient=tk.HORIZONTAL)
        voice_scale.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))

        # Efeitos de áudio
        reverb_check = ttk.Checkbutton(parent, text="Reverb",
                                      variable=self.reverb_var)
        reverb_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)

        echo_check = ttk.Checkbutton(parent, text="Echo",
                                    variable=self.echo_var)
        echo_check.grid(row=5, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configura grid
        parent.columnconfigure(1, weight=1)
    
    def setup_gameplay_tab(self, parent):
        """Configura a aba de gameplay"""
        # Dificuldade
        ttk.Label(parent, text="Dificuldade:").grid(row=0, column=0, sticky=tk.W, pady=5)
        difficulty_combo = ttk.Combobox(parent, textvariable=self.difficulty_var, 
                                       values=["Fácil", "Normal", "Difícil", "Pesadelo"])
        difficulty_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        
        # Auto-save
        autosave_check = ttk.Checkbutton(parent, text="Auto-save",
                                        variable=self.autosave_var)
        autosave_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Mostrar FPS
        fps_check = ttk.Checkbutton(parent, text="Mostrar FPS",
                                   variable=self.fps_var)
        fps_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Mostrar minimapa
        minimap_check = ttk.Checkbutton(parent, text="Mostrar Minimapa",
                                       variable=self.minimap_var)
        minimap_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Mostrar números de dano
        damage_check = ttk.Checkbutton(parent, text="Mostrar Números de Dano",
                                      variable=self.damage_var)
        damage_check.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Configura grid
        parent.columnconfigure(1, weight=1)
    
    def setup_advanced_tab(self, parent):
        """Configura a aba avançada"""
        # Modo debug
        debug_check = ttk.Checkbutton(parent, text="Modo Debug",
                                     variable=self.debug_var)
        debug_check.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Console do desenvolvedor
        console_check = ttk.Checkbutton(parent, text="Console do Desenvolvedor",
                                       variable=self.console_var)
        console_check.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Shaders customizados
        shaders_check = ttk.Checkbutton(parent, text="Shaders Customizados",
                                       variable=self.shaders_var)
        shaders_check.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=5)

        # Modo seguro
        safe_check = ttk.Checkbutton(parent, text="Modo Seguro",
                                    variable=self.safe_mode_var)
        safe_check.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Informações do sistema
        info_frame = ttk.LabelFrame(parent, text="Informações do Sistema", padding="10")
        info_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=20)
        
        ttk.Label(info_frame, text=f"Python: {sys.version}").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"Panda3D: {self.get_panda3d_version()}").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(info_frame, text=f"Resolução: {self.get_screen_resolution()}").grid(row=2, column=0, sticky=tk.W)
        
        # Configura grid
        parent.columnconfigure(1, weight=1)
    
    def load_background_image(self):
        """Carrega imagem de fundo se disponível"""
        try:
            # Tenta carregar uma imagem de fundo
            image_paths = ["loading2.png", "config2.png", "mp_logo.png"]
            for path in image_paths:
                if os.path.exists(path):
                    image = Image.open(path)
                    image = image.resize((800, 600), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    
                    # Cria um label de fundo
                    bg_label = tk.Label(self.root, image=photo)
                    bg_label.image = photo  # Mantém referência
                    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    bg_label.lower()  # Coloca atrás dos outros widgets
                    break
        except Exception as e:
            print(f"Erro ao carregar imagem de fundo: {e}")
    
    def get_panda3d_version(self):
        """Obtém a versão do Panda3D"""
        try:
            import panda3d
            return panda3d.__version__
        except ImportError:
            return "Não instalado"
    
    def get_screen_resolution(self):
        """Obtém a resolução da tela"""
        return f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}"
    
    def save_config(self):
        """Salva as configurações"""
        try:
            # Atualiza configurações
            self.config.resolution = self.resolution_var.get()
            self.config.fullscreen = self.fullscreen_var.get()
            self.config.vsync = self.vsync_var.get()
            self.config.antialiasing = self.antialiasing_var.get()
            self.config.master_volume = int(self.master_volume_var.get() * 100)
            self.config.music_volume = int(self.music_volume_var.get() * 100)
            self.config.sfx_volume = int(self.sfx_volume_var.get() * 100)
            self.config.difficulty = self.difficulty_var.get()
            
            # Salva no arquivo
            self.config.save()
            
            messagebox.showinfo("Sucesso", "Configurações salvas com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar configurações: {e}")
    
    def reset_config(self):
        """Restaura configurações padrão"""
        if messagebox.askyesno("Confirmar", "Restaurar configurações padrão?"):
            self.config = config_modern.ModernConfig()
            self.load_config_to_ui()
            messagebox.showinfo("Sucesso", "Configurações restauradas!")
    
    def load_config_to_ui(self):
        """Carrega configurações para a interface"""
        self.resolution_var.set(self.config.resolution)
        self.fullscreen_var.set(self.config.fullscreen)
        self.vsync_var.set(self.config.vsync)
        self.antialiasing_var.set(self.config.antialiasing)
        self.master_volume_var.set(self.config.master_volume / 100.0)
        self.music_volume_var.set(self.config.music_volume / 100.0)
        self.sfx_volume_var.set(self.config.sfx_volume / 100.0)
        self.difficulty_var.set(self.config.difficulty)
    
    def launch_game(self):
        """Inicia o jogo"""
        try:
            # Salva configurações antes de iniciar
            self.save_config()
            
            # Mostra mensagem de carregamento
            loading_window = tk.Toplevel(self.root)
            loading_window.title("Carregando...")
            loading_window.geometry("300x100")
            loading_window.transient(self.root)
            loading_window.grab_set()
            
            ttk.Label(loading_window, text="Iniciando Avolition...", 
                     font=("Arial", 12)).pack(pady=20)
            
            progress = ttk.Progressbar(loading_window, mode='indeterminate')
            progress.pack(pady=10)
            progress.start()
            
            def run_game():
                try:
                    # Inicia o jogo em um processo separado
                    subprocess.run([sys.executable, "main.py"],
                                 cwd=os.path.dirname(os.path.abspath(__file__)),
                                 check=True)
                except subprocess.CalledProcessError as e:
                    self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro ao iniciar o jogo: {e}"))
                finally:
                    self.root.after(0, loading_window.destroy)
            
            # Executa o jogo em uma thread separada
            game_thread = threading.Thread(target=run_game)
            game_thread.daemon = True
            game_thread.start()
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar o jogo: {e}")
    
    def run(self):
        """Executa o launcher"""
        self.root.mainloop()

def main():
    """Função principal"""
    launcher = ModernLauncher()
    launcher.run()

if __name__ == "__main__":
    main()

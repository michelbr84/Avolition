#!/usr/bin/env python3
"""
Script de Inicializacao do Avolition
Configura o ambiente e inicia o jogo com as configuracoes corretas
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def find_venv_python():
    """Encontra o Python do ambiente virtual, se disponivel"""
    script_dir = Path(__file__).resolve().parent
    venv_dir = script_dir / "avolition_env"

    # Windows
    venv_python = venv_dir / "Scripts" / "python.exe"
    if venv_python.exists():
        return str(venv_python)

    # Linux/Mac
    venv_python = venv_dir / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)

    return None


def get_python_executable():
    """Retorna o melhor executavel Python disponivel"""
    # Se ja estamos no venv, usar sys.executable
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        return sys.executable

    # Tentar encontrar o venv
    venv_python = find_venv_python()
    if venv_python:
        return venv_python

    # Fallback para o Python atual
    return sys.executable


def setup_environment(python_exe):
    """Configura o ambiente antes de iniciar o jogo"""
    print("Configurando ambiente do Avolition...")

    # Verifica dependencias usando o Python correto
    check_script = (
        "import sys; "
        "missing = []; "
        "try:\n import panda3d; print('Panda3D', panda3d.__version__, 'encontrado')\n"
        "except ImportError: missing.append('panda3d')\n"
        "try:\n import PIL; print('Pillow', PIL.__version__, 'encontrado')\n"
        "except ImportError: missing.append('pillow')\n"
        "try:\n import numpy; print('NumPy', numpy.__version__, 'encontrado')\n"
        "except ImportError: missing.append('numpy')\n"
        "try:\n import pygame; print('Pygame', pygame.version.ver, 'encontrado')\n"
        "except ImportError: missing.append('pygame')\n"
        "if missing: print('MISSING:' + ','.join(missing)); sys.exit(1)\n"
        "else: print('Todas as dependencias OK')"
    )

    result = subprocess.run(
        [python_exe, "-c", check_script],
        capture_output=True, text=True
    )

    if result.stdout:
        for line in result.stdout.strip().split('\n'):
            print(f"  {line}")

    if result.returncode != 0:
        if result.stderr:
            print(f"  Erro: {result.stderr.strip()}")
        print("\nDependencias faltando. Instalando...")
        # Extrair pacotes faltando
        for line in result.stdout.split('\n'):
            if line.startswith('MISSING:'):
                packages = line.replace('MISSING:', '').split(',')
                for pkg in packages:
                    pkg = pkg.strip()
                    if pkg:
                        print(f"  Instalando {pkg}...")
                        install_result = subprocess.run(
                            [python_exe, "-m", "pip", "install", pkg],
                            capture_output=True, text=True
                        )
                        if install_result.returncode != 0:
                            print(f"  FALHA ao instalar {pkg}: {install_result.stderr.strip()}")
                            return
        print("  Dependencias instaladas.")


def load_config():
    """Carrega configuracoes do jogo"""
    script_dir = Path(__file__).resolve().parent
    config_file = script_dir / "modern_config.json"
    if config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print("Configuracoes carregadas")
            return config
        except Exception as e:
            print(f"Erro ao carregar configuracoes: {e}")

    # Configuracoes padrao
    default_config = {
        "resolution": "1280x720",
        "fullscreen": False,
        "vsync": True,
        "antialiasing": 2,
        "master_volume": 100,
        "music_volume": 80,
        "sfx_volume": 100,
        "difficulty": "Normal"
    }
    print("Usando configuracoes padrao")
    return default_config


def setup_panda3d_config(config):
    """Configura o Panda3D com as configuracoes"""
    config_lines = [
        "# Configuracao automatica do Avolition",
        f"win-size {config['resolution'].replace('x', ' ')}",
        f"fullscreen {'1' if config['fullscreen'] else '0'}",
        f"vsync {'1' if config['vsync'] else '0'}",
        f"multisamples {config['antialiasing']}",
        f"music-volume {config['music_volume']}",
        f"sound-volume {config['sfx_volume']}",
        "show-frame-rate-meter 1",
        "win-origin 0 0",
        "undecorated 0",
        "cursor-hidden 0"
    ]

    with open("autoconfig.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(config_lines))


def start_game():
    """Inicia o jogo"""
    print("Iniciando Avolition...\n")

    try:
        # Encontra o Python correto
        python_exe = get_python_executable()
        venv_python = find_venv_python()
        print(f"Python: {python_exe}")

        if venv_python and python_exe == venv_python:
            print("Ambiente virtual: ativo (avolition_env)")
        elif venv_python:
            print("Ambiente virtual: encontrado mas nao ativo")
        else:
            print("Ambiente virtual: nao encontrado")
        print()

        # Configura o ambiente
        setup_environment(python_exe)

        # Carrega configuracoes
        config = load_config()

        # Configura Panda3D
        setup_panda3d_config(config)

        # Inicia o jogo
        print("\nCarregando jogo...")
        result = subprocess.run(
            [python_exe, "main.py"],
            cwd=os.path.dirname(os.path.abspath(__file__))
        )

        if result.returncode != 0:
            print(f"Jogo encerrado com codigo: {result.returncode}")
        else:
            print("Jogo encerrado normalmente")

    except KeyboardInterrupt:
        print("\nJogo interrompido pelo usuario")
    except Exception as e:
        print(f"Erro ao iniciar o jogo: {e}")
        print("\nDicas de solucao:")
        print("  1. Crie o ambiente virtual: python -m venv avolition_env")
        print("  2. Ative: avolition_env\\Scripts\\activate")
        print("  3. Instale dependencias: pip install -r requirements.txt")
        print("  4. Execute novamente: python start_game.py")
    except Exception:
        pass


def show_menu():
    """Mostra menu de opcoes"""
    print("\n" + "=" * 50)
    print("  AVOLITION - LAUNCHER")
    print("=" * 50)
    print("1. Iniciar Jogo")
    print("2. Launcher Moderno")
    print("3. Verificar Dependencias")
    print("4. Sair")
    print("=" * 50)

    while True:
        try:
            choice = input("Escolha uma opcao (1-4): ").strip()

            if choice == "1":
                start_game()
                break
            elif choice == "2":
                python_exe = get_python_executable()
                print("Iniciando launcher moderno...")
                subprocess.run([python_exe, "modern_launcher.py"])
                break
            elif choice == "3":
                python_exe = get_python_executable()
                setup_environment(python_exe)
                input("\nPressione Enter para continuar...")
                continue
            elif choice == "4":
                print("Ate logo!")
                break
            else:
                print("Opcao invalida. Tente novamente.")
        except KeyboardInterrupt:
            print("\nAte logo!")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--direct":
            start_game()
        elif sys.argv[1] == "--launcher":
            python_exe = get_python_executable()
            subprocess.run([python_exe, "modern_launcher.py"])
        else:
            print("Uso: python start_game.py [--direct|--launcher]")
    else:
        show_menu()

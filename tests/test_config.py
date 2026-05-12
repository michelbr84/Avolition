"""Tests for the unified config system."""
import sys
import os
import json
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import GameConfig


def test_default_config():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        config_path = f.name
    try:
        os.unlink(config_path)  # Ensure it doesn't exist
        config = GameConfig(config_path)
        assert config.get('resolution') == '1920 1080'
        assert config.get('fullscreen') == False
        assert config.get('bloom') == True
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_save_and_load():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        config_path = f.name
    try:
        os.unlink(config_path)
        config = GameConfig(config_path)
        config.set('resolution', '800 600')
        config.save()

        config2 = GameConfig(config_path)
        assert config2.get('resolution') == '800 600'
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_to_panda3d():
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
        config_path = f.name
    try:
        os.unlink(config_path)
        config = GameConfig(config_path)
        prc = config.to_panda3d()
        assert 'win-size 1920 1080' in prc
        assert 'fullscreen 0' in prc
        assert 'bloom 1' in prc
    finally:
        if os.path.exists(config_path):
            os.unlink(config_path)


if __name__ == '__main__':
    test_default_config()
    test_save_and_load()
    test_to_panda3d()
    print("All config tests passed!")

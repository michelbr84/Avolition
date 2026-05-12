"""Tests for game data integrity."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.world import data


def test_items_exist():
    assert 'potion' in data.items
    assert 'key' in data.items
    assert 'exit' in data.items


def test_item_structure():
    for name, item in data.items.items():
        assert 'model' in item, f"Item {name} missing 'model'"
        assert 'scale' in item, f"Item {name} missing 'scale'"
        assert 'gui' in item, f"Item {name} missing 'gui'"
        assert 'command' in item, f"Item {name} missing 'command'"


def test_levels_exist():
    assert len(data.levels) > 0


def test_level_structure():
    required_keys = ['map_name', 'map_monsters', 'num_monsters', 'kills_for_key', 'enter', 'exit']
    for i, level in enumerate(data.levels):
        for key in required_keys:
            assert key in level, f"Level {i} missing '{key}'"


def test_monsters_exist():
    assert len(data.monsters) > 0


def test_monster_structure():
    required_keys = ['model', 'root_bone', 'anim', 'speed', 'scale', 'hp', 'armor', 'dmg']
    for i, monster in enumerate(data.monsters):
        for key in required_keys:
            assert key in monster, f"Monster {i} missing '{key}'"


if __name__ == '__main__':
    test_items_exist()
    test_item_structure()
    test_levels_exist()
    test_level_structure()
    test_monsters_exist()
    test_monster_structure()
    print("All data tests passed!")

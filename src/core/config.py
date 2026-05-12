"""Unified configuration system for Avolition."""
import json
from pathlib import Path
from panda3d.core import loadPrcFileData, ConfigVariableInt, ConfigVariableBool, ConfigVariableString


class GameConfig:
    """Unified configuration - replaces autoconfig.txt + modern_config.json."""

    DEFAULTS = {
        'resolution': '1920 1080',
        'fullscreen': False,
        'bloom': True,
        'multisamples': 2,
        'safemode': False,
        'music_volume': 30,
        'sound_volume': 100,
        'loverslab': 0,
        'keys': {
            'key_forward': 'w|arrow_up',
            'key_back': 's|arrow_down',
            'key_left': 'a|arrow_left',
            'key_right': 'd|arrow_right',
            'key_cam_left': 'q|delete',
            'key_cam_right': 'e|page_down',
            'key_action1': 'mouse1|enter',
            'key_action2': 'mouse3|space',
            'key_zoomin': 'wheel_up|r',
            'key_zoomout': 'wheel_down|f',
        }
    }

    def __init__(self, config_path='config/game_config.json'):
        self.config_path = Path(config_path)
        self.data = dict(self.DEFAULTS)
        self.load()

    def load(self):
        # Try loading JSON config
        if self.config_path.exists():
            with open(self.config_path) as f:
                saved = json.load(f)
                self.data.update(saved)
        # Fallback: try legacy autoconfig.txt (only for default path)
        elif str(self.config_path) == 'config/game_config.json' and Path('autoconfig.txt').exists():
            self._load_legacy_autoconfig()

    def _load_legacy_autoconfig(self):
        with open('autoconfig.txt') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                parts = line.split(None, 1)
                if len(parts) == 2:
                    key, value = parts
                    if key == 'win-size':
                        self.data['resolution'] = value
                    elif key == 'fullscreen':
                        self.data['fullscreen'] = value == '1'
                    elif key == 'bloom':
                        self.data['bloom'] = value == '1'
                    elif key == 'multisamples':
                        self.data['multisamples'] = int(value)
                    elif key == 'safemode':
                        self.data['safemode'] = value == '1'
                    elif key == 'music-volume':
                        self.data['music_volume'] = int(value)
                    elif key == 'sound-volume':
                        self.data['sound_volume'] = int(value)
                    elif key.startswith('key_'):
                        if 'keys' not in self.data:
                            self.data['keys'] = {}
                        self.data['keys'][key] = value

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.data, f, indent=2)

    def to_panda3d(self):
        """Export as Panda3D config string."""
        lines = []
        lines.append('win-size ' + self.data['resolution'])
        lines.append('fullscreen ' + ('1' if self.data['fullscreen'] else '0'))
        lines.append('bloom ' + ('1' if self.data['bloom'] else '0'))
        lines.append('multisamples ' + str(self.data['multisamples']))
        lines.append('safemode ' + ('1' if self.data['safemode'] else '0'))
        lines.append('music-volume ' + str(self.data['music_volume']))
        lines.append('sound-volume ' + str(self.data['sound_volume']))
        for key, value in self.data.get('keys', {}).items():
            lines.append(key + ' ' + value)
        return '\n'.join(lines)

    def apply(self):
        """Apply config via loadPrcFileData."""
        for line in self.to_panda3d().split('\n'):
            loadPrcFileData('', line)

    def get(self, key, default=None):
        return self.data.get(key, default)

    def set(self, key, value):
        self.data[key] = value

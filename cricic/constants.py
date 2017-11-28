from pathlib import Path

CRICIC_ROOT = Path(__file__).parents[1].resolve()
CONF_ROOT = CRICIC_ROOT / 'config'
CONF_LOCATIONS = (
    CONF_ROOT,
    Path('/etc/cricic'),
    Path('/usr/share/cricic'),
    Path('~/.config/cricic').expanduser()
    )

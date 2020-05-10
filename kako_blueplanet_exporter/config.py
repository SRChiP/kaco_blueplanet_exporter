import configparser
from pathlib import Path

config = configparser.ConfigParser()
path = Path(__file__).parent / "config.ini"
if not path.exists():
    raise EnvironmentError("Config file is missing")
config.read(path)


def get_config(val: str) -> str:
    return config["DEFAULT"][val]

import os
import tomllib


def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    cfg_file = os.path.join(parent_dir, "pyproject.toml")

    if not os.path.exists(cfg_file):
        return {}

    with open(cfg_file, "rb") as f:
        cfg = tomllib.load(f)

    common = cfg.get("tool", {}).get("pyfactoring", {})
    return {
        "common": common,
        "pydioms": common.get("pydioms", {}),
        "pyclones": common.get("pyclones", {})
    }


config = load_config()

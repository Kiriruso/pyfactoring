__all__ = ["common_settings", "pydioms_settings", "pyclones_settings"]

import os
import tomllib
from typing import Annotated, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class CommonSettings(BaseSettings):
    color: Annotated[bool, Field(default=True)]
    diff: Annotated[bool, Field(default=True)]
    typed: Annotated[bool, Field(default=False)]

    model_config = SettingsConfigDict(extra="ignore")


class PydiomsSettings(CommonSettings):
    count: Annotated[int, Field(ge=0, default=5)]
    length: Annotated[int, Field(gt=0, default=10)]
    debug: Annotated[bool, Field(default=False)]


class PyclonesSettings(CommonSettings):
    count: Annotated[int, Field(ge=0, default=1)]
    length: Annotated[int, Field(gt=0, default=5)]
    template_mode: Literal["tree", "code"] | None = None


def load_config():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    cfg_file = os.path.join(parent_dir, "pyproject.toml")

    if not os.path.exists(cfg_file):
        return {}

    with open(cfg_file, "rb") as f:
        cfg = tomllib.load(f)

    pyfactoring = cfg.get("tool", {}).get("pyfactoring", {})
    return {
        "common": pyfactoring,
        "pydioms": pyfactoring.get("pydioms", {}),
        "pyclones": pyfactoring.get("pyclones", {})
    }


_config = load_config()

common_settings = CommonSettings(**_config.get("common"))
pydioms_settings = PydiomsSettings(**_config.get("pydioms"))
pyclones_settings = PyclonesSettings(**_config.get("pyclones"))

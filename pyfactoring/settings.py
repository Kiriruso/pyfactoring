__all__ = ["common_settings", "pydioms_settings", "pyclones_settings"]

import os
import tomllib
from typing import Annotated, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from pyfactoring.arguments import args
from pyfactoring.exceptions import OptionsConflictError


class CommonSettings(BaseSettings):
    action: Annotated[Literal["check", "format"], Field(default="check")]
    paths: Annotated[list[str], Field(default=["."])]

    diff: Annotated[bool, Field(default=False)]
    workers: Annotated[int, Field(default=1)]
    exclude: Annotated[list[str], Field(default_factory=list)]
    chain: Annotated[list[str], Field(default=list)]

    model_config = SettingsConfigDict(extra="ignore")


class PydiomsSettings(BaseSettings):
    count: Annotated[int, Field(ge=0, default=5)]
    length: Annotated[int, Field(gt=0, default=10)]
    verbose: Annotated[bool, Field(default=False)]

    model_config = SettingsConfigDict(extra="ignore")


class PyclonesSettings(BaseSettings):
    count: Annotated[int, Field(ge=0, default=2)]
    length: Annotated[int, Field(gt=0, default=5)]
    template_mode: Literal["tree", "code"] | None = None
    template_view: bool = False

    model_config = SettingsConfigDict(extra="ignore")


def _load_config():
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


def _assign_arguments(config: dict):
    if args.action:
        config["common"]["action"] = args.action
        config["common"]["paths"] = args.paths.split() if isinstance(args.paths, str) else args.paths

        if args.chain_all and args.chain:
            raise OptionsConflictError(
                f"The passed options are incompatible: '--chain-all' and '--chain'"
            )

        if args.chain_all:
            config["common"]["chain"] = config["common"]["paths"]
        elif args.chain:
            config["common"]["chain"] = args.chain

        if args.exclude:
            config["common"]["exclude"] = args.exclude

    if args.color:
        config["common"]["color"] = True

    if args.diff:
        config["common"]["diff"] = True

    if args.workers:
        config["common"]["workers"] = args.workers

    if args.pd_verbose:
        config["pydioms"]["verbose"] = args.pd_verbose

    if args.pd_count:
        config["pydioms"]["count"] = args.pd_count

    if args.pd_length:
        config["pydioms"]["length"] = args.pd_length

    if args.template_mode:
        config["pyclones"]["template_mode"] = args.template_mode

    if args.template_view:
        config["pyclones"]["template_view"] = args.template_view

    if args.pc_count:
        config["pyclones"]["count"] = args.pc_count

    if args.pc_length:
        config["pyclones"]["length"] = args.pc_length


_config = _load_config()
_assign_arguments(_config)

common_settings: CommonSettings = CommonSettings(**_config.get("common"))
pydioms_settings: PydiomsSettings = PydiomsSettings(**_config.get("pydioms"))
pyclones_settings: PyclonesSettings = PyclonesSettings(**_config.get("pyclones"))

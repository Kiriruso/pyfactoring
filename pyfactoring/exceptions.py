from dataclasses import dataclass


@dataclass(frozen=True)
class PyfactoringException(Exception):
    text: str


@dataclass(frozen=True)
class FileOrDirNotFoundError(PyfactoringException):
    """Invalid path to project file or directory"""


@dataclass(frozen=True)
class UndefinedModeError(PyfactoringException):
    """Invalid template extraction mode

    The mode is set in the file `pyproject.toml`: `template_mode = "code" or "tree"`
    """


@dataclass(frozen=True)
class OptionsConflictError(PyfactoringException):
    """The command line parameters passed are incompatible with each other"""

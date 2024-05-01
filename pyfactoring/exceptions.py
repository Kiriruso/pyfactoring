from dataclasses import dataclass


@dataclass(frozen=True)
class PyfactoringException(Exception):
    text: str


@dataclass(frozen=True)
class FileOrDirNotFoundError(PyfactoringException):
    """Недействительный путь к файлу или директории проекта"""

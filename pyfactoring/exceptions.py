from dataclasses import dataclass


@dataclass(frozen=True)
class PyfactoringException(Exception):
    text: str


@dataclass(frozen=True)
class FileOrDirNotFoundError(PyfactoringException):
    """Недействительный путь к файлу или директории проекта"""


@dataclass(frozen=True)
class UndefinedModeError(PyfactoringException):
    """Недействительный режим извлечения шаблона

    Режим устанавливается:

    - в файле `pyproject.toml`
    - в методе `get_template(mode=<mode>)`
    """
